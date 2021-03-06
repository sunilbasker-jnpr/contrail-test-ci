import os
import copy
from tcutils.util import get_random_name
from api_drivers.heat import parser
from vn_fixture import VNFixture_v2
from subnet_fixture import SubnetFixture
from policy_fixture import PolicyFixture_v2
from alarm_fixture import AlarmFixture_v2
from vm_fixture import VMFixture_v2
from ipam_fixture import IPAMFixture_v2
from vdns_fixture_new import VdnsFixture_v2, VdnsRecordFixture_v2
from qos_fixture_new import QosQueueFixture_v2, QosForwardingClassFixture_v2, QosConfigFixture_v2

# Map: heat resource type -> fixture
_HEAT_2_FIXTURE = {
    'OS::ContrailV2::VirtualNetwork': VNFixture_v2,
    'OS::ContrailV2::NetworkPolicy': PolicyFixture_v2,
    'OS::ContrailV2::NetworkIpam': IPAMFixture_v2,
    'OS::ContrailV2::VirtualDns': VdnsFixture_v2,
    'OS::ContrailV2::VirtualDnsRecord': VdnsRecordFixture_v2,
    'OS::ContrailV2::Alarm': AlarmFixture_v2,
    'OS::Neutron::Subnet': SubnetFixture,
    'OS::Neutron::Net': VNFixture_v2,
    'OS::Neutron::Policy': PolicyFixture_v2,
    'OS::Nova::Server': VMFixture_v2,  
    'OS::ContrailV2::QosQueue': QosQueueFixture_v2,
    'OS::ContrailV2::ForwardingClass': QosForwardingClassFixture_v2,
    'OS::ContrailV2::QosConfig': QosConfigFixture_v2,
}

def verify_on_setup (objs):
    for res in objs['fixtures']:
        objs['fixtures'][res].verify_on_setup()

def verify_on_cleanup (objs):
    for res in objs['fixtures']:
        objs['fixtures'][res].verify_on_cleanup()

def _add_to_objs (objs, res_name, obj, args=None):
    objs['fixtures'][res_name] = obj
    objs['id-map'][obj.uuid] = obj
    objs['name-map'][obj.name] = obj
    if args:
        objs['args'][res_name] = args
    if obj.fq_name_str:
        objs['fqn-map'][obj.fq_name_str] = obj

def _get_resources_and_uuids (stack, tmpl):
    ret = {}
    for out in stack.outputs:
        key = out['output_key']
        res_id = out['output_value']
        try:
            res_name = tmpl['outputs'][key]['value']['get_attr'][0]
        except KeyError:
            res_name = tmpl['outputs'][key]['value']['get_resource']
        ret[res_name] = res_id
    return ret

def _create_via_heat (test, tmpl, params):

    ''' Create resources via heat and for each resource create appropriate
        fixture
        - for each resource in "resources" section an appropriate
        entry must be present in the "outputs" section of the template
        - code *CANNOT* handle cyclic dependency
        - to account for cyclic reference,
            i) build dependency table,
            ii) check & remove forward references
                forward references are those where resource holds reference to
                another resource that is to be created later
            iii) create resource and then update the reference
    '''

    parser.check_cyclic_dependency(tmpl)
    test.logger.debug("Creating resources via Heat")
    wrap = test.connections.get_orch_ctrl().get_api('heat')
    assert wrap, "Unable to obtain Heat api-wrap"

    tmpl_first = copy.deepcopy(tmpl)
    lvls, tbl = parser.build_dependency_tables(tmpl_first)
    refs = parser.report_fwd_refs(tbl, tmpl_first)
    tmpl_first, tmpl_to_update = parser.remove_fwd_refs(tmpl_first, refs)
    st = wrap.stack_create(get_random_name(), tmpl_first, params)
    objs = {'heat_wrap': wrap, 'stack': st,
            'fixture_cleanup': test.connections.inputs.fixture_cleanup,
            'fixtures': {}, 'id-map': {}, 'fqn-map': {}, 'args': {},
            'name-map': {}}
    test.addCleanup(_delete_via_heat, objs)
    uuids = _get_resources_and_uuids(st, tmpl_first)
    for i in range(len(lvls)):
        for res_name in lvls[i]:
            res_tmpl = tmpl_first['resources'][res_name]
            res_type = _HEAT_2_FIXTURE[res_tmpl['type']]
            test.logger.debug('Reading %s - %s' % (res_name,
                                res_tmpl['properties'].get('name', None)))
            args = parser.parse_resource(res_tmpl, params, objs)
            obj = test.useFixture(res_type(test.connections,
                                           uuid=uuids[res_name],
                                           fixs=objs, params=args))
            _add_to_objs(objs, res_name, obj)
    if tmpl_to_update:
        parser.fix_fwd_refs(objs, tmpl_to_update, refs)
        wrap.stack_update(st, tmpl_to_update, params, {})
        for res_name in refs:
            test.logger.debug('Updating %s' % res_name)
            args = parser.parse_resource(
                        tmpl_to_update['resources'][res_name], params, objs)
            objs['fixtures'][res_name].update_args(args)
            objs['fixtures'][res_name].update()
    return objs

def _delete_via_heat (objs):
    if objs['fixture_cleanup'] == 'no':
        return
    wrap = objs['heat_wrap']
    wrap.stack_delete(objs['stack'])
    if int(os.getenv('VERIFY_ON_CLEANUP', 1)):
        verify_on_cleanup(objs)

def _update_via_heat (test, objs, tmpl, params):

    ''' Update heat stack and refresh each resource's fixture
        procedure should be same as 'create' method
    '''

    parser.check_cyclic_dependency(tmpl)
    test.logger.debug("Updating resources via Heat")
    wrap = objs['heat_wrap']
    st = objs['stack']
    tmpl_first = copy.deepcopy(tmpl)
    lvls, tbl = parser.build_dependency_tables(tmpl_first)
    refs = parser.report_fwd_refs(tbl, tmpl_first)
    tmpl_first, tmpl_to_update = parser.remove_fwd_refs(tmpl_first, refs)
    st = wrap.stack_update(st, tmpl_first, params, {})
    uuids = _get_resources_and_uuids(st, tmpl_first)
    for i in range(len(lvls)):
        for res_name in lvls[i]:
            res_tmpl = tmpl_first['resources'][res_name]
            res_type = _HEAT_2_FIXTURE[res_tmpl['type']]
            args = parser.parse_resource(res_tmpl, params, objs)
            if objs['fixtures'].get(res_name, None):
                test.logger.debug('Updating %s' % res_name)
                objs['fixtures'][res_name].update_args(args)
                objs['fixtures'][res_name].update()
        else:
            test.logger.debug('Reading %s - %s' % (res_name,
                tmpl_first['resources'][res_name]['properties'].get('name',
                                                                    None)))
            obj = test.useFixture(res_type(test.connections,
                                           uuid=uuids[res_name],
                                           fixs=objs, params=args))
            _add_to_objs(objs, res_name, obj)
    if tmpl_to_update:
        parser.fix_fwd_refs(objs, tmpl_to_update, refs)
        wrap.stack_update(st, tmpl_to_update, params, {})
        for res_name in refs:
            test.logger.debug('Updating %s' % res_name)
            args = parser.parse_resource(
                        tmpl_to_update['resources'][res_name], params, objs)
            objs['fixtures'][res_name].update_args(args)
            objs['fixtures'][res_name].update()
    return objs

def _create_via_fixture (test, tmpl, params):

    ''' Create resource via fixture
        - Heat template *MUST* explicilty call out dependency with the
          directive "depends_on"
        - Build a dependency table, which specifies the order in which the
          fixtures/resource must be initiated
        - Remove any forward references
        - Parse the heat template and derive arguments
        - Create resources using fixtures, in order given by dependency table
        - Update references with fixtures' update method
    '''
    
    parser.check_cyclic_dependency(tmpl)
    test.logger.debug("Creating resources via fixtures")
    objs = {'fixtures': {}, 'args': {}, 'id-map': {}, 'fqn-map': {}, 'name-map': {}}
    tmpl_first = copy.deepcopy(tmpl)
    dep_tbl, res_tbl = parser.build_dependency_tables(tmpl)
    lvls = dep_tbl.keys()
    lvls.sort()
    refs = parser.report_fwd_refs(res_tbl, tmpl_first)
    tmpl_first, tmpl_to_update = parser.remove_fwd_refs(tmpl_first, refs)
    for i in lvls:
        for res_name in dep_tbl[i]:
            res_tmpl = tmpl_first['resources'][res_name]
            res_type = _HEAT_2_FIXTURE[res_tmpl['type']]
            args = parser.parse_resource(res_tmpl, params, objs)
            obj = test.useFixture(res_type(test.connections, params=args,
                                           fixs=objs))
            _add_to_objs(objs, res_name, obj, args)
    if tmpl_to_update:
        parser.fix_fwd_refs(objs, tmpl_to_update, refs)
        for res_name in refs:
            res_tmpl = tmpl_to_update['resources'][res_name]
            args = parser.parse_resource(res_tmpl, params, objs)
            diff_args = _get_delta(objs['args'][res_name], args)
            objs['fixtures'][res_name].update(args)
            objs['args'][res_name].update(diff_args)
    return objs

def _update_via_fixture (test, objs, tmpl, params):

    ''' Update resource via fixture
        - Add new resources if any
        - Check for Update in existing resources
        - Delete resources no longer in template
    '''

    parser.check_cyclic_dependency(tmpl)
    test.logger.debug("Updating resources via fixtures")
    check_for_update = []
    tmpl_first = copy.deepcopy(tmpl)
    dep_tbl, res_tbl = parser.build_dependency_tables(tmpl)
    lvls = dep_tbl.keys()
    lvls.sort()
    refs = parser.report_fwd_refs(res_tbl, tmpl_first)
    tmpl_first, tmpl_to_update = parser.remove_fwd_refs(tmpl_first, refs)
    for i in lvls:
        for res_name in dep_tbl[i]:
            if res_name not in objs['fixtures']:
                res_tmpl = tmpl_first['resources'][res_name]
                res_type = _HEAT_2_FIXTURE[res_tmpl['type']]
                args = parser.parse_resource(res_tmpl, params, objs)
                obj = test.useFixture(res_type(test.connections, params=args,
                                               fixs=objs))
                _add_to_objs(objs, res_name, obj, args)
            else:
                check_for_update.append(res_name)

    if tmpl_to_update:
        parser.fix_fwd_refs(objs, tmpl_to_update, refs)
    else:
        tmpl_to_update = tmpl_first

    check_for_update = list(set(check_for_update + refs.keys()))
    for res_name in check_for_update:
        res_tmpl = tmpl_to_update['resources'][res_name]
        args = parser.parse_resource(res_tmpl, params, objs)
        diff_args = _get_delta(objs['args'][res_name], args)
        if diff_args:
            args['type'] = res_tmpl['type']
            objs['fixtures'][res_name].update(args)
            objs['args'][res_name].update(diff_args)

    return objs

def create (test, tmpl, params):
    if test.testmode == 'heat':
        objs =  _create_via_heat(test, tmpl, params)
    else:
        test.connections.get_orch_ctrl().select_api = test.testmode
        objs = _create_via_fixture(test, tmpl, params)
    test.objs = objs
    return test.objs

def update (test, objs, tmpl, params):
    if test.testmode == 'heat':
        objs = _update_via_heat(test, objs, tmpl, params)
    else:
        test.connections.get_orch_ctrl().select_api = test.testmode
        objs = _update_via_fixture(test, objs, tmpl, params)
    test.objs = objs
    return test.objs

def _diff_help (old, new):
    if len(old) != len(new):
        return new
    if type(new) == type([]):
        old_cp = copy.copy(old)
        new_cp = copy.copy(new)
        old_cp.sort()
        new_cp.sort()
        items = range(len(new))
    else:
        items = new.keys()
        old_cp = old
        new_cp = new
    for i in items:
        if type(new[i]) == type({}) or type(new[i]) == type([]):
            if _diff_help(old[i], new[i]):
                return new
        elif new[i] != old[i]:
            return new
    return None

def _get_delta (old, new):
    delta = {}
    for k in old:
        if k not in new:
            if type(old[k]) == type([]):
                delta[k] = []
            else:
                delta[k] = None
    for k in new:
        if k not in old:
            delta[k] = new[k]
        else:
            if type(new[k]) == type({}):
                diff = _diff_help(old[k], new[k])
            elif type(new[k]) == type([]):
                diff = _diff_help(old[k], new[k])
            else:
                diff = new[k] if new[k] != old[k] else None
            if diff:
                delta[k] = diff
    return delta
