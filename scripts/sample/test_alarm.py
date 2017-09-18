import test_v1
from tcutils.wrappers import preposttest_wrapper
from tcutils.util import get_random_name
from common import resource_handler
from common.base import GenericTestBase

tmpl = {
    'heat_template_version': '2015-10-15',
    'outputs': {
        'alarm_id': {'value': {'get_resource': 'alarm'}},
    },
    'parameters': {
        'severity': {'type': 'number'},
        'name': {'type': 'string'},
        'r1_op': {'type': 'string'},
        'r1_var': {'type': 'string'},
        'r1_val': {'type': 'string'},
        'r2_op': {'type': 'string'},
        'r2_var': {'type': 'string'},
        'r2_val': {'type': 'string'},
        'r3_op': {'type': 'string'},
        'r3_var': {'type': 'string'},
        'r3_val': {'type': 'string'},
    },
    'resources': {
        'alarm': {
            'type': 'OS::ContrailV2::Alarm',
            'properties': {
                'name': {'get_param': 'name'},
                'alarm_severity': {'get_param': 'severity'},
                'alarm_rules': {
                    'alarm_rules_or_list': [
                        {'alarm_rules_or_list_and_list': [
                            {'alarm_rules_or_list_and_list_operation':
                                {'get_param': 'r1_op'},
                             'alarm_rules_or_list_and_list_operand1':
                                {'get_param': 'r1_var'},
                             'alarm_rules_or_list_and_list_operand2': {
                                'alarm_rules_or_list_and_list_operand2_json_value': {
                                    'get_param': 'r1_val'
                                }
                             }
                            },
                            {'alarm_rules_or_list_and_list_operation':
                                {'get_param': 'r2_op'},
                             'alarm_rules_or_list_and_list_operand1':
                                {'get_param': 'r2_var'},
                             'alarm_rules_or_list_and_list_operand2': {
                                'alarm_rules_or_list_and_list_operand2_json_value': {
                                    'get_param': 'r2_val'
                                }
                             }
                            }],
                        },
                        {'alarm_rules_or_list_and_list': [
                            {'alarm_rules_or_list_and_list_operation':
                                {'get_param': 'r3_op'},
                             'alarm_rules_or_list_and_list_operand1':
                                {'get_param': 'r3_var'},
                             'alarm_rules_or_list_and_list_operand2': {
                                'alarm_rules_or_list_and_list_operand2_json_value': {
                                    'get_param': 'r3_val'
                                }
                             }
                            }],
                        }
                    ]
                },
            }
        },
    }
}

env = {
    'parameters': {
        'name': get_random_name('alarm'),
        'severity': 10,
        'r1_op': '<=',
        'r1_var': 'UveVirtualNetworkConfig.total_acl_rules',
        'r1_val': '5',
        'r2_op': '>=',
        'r2_var': 'UveVirtualNetworkConfig.total_acl_rules',
        'r2_val': '1',
        'r3_op': '==',
        'r3_var': 'UveVirtualNetworkConfig.total_acl_rules',
        'r3_val': '7',
    }
}

class Tests (test_v1.BaseTestCase_v1):

    @classmethod
    def setUpClass (cls):
        super(Tests, cls).setUpClass()

    @classmethod
    def tearDownClass (cls):
        super(Tests, cls).tearDownClass()

    @preposttest_wrapper
    def test1 (self):
        objs = resource_handler.create(self, tmpl, env)
        resource_handler.verify_on_setup(objs)
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
