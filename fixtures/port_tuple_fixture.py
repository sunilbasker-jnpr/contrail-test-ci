from contrail_fixtures import ContrailFixture
from tcutils.util import retry
from vnc_api.vnc_api import PortTuple

class PortTupleFixture (ContrailFixture):

   vnc_class = PortTuple

   def __init__ (self, connections, uuid=None, params=None, fixs=None):
       super(PortTupleFixture, self).__init__(
           uuid=uuid,
           connections=connections,
           params=params,
           fixs=fixs)

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
       obj = self._vnc.get_port_tuple(self.uuid)
       found = 'not' if not obj else ''
       self.logger.debug('%s %s found in api-server' % (self, found))
       return obj != None, obj

   def _read (self):
       ret, obj = self._read_vnc_obj()
       if ret:
           self._vnc_obj = obj
       self._obj = self._vnc_obj

   def _create (self):
       self.logger.info('Creating %s' % self)
       self.uuid = self._ctrl.create_port_tuple(
           **self._args)

   def _delete (self):
       self.logger.info('Deleting %s' % self)
       self._ctrl.delete_port_tuple(
           obj=self._obj, uuid=self.uuid)

   def _update (self):
       self.logger.info('Updating %s' % self)
       self._ctrl.update_port_tuple(
           obj=self._obj, uuid=self.uuid, **self.args)

   @property
   def if_details (self):
       if getattr(self, '_if_details', None):
           return self._if_details
       ifs = self._vnc_obj.get_virtual_machine_interface_back_refs()
       if self.fixs:
           self._if_details =  [self.fixs['fqn-map'][intf] for intf in ifs]
       else:
           self._if_details =  [fixture.useFixture(
               PortFixture(connections=self.connections,
                   uuid=intf)) for intf in ifs]
       return self._if_details

   def verify_on_setup (self):
       self.assert_on_setup(*self._verify_in_api_server())
       #TODO: check if more verification is needed

   def verify_on_cleanup (self):
       self.assert_on_cleanup(*self._verify_not_in_api_server())
       #TODO: check if more verification is needed

   def _verify_in_api_server (self):
       if not self._read_vnc_obj()[0]:
           return False, '%s not found in api-server' % self
       return True, None

   @retry(delay=5, tries=6)
   def _verify_not_in_api_server (self):
       if self._vnc.get_port_tuple(self.uuid):
           msg = '%s not removed from api-server' % self
           self.logger.debug(msg)
           return False, msg
       self.logger.debug('%s removed from api-server' % self)
       return True, None

   def verify_if_details (self, ifs):
       if len(ifs) != len(self.if_details):
           msg = "Mismatch in number of interfaces: port-tuple vs template"
           return False, msg
       for intf in ifs:
           found = False
           for intf_obj in self.if_details:
               if intf['interface_type'] == \
                       intf_obj.virtual_machine_interface_properties.\
                       service_interface_type:
                   found = True
                   break
           if not found:
               msg = "intf type %s not found" % intf['interface_type']
               return False, msg
       return True, None
