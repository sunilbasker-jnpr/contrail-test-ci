import test_v1
from tcutils.wrappers import preposttest_wrapper
from tcutils.util import get_random_name, get_random_cidr, get_random_cidrs
from common import resource_handler
from common.base import GenericTestBase
from common.qos.base import QosTestBase

tmpl = {
   'heat_template_version': '2015-04-30',
   'outputs': {
       'fc_uid': {'value': {'get_resource': 'fc_test'}}
   },
   'parameters': {
       'fc_name': {'type': 'string'},
       'fc_dot1p': {'type': 'number'},
       'fc_exp': {'type': 'number'},
       'fc_id': {'type': 'number'},
       'fc_dscp': {'type': 'number'},
       'qos_queue_refs': {'type': 'string'},
       'qos_queue_identifier': {'type': 'number'},
       'qos_queue_name': {'type': 'string'},
       'global_parent_qos': {'type': 'string'},
       'qos_config_name': {'type': 'string'},
       'qos_config_type': {'type': 'string'}, # Could be 'vhost', 'fabric' or 'project'
       'default_fc_id': {'type': 'number'},
       #'project_name': {'type': 'string'},
       'input_dot1p_entry_1': {'type': 'number'},
       'input_dot1p_entry_2': {'type': 'number'},
       'input_exp_entry_1': {'type': 'number'},
       'input_exp_entry_2': {'type': 'number'},
       'input_dscp_entry_1': {'type': 'number'},
       'input_dscp_entry_2': {'type': 'number'},
       'fc_id_junk_entry': {'type': 'number'}
   },
    'resources' : {
        'fc_test': {
            'type': 'OS::ContrailV2::ForwardingClass',
            'depends_on': ['qos_queue_test'],
            'properties': { 
                'name': { 'get_param': 'fc_name' },
                'forwarding_class_vlan_priority': { 'get_param': 'fc_dot1p' },
                'forwarding_class_mpls_exp': { 'get_param': 'fc_exp' },
                'forwarding_class_id': { 'get_param': 'fc_id' },
                'forwarding_class_dscp': { 'get_param': 'fc_dscp' },
                'qos_queue_refs': [{ 'get_param': 'qos_queue_refs' }],
                'global_qos_config': { 'get_param': 'global_parent_qos' }
            }
        },
        'qos_queue_test': {
            'type': 'OS::ContrailV2::QosQueue',
            'properties': { 
                'name': { 'get_param': 'qos_queue_name' },
                'qos_queue_identifier': { 'get_param': 'qos_queue_identifier' },
                'global_qos_config': { 'get_param': 'global_parent_qos' }
            }
        },
        'qos_config_test': {
            'type': 'OS::ContrailV2::QosConfig',
            'properties': { 
                'name': { 'get_param': 'qos_config_name' },
                'qos_config_type': { 'get_param': 'qos_config_type' },
                #'project': { 'get_param': 'project_name' },
                'global_qos_config': { 'get_param': 'global_parent_qos' },
                'default_forwarding_class_id': { 'get_param': 'default_fc_id' },
                'vlan_priority_entries': {
                    'vlan_priority_entries_qos_id_forwarding_class_pair': [{
                        'vlan_priority_entries_qos_id_forwarding_class_pair_key': { 'get_param': 'input_dot1p_entry_1' },
                        'vlan_priority_entries_qos_id_forwarding_class_pair_forwarding_class_id': { 'get_param': 'fc_id' }
                    },
                    {
                        'vlan_priority_entries_qos_id_forwarding_class_pair_key': { 'get_param': 'input_dot1p_entry_2' },
                        'vlan_priority_entries_qos_id_forwarding_class_pair_forwarding_class_id': { 'get_param': 'fc_id_junk_entry' }
                    }],
                },
                'mpls_exp_entries': {
                    'mpls_exp_entries_qos_id_forwarding_class_pair': [{
                        'mpls_exp_entries_qos_id_forwarding_class_pair_key': { 'get_param': 'input_exp_entry_1' },
                        'mpls_exp_entries_qos_id_forwarding_class_pair_forwarding_class_id': { 'get_param': 'fc_id' }
                    },
                    {
                        'mpls_exp_entries_qos_id_forwarding_class_pair_key': { 'get_param': 'input_exp_entry_2' },
                        'mpls_exp_entries_qos_id_forwarding_class_pair_forwarding_class_id': { 'get_param': 'fc_id_junk_entry' }
                    }],
                },
                'dscp_entries': {
                    'dscp_entries_qos_id_forwarding_class_pair': [{
                        'dscp_entries_qos_id_forwarding_class_pair_key': { 'get_param': 'input_dscp_entry_1' },
                        'dscp_entries_qos_id_forwarding_class_pair_forwarding_class_id': { 'get_param': 'fc_id' }
                    },
                    {
                        'dscp_entries_qos_id_forwarding_class_pair_key': { 'get_param': 'input_dscp_entry_2' },
                        'dscp_entries_qos_id_forwarding_class_pair_forwarding_class_id': { 'get_param': 'fc_id_junk_entry' }
                    }],
                }
            }
        }
    }
}


env = {
   'parameters': {
       'fc_name': 'TestFC',
       'fc_dot1p': 4,
       'fc_exp': 4,
       'fc_dscp': 24,
       'fc_id': 1,
       'qos_queue_refs': 'default-global-system-config:default-global-qos-config:TestQOSQueue',
       'qos_queue_identifier': 115,
       'qos_queue_name': 'TestQOSQueue',
       'global_parent_qos': 'default-global-system-config:default-global-qos-config',
       'qos_config_name': 'TestQosConfig',
       'qos_config_type': 'vhost', # # Could be 'vhost', 'fabric' or 'project'
       #'qos_config_type': 'project',
       #'project_name': 'default-domain:admin',
       'default_fc_id': 10,
       'input_dot1p_entry_1': 5,
       'input_dot1p_entry_2': 6,
       'input_exp_entry_1': 5,
       'input_exp_entry_2': 6,
       'input_dscp_entry_1': 30,
       'input_dscp_entry_2': 40,
       'fc_id_junk_entry': 2
   }
}


'''
Intead if Qos config on vhost/fabric, for Qos config on a project, do the following changes:
Comment following:
#'qos_config_type': 'vhost', # Could be "vhost, " fabric" or "project"
Uncomment following:
'qos_config_type': 'project'

Uncomment project form parameters, respurces and env:
'project_name': {'type': 'string'}
'project': { 'get_param': 'project_name' },
'project_name': 'default-domain:admin',

Comment the global_qos_config part from qos_config resources section
#'global_qos_config': { 'get_param': 'global_parent_qos' }
'''


class Tests (test_v1.BaseTestCase_v1):

    @classmethod
    def setUpClass (cls):
       super(Tests, cls).setUpClass()
       cls.testmode = 'vnc'

    @classmethod
    def tearDownClass (cls):
       super(Tests, cls).tearDownClass()

    @preposttest_wrapper
    def test1 (self):
       objs = resource_handler.create(self, tmpl, env)
       resource_handler.verify_on_setup(objs)
       #env['parameters']['vn1_subnet1_dhcp'] = False
       #env['parameters']['vn1_subnet2_prefix'] = '1.1.1.0'
       #env['parameters']['vn1_subnet2_prefixlen'] = 24
       #objs = resource_handler.update(self, objs, tmpl, env)
       return True

class TestwithHeat (Tests):

    @classmethod
    def setUpClass(cls):
       super(TestwithHeat, cls).setUpClass()
       cls.testmode = 'heat'

class TestwithVnc (Tests):

    @classmethod
    def setUpClass (cls):
       super(TestwithVnc, cls).setUpClass()
       cls.testmode = 'vnc'

class TestOldStyle (QosTestBase):

    @classmethod
    def setUpClass (cls):
       super(TestOldStyle, cls).setUpClass()
       cls.testmode = 'vnc'

    @classmethod
    def tearDownClass(cls):
       super(TestOldStyle, cls).tearDownClass()

    @preposttest_wrapper
    def test1 (self):
        logical_ids = [15, 45, 75, 115, 145, 175, 215, 245]
        queues = []
        for logical_id in logical_ids:
            entry = {'queue_id': logical_id}
            queues.append(entry)
        queue_fixtures = self.setup_queues(queues)
        
        fc = [{'fc_id': 1, 'dscp': 10, 'dot1p': 1, 'exp': 1,
                       #'queue_fixture' : queue_fixtures[0]},
                       'queue_uuid' : queue_fixtures[0].uuid},
              {'fc_id': 2, 'dscp': 20, 'dot1p': 2, 'exp': 2,
                       #'queue_fixture' : queue_fixtures[1]}]
                        'queue_uuid' : queue_fixtures[1].uuid},
              {'fc_id': 3, 'dscp': 30, 'dot1p': 3, 'exp': 3,
                       #'queue_fixture' : queue_fixtures[1]}]
                        'queue_uuid' : queue_fixtures[3].uuid}]
        fc_fixture = self.setup_fcs(fc)
        
        dscp_map = {15: 1 , 25: 2}
        dot1p_map = {3 : 1, 5 : 2}
        exp_map = {1: 1 , 7: 2}
        qos_fixture = self.setup_qos_config(dscp_map=dscp_map,
                                            dot1p_map = dot1p_map,
                                            exp_map = exp_map,
                                            default_fc_id=3)
        
        
