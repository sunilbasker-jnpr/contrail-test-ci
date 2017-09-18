import test_v1
from tcutils.wrappers import preposttest_wrapper
from tcutils.util import get_random_name, get_random_cidr, get_random_cidrs,\
   get_an_ip
from common import resource_handler
from common.base import GenericTestBase

tmpl = {
    'heat_template_version': '2015-10-15',
    'outputs': {
        'vn1_id': {'value': {'get_attr': ['vn1', 'fq_name']}},
        'vm1_id': {'value': {'get_resource': 'vm1'}},
        'vm2_id': {'value': {'get_resource': 'vm2'}},
    },
    'parameters': {
        'domain': {'type': 'string'},
        'ipam': {'type': 'string'},
        'vn1_name': {'type': 'string'},
        'vn1_subnet1_prefix': {'type': 'string'},
        'vn1_subnet1_prefixlen': {'type': 'number'},
        'vn1_subnet1_dhcp': {'type': 'boolean'},
        'vn1_subnet2_prefix': {'type': 'string'},
        'vn1_subnet2_prefixlen': {'type': 'number'},
        'vm1_name': {'type': 'string'},
        'vm2_name': {'type': 'string'},
        'image': {'type': 'string'},
        'flavor': {'type': 'string'},
        'availability_zone': {
          'description': 'Name of availability zone to use for servers',
          'default': '',
          'type': 'string'},
        'availability_zone2': {
          'type': 'string'},
        'fixed_ip': {
          'type': 'string'},
    },
    'resources': {
        'vn1': {
            'type': 'OS::ContrailV2::VirtualNetwork',
            'properties': {
                'name': {'get_param': 'vn1_name'},
                'network_ipam_refs': [{'get_param': 'ipam'}],
                'network_ipam_refs_data': [{
                    'network_ipam_refs_data_ipam_subnets': [{
                        'network_ipam_refs_data_ipam_subnets_subnet': {
                            'network_ipam_refs_data_ipam_subnets_subnet_ip_prefix': {
                                'get_param': 'vn1_subnet1_prefix',
                            },
                            'network_ipam_refs_data_ipam_subnets_subnet_ip_prefix_len': {
                                'get_param': 'vn1_subnet1_prefixlen',
                            },
                        },
                        'network_ipam_refs_data_ipam_subnets_addr_from_start' : True,
                        'network_ipam_refs_data_ipam_subnets_enable_dhcp': {
                            'get_param': 'vn1_subnet1_dhcp',
                        },
                     },{
                        'network_ipam_refs_data_ipam_subnets_subnet': {
                            'network_ipam_refs_data_ipam_subnets_subnet_ip_prefix': {
                               'get_param': 'vn1_subnet2_prefix',
                            },
                            'network_ipam_refs_data_ipam_subnets_subnet_ip_prefix_len': {
                               'get_param': 'vn1_subnet2_prefixlen',
                            },
                        },
                        'network_ipam_refs_data_ipam_subnets_addr_from_start' : True,
                        'network_ipam_refs_data_ipam_subnets_enable_dhcp': True,
                    }]
                }],
            }
        },
        'vm1': {
            'type': 'OS::Nova::Server',
            'depends_on': ['vn1'],
            'properties': {
                'name': {'get_param': 'vm1_name'},
                'image' : { "get_param" :  "image" },
                'flavor' : { "get_param" : "flavor" },
                'availability_zone': {'get_param': 'availability_zone'},
                'networks' : [
                    {'network': { "get_resource" : "vn1"}}
                    #{"port": { "get_resource" : "vmi1"}}
                ]
            }
        },
        'vm2': {
            'type': 'OS::Nova::Server',
            'depends_on': ['vn1'],
            'properties': {
                'name': {'get_param': 'vm2_name'},
                'image' : { "get_param" :  "image" },
                'flavor' : { "get_param" : "flavor" },
                'availability_zone': {'get_param': 'availability_zone2'},
                'networks' : [
                    {'network': { "get_resource" : "vn1"},
                     'fixed_ip': {'get_param': 'fixed_ip'}}
                ]
            }
        },
    }
}
''' 'vmi1' : {
    "type" : "OS::ContrailV2::VirtualMachineInterface",
    "properties" : {
        "name" : { "get_param" : "vmi1_name" },
        "virtual_network_refs" : [{ "list_join" : [':', { "get_attr" : [ "vn1" , "fq_name" ] } ] }]
    }
} '''

env = {
    'parameters': {
        'domain': 'default-domain',
        'ipam': 'default-domain:default-project:default-network-ipam',
        'vn1_name': get_random_name('vn1'),
        'vn1_subnet1_prefix': '1001::',
        'vn1_subnet1_prefixlen': 64,
        'vn1_subnet1_dhcp': True,
        'vn1_subnet2_prefix': '101.101.101.0',
        'vn1_subnet2_prefixlen': 24,
        'vm1_name': get_random_name('vm1'),
        'vm2_name': get_random_name('vm2'),
        'flavor': 'contrail_flavor_tiny',
        'image': 'cirros',
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
        orch_ctrl = self.connections.get_orch_ctrl()
        zones = orch_ctrl.get_zones()
        hosts = orch_ctrl.get_hosts()
        #pass only zone for vm1
        env['parameters']['availability_zone'] = zones[0]
        #pass zone as well as host for vm2
        env['parameters']['availability_zone2'] = zones[0] + ':' + hosts[0]
        offset = 5
        fixed_ip = get_an_ip(env['parameters']['vn1_subnet2_prefix']+ '/' +
            str(env['parameters']['vn1_subnet2_prefixlen']), offset=offset)
        env['parameters']['fixed_ip'] = fixed_ip

        objs = resource_handler.create(self, tmpl, env)
        resource_handler.verify_on_setup(objs)
        #objs = resource_handler.update(self, objs, tmpl, env)
        #resource_handler.verify_on_setup(objs)
        return True

class TestwithHeat (Tests):

    @classmethod
    def setUpClass(cls):
        super(TestwithHeat, cls).setUpClass()
        cls.testmode = 'heat'

class TestwithOrch (Tests):

    @classmethod
    def setUpClass (cls):
        super(TestwithOrch, cls).setUpClass()
        cls.testmode = 'orch'

class TestOldStyle (GenericTestBase):

    @classmethod
    def setUpClass (cls):
        super(TestOldStyle, cls).setUpClass()
        cls.testmode = 'vnc'

    @classmethod
    def tearDownClass(cls):
        super(TestOldStyle, cls).tearDownClass()

    @preposttest_wrapper
    def test1 (self):
        hosts = self.connections.orch.get_hosts()
        zones = self.connections.orch.get_zones()
        vn1 = self.create_vn(vn_name=get_random_name('vn1'),
                vn_subnets=get_random_cidrs('dual'),
                option='quantum')
        #Create with only host name
        vm1 = self.create_vm(vn_fixture=vn1, vm_name=get_random_name('vm1'),
            node_name=hosts[0])
        #Create with only zone
        vm2 = self.create_vm(vn_fixture=vn1, vm_name=get_random_name('vm2'),
            zone=zones[0])
        #Create with both zone and host name and fixed ip
        fixed_ip = get_an_ip(vn1.subnets[0], offset=10)
        vm3 = self.create_vm(vn_fixture=vn1, vm_name=get_random_name('vm3'),
            zone=zones[0], node_name=hosts[0], fixed_ips=[fixed_ip])

        vn1.verify_on_setup()
        vm1.verify_on_setup()
        vm2.verify_on_setup()
        vm3.verify_on_setup()
        return True
