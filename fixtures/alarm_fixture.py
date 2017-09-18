#TODO: replaces alarm_test.py
from contrail_fixtures import ContrailFixture
from tcutils.util import retry
from vnc_api.vnc_api import Alarm
from tcutils.util import retry_and_log

class AlarmFixture_v2 (ContrailFixture):

    vnc_class = Alarm

    def __init__ (self, connections, uuid=None, params=None, fixs=None):
        super(AlarmFixture_v2, self).__init__(
                uuid=uuid,
                connections=connections,
                params=params,
                fixs=fixs)
        self.api_s_inspect = connections.api_server_inspect

    def get_attr (self, lst):
        if lst == ['fq_name']:
            return self.fq_name
        return None

    def get_resource (self):
        return self.uuid

    @retry_and_log(delay=1, tries=5)
    def _read_vnc_obj (self):
        obj = self._vnc.get_alarm(self.uuid)
        err = 'alarm (%s) not found in api-server' % self.uuid
        return obj != None, obj if obj else err

    def _read (self):
        ret, obj = self._read_vnc_obj()
        if ret:
            self._vnc_obj = obj
            self._obj = self._vnc_obj

    def _create (self):
        self.uuid = self._ctrl.create_alarm(**self._args)

    def _delete (self):
        self._ctrl.delete_alarm(obj=self._obj, uuid=self.uuid)

    def _update (self):
        self._ctrl.update_alarm(obj=self._obj, uuid=self.uuid, **self.args)

    def verify_on_setup (self):
        self.assert_on_setup(*self._verify_in_api_server())
        self.assert_on_setup(*self._verify_alarm_config())

    def verify_on_cleanup (self):
        self.assert_on_cleanup(*self._verify_not_in_api_server())

    def _verify_in_api_server (self):
        if not self._read_vnc_obj()[0]:
            return False, 'alarm (%s) not found in api-server' % self.uuid
        return True, None

    @retry_and_log(delay=5, tries=6)
    def _verify_not_in_api_server (self):
        if self._vnc.get_alarm(self.uuid):
            err = 'alarm (%s) not removed from api-server' % self.uuid
            return False, err
        return True, None

    @retry_and_log(delay=3, tries=3)
    def _verify_alarm_config (self):
        try:
            alarm_config = self.api_s_inspect.get_cs_alarm(alarm_id=self.uuid)
            alarm = alarm_config['alarm']
        except (TypeError, KeyError) as e:
            return False, "No alarm info in API introspect"
        if not self._args:
            return True, None
        name = self._args.get('name')
        if name and name != alarm.get('display_name'):
            raise Exception('Alarm name mismatch %s:%s' % (name,
                            alarm.get('display_name')))
        uve_keys = self._args.get('uve_keys')
        if uve_keys and uve_keys != alarm.get('uve_keys'):
            raise Exception('Uve_keys mismatch\n %s\n %s' % (uve_keys,
                            alarm.get('uve_keys')))
        rules = self._args.get('alarm_rules')
        if rules and not alarm.get('alarm_rules'):
            raise Exception('Rules are not present in config')
        self.logger.info('Alarm %s configured properly ' %self.name)
        return True, None

#
# TODO: this fixture is not needed if alarm-test can be rewritten
#from tcutils.util import get_random_name
#
#class AlarmFixture (AlarmFixture_v2):
#
#    ''' Fixture for backward compatibility '''
#
#    def __init__ (self, connections, **kwargs):alarm_name=None, uve_keys=[],
#                    project_fixture=None, alarm_rules=None):
#        self.params = {
#            'type': 'OS::ContrailV2::Alarm',
#            'name' : kwargs.get('alarm_name', get_random_name('alarm'),
#        }
#        if kwargs.get('alarm_rules'):
#            self.params['alarm_rules'] = kwargs.get('alarm_rules'),
#        if kwargs.get('alarm_severity'):
#            self.params['alarm_severity'] = kwargs.get('alarm_severity')
#        if kwargs.get('uve_keys'):
#            self.params['uve_keys'] = {'uve_keys_uve_key' : uve_keys}
#        if kwargs.get('project_fixture'):
#            self.params['parent_type'] = 'project'
#            self.params['project'] = kwargs.get('project_fixture').fq_name
#        elif kwargs.get('project_name'):
#            self.params['parent_type'] = 'project'
#            self.params['project'] = kwargs.get('project_name')
#        else:
#            self.params['parent_type'] = 'global-system-config'
#            self.params['global_system_config'] = [
#                                    'default-global-system-config']
#        super(AlarmFixture, self).__init__(connections=connections,
#                params=self.params)
