from vnc_api.vnc_api import QosQueue, ForwardingClass, QosConfig
try:
    from webui_test import *
except ImportError:
    pass

from contrail_fixtures import ContrailFixture
from tcutils.util import get_random_name, retry, compare_dict

class QosQueueFixture_v2(ContrailFixture):

    '''
    Fixture for creating Qos Queue object
    '''
    vnc_class = QosQueue
    
    def __init__(self, connections, uuid=None, params=None, fixs=None):
        super(QosQueueFixture_v2, self).__init__(
           uuid=uuid,
           connections=connections,
           params=params,
           fixs=fixs)
        self.agent_inspect = connections.agent_inspect

    def get_attr (self, lst):
        if lst == ['fq_name']:
            return self.fq_name
        return None

    def get_resource (self):
        return self.uuid
   
    def __str__ (self):
        #TODO: __str__
        if self._args:
            info = ''
        else:
            info = ''
        return '%s:%s' % (self.type_name, info)
    
    @retry(delay=1, tries=5)
    def _read_vnc_obj (self):
        self.logger.info('Reading existing Queue with UUID %s' % (
                                                        self.uuid))
        obj = self._vnc.get_qos_queue(self.uuid)
        if obj != None:
            return True, obj
        else:
            self.logger.warn('UUID %s not found, unable to read Queue' % (
                self.uuid))
            return False, obj

    def _read (self):
        ret, obj = self._read_vnc_obj()
        if ret:
            self._vnc_obj = obj
            self._populate_attr(self._vnc_obj)
        
    def _create (self):
        self.logger.info('Creating %s' % self)
        with self._api_ctx:
            self.uuid = self._ctrl.create_qos_queue(
                           **self._args)
            self._read()

    def _delete (self):
        self.logger.info('Deleting %s' % self)
        with self._api_ctx:
            self._ctrl.delete_qos_queue(
               obj=self._obj, uuid=self.uuid)

    def _update (self):
        self.logger.info('Updating %s' % self)
        with self._api_ctx:
            self._ctrl.update_qos_queue(
               obj=self._obj, uuid=self.uuid, **self.args)

    def verify_on_setup(self):
        self.assert_on_setup(*self.verify_qq_in_all_agents())
    # end verify_on_setup

    def verify_on_cleanup(self):
        self.assert_on_setup(*self.verify_qq_not_in_all_agents())
    # end verify_on_cleanup

    @retry(delay=2, tries=5)
    def verify_qq_in_all_agents(self):
        agent_qos_queues= {}
        for compute in self.inputs.compute_ips:
            inspect_h = self.agent_inspect[compute]
            agent_qos_queues[compute] = inspect_h.get_agent_qos_queue(
                self.uuid)
            if not agent_qos_queues[compute]:
                msg = 'Qos Queue %s not found in Compute %s' % (self.uuid, compute)
                self.logger.warn(msg)
                return False, msg
        agent_qq_reference = agent_qos_queues[self.inputs.compute_ips[0]]

        # Check that all values are same across all agents
        self.id = {}
        for compute, agent_qq in agent_qos_queues.iteritems():
            self.id[compute] = agent_qq['id']
            (result, mismatches) = compare_dict(agent_qq, agent_qq_reference)
            if not result:
                msg = 'On Compute %s, mismatch found in qos queue entries, Unmatched items: %s' % (compute, mismatches)
                self.logger.warn(msg)
                return False, msg
        msg = 'Validated Qos Queue UUID %s in agents of all computes' % (self.uuid)
        self.logger.info(msg)
        return True, msg
    # end verify_qq_in_all_agents

    @retry(delay=2, tries=5)
    def verify_qq_not_in_all_agents(self):
        for compute in self.inputs.compute_ips:
            inspect_h = self.agent_inspect[compute]
            agent_qos_queue = inspect_h.get_agent_qos_queue(self.uuid)
            if agent_qos_queue:
                msg = 'Qos Queue %s is still in Compute %s' % (self.uuid, compute)
                self.logger.warn(msg)
                return False, msg
        msg = 'Validated Qos Queue UUID %s deleted in agents of all computes' % (self.uuid)
        self.logger.info(msg)
        return True, msg
    # end verify_qq_not_in_all_agents

    def _populate_attr(self, queue_obj):
        self.obj = queue_obj
        self.queue_id = queue_obj.qos_queue_identifier
        self.uuid = queue_obj.uuid
    # end _populate_attr


class QosForwardingClassFixture_v2(ContrailFixture):

    vnc_class = ForwardingClass
    
    def __init__(self, connections, uuid=None, params=None, fixs=None):
        super(QosForwardingClassFixture_v2, self).__init__(
           uuid=uuid,
           connections=connections,
           params=params,
           fixs=fixs)
        '''
        queue_uuid : UUID of QosQueue object
        '''
        self.agent_inspect = connections.agent_inspect
        
        if self.inputs.verify_thru_gui():
            self.webui = WebuiTest(self.connections, self.inputs)
            self.kwargs = kwargs
    # end __init__

    def get_attr (self, lst):
        if lst == ['fq_name']:
            return self.fq_name
        return None

    def get_resource (self):
        return self.uuid
   
    def __str__ (self):
        #TODO: __str__
        if self._args:
            info = ''
        else:
            info = ''
        return '%s:%s' % (self.type_name, info)
    
    @retry(delay=1, tries=5)
    def _read_vnc_obj (self):
        self.logger.info('Reading existing Forwarding Class with UUID %s' % (
                                                        self.uuid))
        obj = self._vnc.get_forwarding_class(self.uuid)
        if obj != None:
            return True, obj
        else:
            self.logger.warn('UUID %s not found, unable to read Forwarding Class' % (
                self.uuid))
            return False, obj

    def _read (self):
        ret, obj = self._read_vnc_obj()
        if ret:
            self._vnc_obj = obj
            self._populate_attr(self._vnc_obj)
        
    def _create (self):
        self.logger.info('Creating %s' % self)
        with self._api_ctx:
            self.uuid = self._ctrl.create_forwarding_class(
                           **self._args)
            self._read()

    def _delete (self):
        self.logger.info('Deleting %s' % self)
        with self._api_ctx:
            self._ctrl.delete_forwarding_class(
               obj=self._obj, uuid=self.uuid)

    def _update (self):
        self.logger.info('Updating %s' % self)
        with self._api_ctx:
            self._ctrl.update_forwarding_class(
               obj=self._obj, uuid=self.uuid, **self.args)
    
    def _populate_attr(self, fc_obj):
        self.obj = fc_obj
        self.dscp = fc_obj.forwarding_class_dscp
        self.dot1p = fc_obj.forwarding_class_vlan_priority
        self.exp = fc_obj.forwarding_class_mpls_exp
        self.fc_id = fc_obj.forwarding_class_id
        self.uuid = fc_obj.uuid

    def verify_on_setup(self):
        self.assert_on_setup(*self.verify_fc_in_all_agents())
        self.assert_on_setup(*self.verify_fc_in_all_vrouters())
    # end verify_on_setup

    def verify_on_cleanup(self):
        self.assert_on_setup(*self.verify_fc_not_in_all_agents())
        self.assert_on_setup(*self.verify_fc_not_in_all_vrouters())
    # end verify_on_cleanup

    @retry(delay=2, tries=5)
    def verify_fc_in_all_agents(self):
        agent_fcs = {}
        for compute in self.inputs.compute_ips:
            inspect_h = self.agent_inspect[compute]
            agent_fcs[compute] = inspect_h.get_agent_forwarding_class(
                self.uuid)
            if not agent_fcs[compute]:
                msg = 'Qos FC %s not found in Compute %s' % (self.uuid, compute)
                self.logger.warn(msg)
                return False, msg
        agent_fc_reference = agent_fcs[self.inputs.compute_ips[0]]

        # Check that all values are same across all agents
        self.id = {}
        for compute, agent_fc in agent_fcs.iteritems():
            self.id[compute] = agent_fc['id']
            (result, mismatches) = compare_dict(agent_fc, agent_fc_reference,
                                                ignore_keys=['id'])
            if not result:
                msg = 'On Compute %s, mismatch found in qos fc entries, Unmatched items: %s' %\
                         (compute, mismatches)
                self.logger.warn(msg)
                return False, msg
        msg = 'Validated Qos FC UUID %s in agents of all computes' % (self.uuid)
        self.logger.info(msg)
        return True, msg
    # end verify_fc_in_all_agents

    @retry(delay=2, tries=5)
    def verify_fc_not_in_all_agents(self):
        for compute in self.inputs.compute_ips:
            inspect_h = self.agent_inspect[compute]
            agent_fc = inspect_h.get_agent_forwarding_class(self.uuid)
            if agent_fc:
                msg = 'Qos FC %s is still in Compute %s' % (self.uuid, compute)
                self.logger.warn(msg)
                return False, msg
        msg = 'Validated Qos FC UUID %s deleted in agents of all computes' % (self.uuid)
        self.logger.info(msg)
        return True, msg
    # end verify_fc_not_in_all_agents


    @retry(delay=2, tries=5)
    def verify_fc_in_all_vrouters(self):
        vrouter_fcs = {}
        for compute in self.inputs.compute_ips:
            inspect_h = self.agent_inspect[compute]
            vrouter_fcs[compute] = inspect_h.get_vrouter_forwarding_class(
                self.id[compute])
            if not vrouter_fcs[compute]:
                msg = 'Qos FC %s not found in Compute vrouter %s' % (self.id[compute], compute)
                self.logger.warn(msg)
                return False, msg
        vrouter_fc_reference = vrouter_fcs[self.inputs.compute_ips[0]]

        # Check that all values are same across all agents
        for compute, vrouter_fc in vrouter_fcs.iteritems():
            self.id[compute] = vrouter_fc['id']
            (result, mismatches) = compare_dict(vrouter_fc, vrouter_fc_reference,
                                                ignore_keys=['id', 'qos_queue'])
            if not result:
                msg = 'On Compute %s(vrouter), mismatch found in qos fc entries, Unmatched items: %s'\
                         % (compute, mismatches)
                self.logger.warn(msg)
                return False, msg
        msg = 'Validated Qos FC UUID %s in vrouters of all computes' % (self.uuid)
        self.logger.info(msg)
        return True, msg
    # end verify_fc_in_all_vrouters

    @retry(delay=2, tries=5)
    def verify_fc_not_in_all_vrouters(self):
        for compute in self.inputs.compute_ips:
            inspect_h = self.agent_inspect[compute]
            vrouter_fc = inspect_h.get_vrouter_forwarding_class(
                self.id[compute])
            if vrouter_fc:
                msg = 'Qos FC %s still in Compute vrouter %s' % (self.id[compute], compute)
                self.logger.warn(msg)
                return False, msg
        msg = 'Validated Qos FC UUID %s s deleted in vrouters of all computes' % (self.uuid)
        self.logger.info('msg')
        return True, msg
    # end verify_fc_not_in_all_vrouters

class QosConfigFixture_v2(ContrailFixture):

    ''' Fixture for QoSConfig
    dscp_mapping , dot1p_mapping and exp_mapping is a
    dict of code_points as key and ForwardingClass id as value

    qos_config_type: One of vhost/fabric/project, Default is project
    '''
    
    vnc_class = QosConfig
    
    def __init__(self, connections, uuid=None, params=None, fixs=None, **kwargs):
        super(QosConfigFixture_v2, self).__init__(
           uuid=uuid,
           connections=connections,
           params=params,
           fixs=fixs,
           **kwargs)
        '''
        queue_uuid : UUID of QosQueue object
        '''
        self.agent_inspect = connections.agent_inspect
        self.vmi_uuid = kwargs.get('vmi_uuid', None)
        self.vn_uuid = kwargs.get('vn_uuid', None)
        self.id = {}
        if self.inputs.verify_thru_gui():
            self.webui = WebuiTest(self.connections, self.inputs)
            self.kwargs = kwargs
    # end __init__

    def get_attr (self, lst):
        if lst == ['fq_name']:
            return self.fq_name
        return None

    def get_resource (self):
        return self.uuid
   
    def __str__ (self):
        #TODO: __str__
        if self._args:
            info = ''
        else:
            info = ''
        return '%s:%s' % (self.type_name, info)
    
    @retry(delay=1, tries=5)
    def _read_vnc_obj (self):
        self.logger.info('Reading existing Qos Config with UUID %s' % (
                                                        self.uuid))
        obj = self._vnc.get_qos_config(self.uuid)
        if obj != None:
            return True, obj
        else:
            self.logger.warn('UUID %s not found, unable to read Qo Config' % (
                self.uuid))
            return False, obj

    def _read (self):
        ret, obj = self._read_vnc_obj()
        if ret:
            self._vnc_obj = obj
            self._populate_attr(self._vnc_obj)
        
    def _create (self):
        self.logger.info('Creating %s' % self)
        with self._api_ctx:
            self.uuid = self._ctrl.create_qos_config(
                           **self._args)
            self._read()

    def _delete (self):
        self.logger.info('Deleting %s' % self)
        with self._api_ctx:
            self._ctrl.delete_qos_config(
               obj=self._obj, uuid=self.uuid)

    def _update (self):
        self.logger.info('Updating %s' % self)
        with self._api_ctx:
            self._ctrl.update_qos_config(
               obj=self._obj, uuid=self.uuid, **self.args)

    def _populate_attr(self, qos_config_obj):
        self.uuid = qos_config_obj.uuid
        self.qos_config_type = qos_config_obj.get_qos_config_type()
        self.dscp_entries = qos_config_obj.dscp_entries
        self.dot1p_entries = qos_config_obj.vlan_priority_entries
        self.mpls_exp_entries = qos_config_obj.mpls_exp_entries
        self.default_fc_id = qos_config_obj.default_forwarding_class_id

    """
    def apply_to_vmi(self, vmi_uuid):
        self.logger.info('Applying qos-config on VM %s' % (vmi_uuid))
        vmi_obj = self.vnc_api_h.virtual_machine_interface_read(id=vmi_uuid)
        vmi_obj.add_qos_config(self.qos_config_obj)
        self.vnc_api_h.virtual_machine_interface_update(vmi_obj)
    # end apply_to_vmi

    def remove_from_vmi(self, vmi_uuid):
        self.logger.info('Removing qos-config on VM %s' % (vmi_uuid))
        vmi_obj = self.vnc_api_h.virtual_machine_interface_read(id=vmi_uuid)
        vmi_obj.del_qos_config(self.qos_config_obj)
        self.vnc_api_h.virtual_machine_interface_update(vmi_obj)
    # end remove_from_vmi

    def apply_to_vn(self, vn_uuid):
        self.logger.info('Applying qos-config on VN %s' % (vn_uuid))
        vn_obj = self.vnc_api_h.virtual_network_read(id=vn_uuid)
        vn_obj.add_qos_config(self.qos_config_obj)
        self.vnc_api_h.virtual_network_update(vn_obj)
    # end apply_to_vn

    def remove_from_vn(self, vn_uuid):
        self.logger.info('Removing qos-config on VN %s' % (vn_uuid))
        vn_obj = self.vnc_api_h.virtual_network_read(id=vn_uuid)
        vn_obj.del_qos_config(self.qos_config_obj)
        self.vnc_api_h.virtual_network_update(vn_obj)
    # end remove_from_vn
    """

    def verify_on_setup(self):
        self.assert_on_setup(*self.verify_qos_config_in_all_agents())
        self.assert_on_setup(*self.verify_qos_config_in_all_vrouters())
    # end verify_on_setup

    def verify_on_cleanup(self):
        self.assert_on_setup(*self.verify_qos_config_not_in_all_agents())
        self.assert_on_setup(*self.verify_qos_config_not_in_all_vrouters())
    # end verify_on_cleanup

    @retry(delay=2, tries=5)
    def verify_qos_config_in_all_agents(self):
        agent_qcs = {}
        for compute in self.inputs.compute_ips:
            inspect_h = self.agent_inspect[compute]
            agent_qcs[compute] = inspect_h.get_agent_qos_config(self.uuid)
            if not agent_qcs[compute]:
                msg = 'Qos Config %s not found in Compute %s' % (self.uuid, compute)
                self.logger.warn(msg)
                return False, msg
        agent_qc_reference = agent_qcs[self.inputs.compute_ips[0]]

        # Check that all values are same across all agents
        for (compute, agent_qc) in agent_qcs.iteritems():
            self.id[compute] = agent_qc['id']
            (result, mismatches) = compare_dict(agent_qc, agent_qc_reference,
                                                ignore_keys=['id'])
            if not result:
                msg = 'On Compute %s, mismatch found in qos config entries, Unmatched items: %s'\
                         % (compute, mismatches)
                self.logger.warn(msg)
                return False, msg
        msg = 'Validated Qos Config UUID %s in agents of all computes'% (self.uuid)
        self.logger.info(msg)
        return True, msg
    # end verify_qos_config_in_all_agents

    @retry(delay=2, tries=5)
    def verify_qos_config_in_all_vrouters(self):
        vrouter_qcs = {}
        for compute in self.inputs.compute_ips:
            inspect_h = self.agent_inspect[compute]
            vrouter_qcs[compute] = inspect_h.get_vrouter_qos_config(
                self.id[compute])
            if not vrouter_qcs[compute]:
                msg = 'Qos config %s not found in Compute vrouter %s' % (self.id[compute], compute)
                self.logger.warn(msg)
                return False, msg
        vrouter_qc_reference = vrouter_qcs[self.inputs.compute_ips[0]]

        # Check that all values are same across all agents
        for compute, vrouter_qc in vrouter_qcs.iteritems():
            self.id[compute] = vrouter_qc['id']
            (result, mismatches) = compare_dict(vrouter_qc, vrouter_qc_reference,
                                                ignore_keys=['id'])
            if not result:
                msg = 'On Compute %s(vrouter), mismatch in qos config entries, Mismatched items: %s' \
                        % (compute, mismatches)
                self.logger.warn(msg)
                return False, msg
        msg = 'Validated Qos Config UUID %s in vrouter of all computes' % (self.uuid)
        self.logger.info(msg)
        return True, msg
    # end verify_qos_config_in_all_vrouters

    @retry(delay=2, tries=5)
    def verify_qos_config_not_in_all_agents(self):
        for compute in self.inputs.compute_ips:
            inspect_h = self.agent_inspect[compute]
            agent_qc = inspect_h.get_agent_qos_config(self.uuid)
            if agent_qc:
                msg = 'Qos Config is in %s Compute %s' % (self.uuid, compute)
                self.logger.warn(msg)
                return False, msg
        msg = 'Validated Qos Config UUID %s is deleted in agents of all computes' % (self.uuid)
        self.logger.info(msg)
        return True
    # end verify_qos_config_not_in_all_agents

    @retry(delay=2, tries=5)
    def verify_qos_config_not_in_all_vrouters(self):
        for compute in self.inputs.compute_ips:
            inspect_h = self.agent_inspect[compute]
            vrouter_qc = inspect_h.get_vrouter_qos_config(self.id[compute])
            if vrouter_qc:
                msg = 'Qos config %s is still in Compute vrouter %s' % (self.id[compute], compute)
                self.logger.warn(msg)
                return False, msg
        msg = 'Validated Qos Config UUID %s is deleted in  vrouter of all computes' % (self.uuid)
        self.logger.info(msg)
        return True, msg
    # end verify_qos_config_not_in_all_vrouters

class QosQueueFixture(QosQueueFixture_v2):

    '''
    Fixture for creating Qos Queue object
    '''
    
    def __init__ (self, connections,
                 **kwargs):
        name = kwargs.get('name', None)
        domain = 'default-global-system-config'
        project = 'default-global-qos-config'
        prj_fqn = domain + ':' + project
        self._api = kwargs.get('option', 'quantum')
        self.inputs = connections.inputs

        if name:
            uid = self._check_if_present(connections, name, [domain, project])
            if uid:
                super(VNFixture, self).__init__(connections=connections,
                                               uuid=uid)
                return
        else:
            name = get_random_name("QosQueue")
        self._construct_contrail_params(name, prj_fqn, kwargs)
        super(QosQueueFixture, self).__init__(connections=connections,
                                       params=self._params)
    
    def _check_if_present (self, conn, qos_queue_name, domain):
        uid = domain + [qos_queue_name]
        obj = conn.get_orch_ctrl().get_api('vnc').get_qos_queue(uid)
        if not obj:
            return None
        return uid

    def setUp (self):
        super(QosQueueFixture, self).setUp()

    def cleanUp (self):
        super(QosQueueFixture, self).cleanUp()

    def _construct_contrail_params (self, name, domain, kwargs):
        self._params = {
           'type': 'OS::ContrailV2::QosQueue',
           'name' : name,
           'global_qos_config' : domain
        }
        qos_queue_id = kwargs.get('queue_id')
        self._params['qos_queue_identifier'] = qos_queue_id


class QosForwardingClassFixture(QosForwardingClassFixture_v2):

    '''
    Fixture for creating Forwarding class object
    '''
    
    def __init__ (self, connections,
                 **kwargs):
        name = kwargs.get('name', None)
        domain = 'default-global-system-config'
        project = 'default-global-qos-config'
        prj_fqn = domain + ':' + project
        self._api = kwargs.get('option', 'quantum')
        self.inputs = connections.inputs
        self.connections = connections
        
        if name:
            uid = self._check_if_present(connections, name, [domain, project])
            if uid:
                super(VNFixture, self).__init__(connections=connections,
                                               uuid=uid)
                return
        else:
            name = get_random_name("ForwardingClass")
        self._construct_contrail_params(name, prj_fqn, kwargs)
        super(QosForwardingClassFixture, self).__init__(connections=connections,
                                       params=self._params)
    
    def _check_if_present (self, conn, forwarding_class_name, domain):
        uid = domain + [forwarding_class_name]
        obj = conn.get_orch_ctrl().get_api('vnc').get_forwarding_class(uid)
        if not obj:
            return None
        return uid

    def setUp (self):
        super(QosForwardingClassFixture, self).setUp()

    def cleanUp (self):
        super(QosForwardingClassFixture, self).cleanUp()

    def _construct_contrail_params (self, name, domain, kwargs):
        self._params = {
           'type': 'OS::ContrailV2::ForwardingClass',
           'name' : name,
           'global_qos_config' : domain
        }
        fc_id = kwargs.get('fc_id', None)
        dscp = kwargs.get('dscp', None)
        dot1p = kwargs.get('dot1p', None)
        exp = kwargs.get('exp', None)
        queue_uuid= kwargs.get('queue_uuid', None)
        queue_obj = self.connections.get_orch_ctrl().get_api('vnc').get_qos_queue(queue_uuid)
        queue_fq_name_str = queue_obj.get_fq_name_str()
        
        self._params['forwarding_class_vlan_priority'] = dot1p
        self._params['forwarding_class_mpls_exp'] = exp
        self._params['forwarding_class_id'] = fc_id
        self._params['forwarding_class_dscp'] = dscp
        self._params['qos_queue_refs'] = [queue_fq_name_str]


class QosConfigFixture(QosConfigFixture_v2):

    '''
    Fixture for creating Forwarding class object
    '''
    
    def __init__ (self, connections,
                 **kwargs):
        name = kwargs.get('name', None)
        
        self._api = kwargs.get('option', 'quantum')
        qos_config_type = kwargs.get('qos_config_type') or 'project'
        if qos_config_type != 'project':
            domain = 'default-global-system-config'
            project = 'default-global-qos-config'
            prj_fqn = domain + ':' + project
        else:
            domain = connections.domain_name
            prj = kwargs.get('project_name') or connections.project_name
            prj_fqn = domain + ':' + prj
        self.inputs = connections.inputs
        self.connections = connections
        
        if name:
            uid = self._check_if_present(connections, name, [domain, project])
            if uid:
                super(VNFixture, self).__init__(connections=connections,
                                               uuid=uid)
                return
        else:
            name = get_random_name("QosConfig")
        self._construct_contrail_params(name, prj_fqn, kwargs)
        super(QosConfigFixture, self).__init__(connections=connections,
                                       params=self._params)
    
    def _check_if_present (self, conn, qos_config_name, domain):
        uid = domain + [qos_config_name]
        obj = conn.get_orch_ctrl().get_api('vnc').get_qos_config(uid)
        if not obj:
            return None
        return uid

    def setUp (self):
        super(QosConfigFixture, self).setUp()

    def cleanUp (self):
        super(QosConfigFixture, self).cleanUp()

    def _construct_contrail_params (self, name, domain, kwargs):
        self._params = {
           'type': 'OS::ContrailV2::QosConfig',
           'name' : name
        }
        qos_config_type = kwargs.get('qos_config_type') or 'project'
        if qos_config_type != 'project':
            self._params['global_qos_config'] = domain
        else:
            self._params['project'] = domain
        
        default_fc_id = kwargs.get('default_fc_id', 0)
        self._params['default_forwarding_class_id'] = default_fc_id
        
        dscp_mapping = kwargs.get('dscp_mapping', {})
        self._params['dscp_entries'] = {}
        self._params['dscp_entries']['qos_id_forwarding_class_pair'] = []
        temp_dict = {}
        for key,value in dscp_mapping.items():
            temp_dict = {'key' : key,
                         'forwarding_class_id' : value}
            self._params['dscp_entries']['qos_id_forwarding_class_pair'].append(temp_dict)
            temp_dict = {}
        
        dot1p_mapping = kwargs.get('dot1p_mapping', {})
        self._params['vlan_priority_entries'] = {}
        self._params['vlan_priority_entries']['qos_id_forwarding_class_pair'] = []
        temp_dict = {}
        for key,value in dot1p_mapping.items():
            temp_dict = {'key' : key,
                         'forwarding_class_id' : value}
            self._params['vlan_priority_entries']['qos_id_forwarding_class_pair'].append(temp_dict)
            temp_dict = {}

        exp_mapping = kwargs.get('exp_mapping', {})
        self._params['mpls_exp_entries'] = {}
        self._params['mpls_exp_entries']['qos_id_forwarding_class_pair'] = []
        temp_dict = {}
        for key,value in exp_mapping.items():
            temp_dict = {'key' : key,
                         'forwarding_class_id' : value}
            self._params['mpls_exp_entries']['qos_id_forwarding_class_pair'].append(temp_dict)
            temp_dict = {}

