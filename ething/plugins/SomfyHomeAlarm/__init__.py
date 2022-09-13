# coding: utf-8
from ething.Device import *
from ething.plugin import Plugin
from ething.scheduler import set_interval
from ething.interfaces import Thermometer
import logging
from dateutil.parser import parse
from somfy_protect_api.api.somfy_protect_api import SomfyProtectApi
from somfy_protect_api.api import model

LOGGER = logging.getLogger(__name__)


REFRESH_INTERVAL = 30 # in seconds


TYPE_TO_CLASSNAME = {
    'mss_pir': 'SomfyHomeAlarmInfraredSensor',
    'mss_siren': 'SomfyHomeAlarmInDoorSiren',
    'mss_tag': 'SomfyHomeAlarmIntelliTag',
    'mss_remote': 'SomfyHomeAlarmKeyFob',
    'mss_outdoor_siren': 'SomfyHomeAlarmOutDoorSiren',
    'mss_plug': 'SomfyHomeAlarmLink',
}

def _toDict(obj, cls):
    d = dict()
    for attr in cls.__slots__:
        d[attr] = getattr(obj, attr, None)
    return d



class SomfyHomeAlarmAlarmTriggered(ResourceSignal):
    """
    is emitted each time an alarm was triggered
    """
    pass


class SomfyHomeAlarmSecurityLevelChanged(ResourceSignal):
    """
    is emitted each time the security level changed
    """
    def __init__(self, resource):
        super(SomfyHomeAlarmSecurityLevelChanged, self).__init__(resource, security_level=resource.security_level)


class SomfyHomeAlarmKeyFobOut(ResourceSignal):
    """
    is emitted each time a key fob was tagged out
    """
    pass


class SomfyHomeAlarmKeyFobIn(ResourceSignal):
    """
    is emitted each time a key fob was tagged in
    """
    pass


@attr('email', type=Email(), default='', description='email used on Somfy Protect Mobile App.')
@attr('password', type=String(), default='', description='password used on Somfy Protect Mobile App.')
@attr('connected', type=Boolean(), default=False, mode=READ_ONLY,
      description="Set to true when connected.")
@attr('token', mode=PRIVATE, default=None)
class SomfyHomeAlarm(Plugin):
    """
    Somfy plugin. Allow you to control the Somfy Home Alarm.
    """

    # the path of your Javascript index file, this file describe how your plugin should be integrated into the web interface.
    # remove it if not used
    JS_INDEX = './index.js'

    def load(self):
        self.api = None

    # this method is executed once, after the core instance is initialized (database, ...)
    def setup(self):
        self.connect()

    def on_config_change(self, dirty_attributes):
        if 'email' in dirty_attributes or 'password' in dirty_attributes:
            self.connect()

    def set_token(self, token):
        self.token = token

    def connect(self):
        self.notification.remove('somfy.credentials')

        self.connected = False

        if self.api:
            # a previous instance already exists
            if self.api.email == self.email and self.api.password == self.password:
                # same api, no need to reconnect
                return
            self.api = None
            self.token = None

        if self.email and self.password:
            LOGGER.info('connecting to SomfyProtectApi')

            self.api = SomfyProtectApi(
                username=self.email, password=self.password, token=self.token, token_updater=self.set_token
            )

            # Check if we already have a token
            if not self.token:
                try:
                    token = self.api.request_token()
                except: # raise oauthlib.oauth2.rfc6749.errors.InvalidGrantError if wrong credentials
                    # wrong credentials
                    self.logger.warning("cannot log in : wrong credentials !")
                    self.notification.warning('cannot log in : wrong credentials', title='Somfy', id='somfy.credentials')
                    self.api = None
                    return False
                self.set_token(token)

            self.connected = True

            self.refresh()

            return True

    @set_interval(REFRESH_INTERVAL)
    def refresh(self):
        if not self.api:
            return

        # List Sites
        try:
            sites = self.api.get_sites()
        except:
            # no internet connection maybe
            # requests.exceptions.ConnectionError
            return

        for site in sites:
            # check if the current site is already created !
            resource = self.core.find_one(lambda r: r.typeof('resources/SomfyHomeAlarmSite') and r.site_id == site.id)
            if resource is None:
                # not found, create it !
                resource = self.core.create('resources/SomfyHomeAlarmSite', {
                    'name': site.label,
                    'site_id': site.id,
                })

            if resource:
                # refresh state
                devices = self.api.get_devices(site_id=site.id)
                resource.refresh_with(site, devices)

        # todo: remove old site ?

    @method.return_type('object')
    def list_sites(self):
        if not self.api:
            return
        return [_toDict(site, model.Site) for site in self.api.get_sites()]

    @method.arg('site_id', type='string')
    @method.return_type('object')
    def list_devices(self, site_id):
        if not self.api:
            return
        return [_toDict(device, model.Device) for device in self.api.get_devices(site_id=site_id)]





@abstract
class SomfyHomeAlarmBase(Device):

    ACTIVITY_TIMEOUT = 600

    @property
    def api(self):
        return self.plugin.api

    @property
    def plugin(self):
        return self.core.plugins['SomfyHomeAlarm']


@throw(SomfyHomeAlarmAlarmTriggered, SomfyHomeAlarmSecurityLevelChanged)
@attr('site_id', type=String(), mode=READ_ONLY, description='Id to identify the current site.')
@attr('security_level', type=String(), default='disarmed', mode=READ_ONLY, description='The current security level of the site')
@attr('alarm_status', type=String(), default='none', mode=READ_ONLY, description='The current security level of the site')
class SomfyHomeAlarmSite(SomfyHomeAlarmBase):

    def on_attr_update(self, attr, new_value, old_value):
        super(SomfyHomeAlarmSite, self).on_attr_update(attr, new_value, old_value)

        if attr == 'security_level':
            self.emit(SomfyHomeAlarmSecurityLevelChanged(self))
        elif attr == 'alarm_status':
            if new_value != 'none':
                self.emit(SomfyHomeAlarmAlarmTriggered(self))


    def refresh_with(self, site_obj, devices_obj):
        # id: N9p1oC9m7zoylxdfgfdggfh...
        # label: Maison
        # security_level: disarmed
        # diagnosis_status: ok
        # alarm: {'status': 'none'}
        # services: {'backup_sms': False, 'mfa_service_enabled': True, 'lora_enabled': False, 'monitoring_enabled': False, 'on_site_intervention_enabled': False, 'link_over_gsm_enabled': False}
        #
        with self:
            self.security_level = getattr(site_obj, 'security_level', 'disarmed')
            self.alarm_status = getattr(site_obj, 'alarm', dict()).get('status', 'none')
            self.refresh_connect_state(True)

        for device in devices_obj:
            # check if the current device is already created !
            resource = self.core.find_one(
                lambda r: r.typeof('resources/SomfyHomeAlarmDevice') and r.device_id == device.id)
            if resource is None or resource.typeof('resources/SomfyHomeAlarmUnknown'):
                # not found, create it !
                type_str = getattr(device, 'device_definition', dict()).get('device_definition_id')
                if type_str:
                    clsname = TYPE_TO_CLASSNAME.get(type_str)
                    if clsname:
                        if resource: # must be of type SomfyHomeAlarmUnknown
                            # will be replaced by a new class
                            resource.remove()
                            resource = None
                    else:
                        if resource:
                            # still not implemented
                            continue
                        self.logger.warning("type %s not implemented !" % type_str)
                        clsname = 'SomfyHomeAlarmUnknown'

                    resource = self.core.create("resources/%s" % clsname, {
                        'name': device.label,
                        'device_id': device.id,
                        'createdBy': self,
                    })
                else:
                    continue

            if resource:
                # refresh state
                with resource:
                    resource.refresh_with(device)

        # todo: remove old device

    @method.arg('security_level', type=Enum(["disarmed", "armed", "partial"]))
    @method.return_type('object')
    def update_security_level(self, security_level):
        if not self.api:
            return
        return self.api.update_security_level(self.site_id, security_level)

    @method.return_type('object')
    def stop_alarm(self):
        if not self.api:
            return
        return self.api.stop_alarm(self.site_id)

    @method.arg('mode', type=Enum(["alarm", "silent"]))
    @method.return_type('object')
    def trigger_alarm(self, mode="alarm"):
        if not self.api:
            return
        return self.api.trigger_alarm(self.site_id, mode)


@abstract
@attr('device_id', type=String(), mode=READ_ONLY, description='Id to identify the current device.')
@attr('version', type=String(), default='none', mode=READ_ONLY, description='The current version of the device')
class SomfyHomeAlarmDevice(SomfyHomeAlarmBase):

    def __init__(self, *args, **kvargs):
        super(SomfyHomeAlarmInfraredSensor, self).__init__(*args, **kvargs)
        self._last_last_status_at = None

    @property
    def site(self):
        return self.createdBy

    # return True if the status need to be refreshed
    def refresh_with(self, device_obj):
        # id: xjJjVc67e04LA...
        # site_id: N9pgfdggS5iOsdf..
        # box_id: 4keNIH5OHOxlHfsdf...
        # label: Sirène intérieure
        # version: 9.0.0
        # device_definition: {'object': 'DeviceDefinition', 'device_definition_id': 'mss_siren', 'label': 'Myfox Security Siren', 'type': 'siren'}
        # status: {'battery_level': 100, 'rlink_state': 0, 'rlink_quality': -56, 'rlink_quality_percent': 100, 'device_lost': False, 'last_status_at': '2022-09-11T19:18:53.000000Z'}
        # diagnosis: {'is_everything_ok': True, 'problems': []}
        # settings: {'object': 'DeviceSettings', 'global': {'light_enabled': True, 'sound_enabled': True, 'auto_protect_enabled': True}, 'disarmed': {'auto_protect_enabled': True}, 'partial': {'auto_protect_enabled': True}, 'armed': {'auto_protect_enabled': True}}
        status = getattr(device_obj, 'status', dict())
        last_status_at = status.get('last_status_at', None)
        if last_status_at is not None and last_status_at == self._last_last_status_at:
            return False# no change !
        self._last_last_status_at = last_status_at

        with self:

            if 'battery_level' in status:
                self.battery = status['battery_level']
            else:
                self.battery = None

            if 'rlink_quality_percent' in status:
                self.rlink_quality = status['rlink_quality_percent']
            else:
                self.rlink_quality = None

            self.version = getattr(device_obj, 'version', 'none')
            self.refresh_connect_state(True)

        return True


# Infrared Sensor
# id: Whriv5aciEU...
# site_id: N9p1oC9m7...
# box_id: 4keNIH5O...
# label: couloir
# version: 2.3.0
# device_definition: {'object': 'DeviceDefinition', 'device_definition_id': 'mss_pir', 'label': 'Myfox Security Infrared Sensor', 'type': 'pir'}
# status: {'battery_level': 100, 'battery_low': False, 'rlink_quality': -68, 'rlink_quality_percent': 75, 'temperature': 25.8, 'temperatureAt': '2022-09-12T07:12:43.000000Z', 'device_lost': False, 'last_status_at': '2022-09-12T07:12:44.000000Z'}
# diagnosis: {'is_everything_ok': True, 'problems': []}
# settings: {'object': 'DeviceSettings', 'global': {'sensitivity_level': 'high', 'light_enabled': True, 'auto_protect_enabled': True, 'night_mode_enabled': False, 'prealarm_enabled': True}, 'disarmed': {'auto_protect_enabled': True}, 'partial': {'auto_protect_enabled': True}, 'armed': {'auto_protect_enabled': True}}
class SomfyHomeAlarmInfraredSensor(SomfyHomeAlarmDevice, Thermometer):

    def __init__(self, *args, **kvargs):
        super(SomfyHomeAlarmInfraredSensor, self).__init__(*args, **kvargs)
        self._last_temperatureAt = None

    def refresh_with(self, device_obj):
        if super(SomfyHomeAlarmInfraredSensor, self).refresh_with(device_obj):
            with self:
                status = getattr(device_obj, 'status', dict())
                temperature = status.get('temperature', None)
                temperatureAt = status.get('temperatureAt', None)
                if temperature is not None and temperatureAt is not None:
                    if self._last_temperatureAt != temperatureAt:
                        self.temperature = status.get('temperature', 0)
                self._last_temperatureAt = temperatureAt




# id: xjJjVc67e04...
# site_id: N9p1oC9m7zoy...
# box_id: 4keNIH5OHOxl...
# label: Sirène intérieure
# version: 9.0.0
# device_definition: {'object': 'DeviceDefinition', 'device_definition_id': 'mss_siren', 'label': 'Myfox Security Siren', 'type': 'siren'}
# status: {'battery_level': 100, 'rlink_state': 0, 'rlink_quality': -56, 'rlink_quality_percent': 100, 'device_lost': False, 'last_status_at': '2022-09-11T19:18:53.000000Z'}
# diagnosis: {'is_everything_ok': True, 'problems': []}
# settings: {'object': 'DeviceSettings', 'global': {'light_enabled': True, 'sound_enabled': True, 'auto_protect_enabled': True}, 'disarmed': {'auto_protect_enabled': True}, 'partial': {'auto_protect_enabled': True}, 'armed': {'auto_protect_enabled': True}}
class SomfyHomeAlarmInDoorSiren(SomfyHomeAlarmDevice):
    pass


# id: wCV6LXKidpfItjum...
# site_id: N9p1oC9m7zoyl...
# box_id: 4keNIH5OHOxlHMP...
# label: atelier
# version: 4.0.0
# device_definition: {'object': 'DeviceDefinition', 'device_definition_id': 'mss_tag', 'label': 'IntelliTag', 'type': 'tag'}
# status: {'recalibration_required': False, 'recalibrateable': True, 'cover_present': False, 'battery_level': 100, 'rlink_state': 0, 'rlink_quality': -75, 'rlink_quality_percent': 50, 'device_lost': False, 'last_status_at': '2022-09-11T22:01:43.000000Z'}
# diagnosis: {'is_everything_ok': True, 'problems': []}
# settings: {'object': 'DeviceSettings', 'global': {'sensitivity': 7, 'support_type': 'externdoor', 'night_mode_enabled': True, 'prealarm_enabled': True}, 'disarmed': None, 'partial': None, 'armed': None}
class SomfyHomeAlarmIntelliTag(SomfyHomeAlarmDevice):
    pass


# id: w9uZBbvnzotMsp...
# site_id: N9p1oC9m7zoy...
# box_id: 4keNIH5OHO...
# label: invité
# version: 245.0.0
# device_definition: {'object': 'DeviceDefinition', 'device_definition_id': 'mss_remote', 'label': 'Key Fob', 'type': 'remote'}
# status: {'device_lost': True, 'battery_level': 100, 'battery_level_state': 'ok', 'rlink_state': 0, 'rlink_quality': -72, 'last_status_at': None, 'last_check_in_state': '2022-08-26T17:16:55.000000Z', 'last_check_out_state': '2022-08-26T17:28:21.000000Z', 'keep_alive': 0}
# diagnosis: {'is_everything_ok': True, 'problems': []}
# settings: {'object': 'DeviceSettings', 'global': {'user_id': '3Q01fAEWzd73sE4SXQWC2kdjNpHOAwjP', 'enabled': True}, 'disarmed': None, 'partial': None, 'armed': None}
@throw(SomfyHomeAlarmKeyFobIn, SomfyHomeAlarmKeyFobOut)
@attr('at_home', type=Boolean(), default=False, mode=READ_ONLY, description='Tells if the key fob is at home or not')
@attr('last_check_in', type=Nullable(TzDate()), default=None, mode=READ_ONLY, description='last time the key fob enter home')
@attr('last_check_out', type=Nullable(TzDate()), default=None, mode=READ_ONLY, description='last time the key fob leave home')
class SomfyHomeAlarmKeyFob(SomfyHomeAlarmDevice):

    def refresh_with(self, device_obj):
        if super(SomfyHomeAlarmKeyFob, self).refresh_with(device_obj):
            with self:
                status = getattr(device_obj, 'status', dict())

                last_check_in_state = status.get('last_check_in_state', None)
                if last_check_in_state:
                    last_check_in_state = parse(last_check_in_state)
                last_check_out_state = status.get('last_check_out_state', None)
                if last_check_out_state:
                    last_check_out_state = parse(last_check_out_state)

                is_at_home = False
                if last_check_in_state and last_check_out_state:
                    is_at_home = last_check_in_state > last_check_out_state

                # if is_at_home != self.at_home:
                #     if is_at_home:
                #         self.emit(SomfyHomeAlarmKeyFobIn(self))
                #         self.store('presence', {
                #             'date': last_check_in_state,
                #             'at_home': True
                #         })
                #     else:
                #         self.emit(SomfyHomeAlarmKeyFobOut(self))
                #         self.store('presence', {
                #             'date': last_check_out_state,
                #             'at_home': False
                #         })

                self.last_check_out = last_check_out_state
                self.last_check_in = last_check_in_state
                self.at_home = is_at_home

    def on_attr_update(self, attr, new_value, old_value):
        super(SomfyHomeAlarmKeyFob, self).on_attr_update(attr, new_value, old_value)

        if attr == 'at_home':
            if new_value:
                if self.last_check_in:
                    self.emit(SomfyHomeAlarmKeyFobIn(self))
                    self.store('presence', {
                        'date': self.last_check_in,
                        'at_home': True
                    })
            else:
                if self.last_check_out:
                    self.emit(SomfyHomeAlarmKeyFobOut(self))
                    self.store('presence', {
                        'date': self.last_check_out,
                        'at_home': False
                    })


# id: 6XLjLKReGr34wC2t0tfdAwVZdaBNuu37
# site_id: N9p1oC9m7zoylxO4UQeTUBS5iOHTnXse
# box_id: 4keNIH5OHOxlHMP8Yd7zJeRwGcXlQ0qy
# label: sirene extérieure
# version: 1.9.0
# device_definition: {'object': 'DeviceDefinition', 'device_definition_id': 'mss_outdoor_siren', 'label': 'Myfox Security Outdoor Siren', 'type': 'siren'}
# status: {'battery_level': 100, 'rlink_quality': -57, 'rlink_quality_percent': 100, 'temperature': 23.8, 'temperatureAt': '2022-09-12T07:55:07.000000Z', 'device_lost': False, 'last_status_at': '2022-09-10T23:51:23.000000Z', 'mounted_at': '2022-09-10T08:43:31.000000Z'}
# diagnosis: {'is_everything_ok': True, 'problems': []}
# settings: {'object': 'DeviceSettings', 'global': {'light_enabled': True, 'sound_enabled': False, 'auto_protect_enabled': True, 'thresholdAcc': 10}, 'disarmed': {'auto_protect_enabled': True}, 'partial': {'auto_protect_enabled': True}, 'armed': {'auto_protect_enabled': True}}
class SomfyHomeAlarmOutDoorSiren(SomfyHomeAlarmDevice, Thermometer):

    def __init__(self, *args, **kvargs):
        super(SomfyHomeAlarmOutDoorSiren, self).__init__(*args, **kvargs)
        self._last_temperatureAt = None

    def refresh_with(self, device_obj):
        if super(SomfyHomeAlarmOutDoorSiren, self).refresh_with(device_obj):
            with self:
                status = getattr(device_obj, 'status', dict())
                temperature = status.get('temperature', None)
                temperatureAt = status.get('temperatureAt', None)
                if temperature is not None and temperatureAt is not None:
                    if self._last_temperatureAt != temperatureAt:
                        self.temperature = status.get('temperature', 0)
                self._last_temperatureAt = temperatureAt


# id: 1noKOkZ3hHsTJtQOvyYRBWxjaLglKCKO
# site_id: N9p1oC9m7zoylxO4UQeTUBS5iOHTnXse
# box_id: None
# label: Link
# version: 2.8.1
# device_definition: {'object': 'DeviceDefinition', 'device_definition_id': 'mss_plug', 'label': 'Link', 'type': 'box'}
# status: {'last_online_at': '2022-09-11T16:42:05.000000Z', 'last_offline_at': '2022-09-05T17:12:59.000000Z', 'battery_level': None, 'wifi_level': -46, 'wifi_level_percent': 65, 'mfa_quality_percent': 40, 'mfa_last_test_at': '2022-07-21T14:41:01.000000Z', 'mfa_last_test_success_at': '2022-09-12T04:46:13.000000Z', 'mfa_last_online_at': '2022-09-05T17:12:59.000000Z', 'mfa_last_offline_at': '2022-09-11T16:42:05.000000Z', 'mfa_last_connected_at': '2022-08-27T04:07:26.000000Z', 'mfa_last_disconnected_at': '2022-08-26T16:00:05.000000Z', 'lora_quality_percent': 0, 'lora_last_test_at': None, 'lora_last_test_success_at': None, 'lora_last_online_at': None, 'lora_test_on_going': False, 'lora_last_offline_at': '2022-09-11T16:42:05.000000Z', 'lora_last_connected_at': None, 'lora_last_disconnected_at': '2021-10-07T19:50:26.000000Z', 'ble_level': None, 'fsk_level': None, 'power_mode': 'current', 'power_state': 1, 'last_status_at': None}
# diagnosis: {'is_everything_ok': True, 'problems': []}
# settings: {'object': 'DeviceSettings', 'global': {'wifi_ssid': 'Livebox-9380'}, 'disarmed': None, 'partial': None, 'armed': None}
class SomfyHomeAlarmLink(SomfyHomeAlarmDevice):
    pass


class SomfyHomeAlarmUnknown(SomfyHomeAlarmDevice):
    pass
