# coding: utf-8
import zigate
from ething import Device
from ething.reg import *
from ething.interfaces import *


zigate_device_classes = list()


class ZigateDeviceMetaClass(MetaReg):
    def __new__(meta, name, bases, dct):
        cls = MetaReg.__new__(meta, name, bases, dct)

        if getattr(cls, '_REGISTER_', True) is not False and (hasattr(cls, 'isvalid') or hasattr(cls, 'isvalid_ep')):
            zigate_device_classes.append(cls)

        return cls


@abstract
@meta(disable_creation=True)
@meta(icon='mdi-alpha-z-box')
@attr('lqi', type=Number(), default=0, mode = READ_ONLY, description="percentage of link quality indicator")
@attr('endpoint', type=Nullable(Integer()), mode = READ_ONLY, default=None, description="If set, this device is only bind to a single endpoint")
@attr('ieee', type=String(allow_empty=False), mode = READ_ONLY, description="The ieee address of the device")
@attr('addr', type=String(), default='', mode = READ_ONLY, description="The network address of the device")
@attr('typename', type=String(), default='', mode = READ_ONLY, description="The type name of the device")
@attr('manufacturer', type=String(), default='', mode = READ_ONLY, description="The manufacturer of the device")
class ZigateBaseDevice(with_metaclass(ZigateDeviceMetaClass, Device)):
    ACTIVITY_TIMEOUT = 1800

    @property
    def z(self):
        return self.core.plugins['zigate'].z

    @property
    def zdevice(self):
        return self.z.get_device_from_ieee(self.ieee)

    @attr()
    def mac_capability(self):
        zdevice = getattr(self, 'zdevice', None)
        return zdevice.info.get('mac_capability') if zdevice else ''

    def process_signal(self, signal, kwargs):
        zdevice = kwargs.get('device')

        if self.error and zdevice.get_property_value('type'):
            self.error = None

        if signal == zigate.ZIGATE_DEVICE_NEED_DISCOVERY:
            self.error = 'need discovery'
        elif zigate.ZIGATE_DEVICE_ADDRESS_CHANGED:
            self.addr = zdevice.addr
        elif signal == zigate.ZIGATE_DEVICE_REMOVED:
            self.refresh_connect_state(False)
            return

        self.lqi = zdevice.lqi_percent

        connected = not zdevice.missing
        self.refresh_connect_state(connected)

        if signal == zigate.ZIGATE_ATTRIBUTE_UPDATED or signal == zigate.ZIGATE_ATTRIBUTE_ADDED:
            attribute = kwargs.get('attribute') # {'endpoint': 1, 'cluster': 1026, 'addr': 'abcd', 'attribute': 0, 'name': 'temperature', 'value': 13.58, 'unit': '°C', 'type': <class 'float'>, 'data': 1358}
            ep = attribute.get('endpoint')
            if self.endpoint is None or self.endpoint == ep:
                name = attribute.get('name')
                value = attribute.get('value')
                if name and value is not None:
                    if name == 'battery_voltage':
                        self.battery = zdevice.battery_percent
                    else:
                        self.process_attr(name, value, attribute)

    def init_state(self):
        """
        is used to initialize the internal state
        """
        zdevice = self.zdevice

        with self:
            for attribute in zdevice.attributes:
                if (self.endpoint is not None and attribute['endpoint'] != self.endpoint) or attribute['cluster'] < 5:
                    continue

                name = attribute.get('name')
                value = attribute.get('value')

                if name and value is not None:
                    self.process_attr(name, value, attribute)

    def process_attr(self, name, value, attribute):
        pass

    @classmethod
    def create_device(cls, plugin, zdevice, endpoint=None, **kwargs):
        name = zdevice.get_property_value('type', cls.__name__)
        #if endpoint is not None:
        #    name = '%s #%d' % (name, endpoint)

        if zdevice.info.get('power_type', 0) == 1:
            battery = None  # plugged
        else:
            battery = zdevice.battery_percent

        attrs = {
            'name': name,
            'ieee': zdevice.ieee,
            'addr': zdevice.addr,
            'lqi': zdevice.lqi_percent,
            'endpoint': endpoint,
            'description': zdevice.get_property_value('description', ''),
            'typename': zdevice.get_property_value('type', ''),
            'manufacturer': zdevice.get_property_value('manufacturer', ''),
            'battery': battery
        }

        attrs.update(kwargs)

        plugin.logger.debug('create device %s %s', cls.__name__, attrs)

        dev = plugin.core.create(cls, attrs)

        if dev:
            dev.init_state()

        return dev

    def remove(self):
        try:
            self.z.remove_device(self.addr)
        except:
            pass
        super(ZigateBaseDevice, self).remove()


# specific devices


class ZMihomeMagnet(ZigateBaseDevice, DoorSensor):
    """
    Mihome door Sensor.
    """

    @classmethod
    def isvalid(cls, plugin, zigate_device_instante):
        return zigate_device_instante.get_property_value('type') in ['lumi.sensor_magnet', 'lumi.sensor_magnet.aq2']

    def process_attr(self, name, value, attribute):
        if name == 'onoff':
            self.state = value


class ZMihomeSwitch(ZigateBaseDevice, Switch):
    """
    Mihome button.
    """

    @classmethod
    def isvalid(cls, plugin, zigate_device_instante):
        return zigate_device_instante.get_property_value('type') in ['lumi.ctrl_ln1', 'lumi.sensor_86sw1']

    def process_attr(self, name, value, attribute):
        if name == 'onoff':
            self.state = value


class ZMihomeButton(ZigateBaseDevice, Button):
    """
    Mihome button.
    """

    @classmethod
    def isvalid(cls, plugin, zigate_device_instante):
        return zigate_device_instante.get_property_value('type') in ['lumi.sensor_switch', 'lumi.sensor_switch.aq2', 'lumi.sensor_switch.aq3', 'lumi.remote.b1acn01', 'lumi.remote.b286acn01']

    def process_attr(self, name, value, attribute):
        if name == 'onoff':
            if value:
                # cf. https://zigate.fr/produits-xiaomi-compatibles-zigate/compatible/bouton/
                self.click(type='single')
        elif name == 'multiclick':
            if isinstance(value, string_types):
                if value == 'Click':
                    self.click(type='single')
                elif value == 'Double Click':
                    self.click(type='double')
                elif value == 'Long Click':
                    self.click(type='long_click')
                elif value == 'Shake':
                    self.click(type='shake')
                else:
                    self.click(type=value)
            else: # int
                if value == 1:
                    self.click(type='single')
                elif value == 2:
                    self.click(type='double')
                elif value > 2:
                    self.click(type='%d click' % value)


# generic class

# todo: lock devices


class ZigateCoverDevice(ZigateBaseDevice, Cover):

    @classmethod
    def isvalid_ep(cls, plugin, zdev, endpoint):
        actions = zdev.available_actions(endpoint).get(endpoint)
        return zigate.ACTIONS_COVER in actions

    def process_attr(self, name, value, attribute):
        if name == 'current_position_lift_percentage':
            self.position = value

    def _send_cmd(self, cmd):
        ep = self.endpoint

        res = self.z.action_onoff(self.addr, ep, cmd)

        if not res:
            # command status is bad !
            raise Exception('unable to reach the device')

    def open_cover(self):
        self._send_cmd(0x00)

    def close_cover(self):
        self._send_cmd(0x01)

    def stop_cover(self):
        self._send_cmd(0x02)


climate_mode_type = Enum(['away', 'home'])


@attr('mode', type=climate_mode_type, default='home', description='the mode of the climate')
class ZigateClimateDevice(ZigateBaseDevice, Thermostat, Thermometer):

    @classmethod
    def isvalid_ep(cls, plugin, zdev, endpoint):
        actions = zdev.available_actions(endpoint).get(endpoint)
        return zigate.ACTIONS_THERMOSTAT in actions

    def _update_target_temperature(self):
        if self.mode == 'away':
            attr = 0x0014
        else:
            attr = 0x0012
        t = 0
        a = self.zdevice.get_attribute(self.endpoint, 0x0201, attr)
        if a:
            t = a.get('value', 0)
        self.target_temperature = t

    def process_attr(self, name, value, attribute):
        if name == 'local_temperature':
            self.temperature = value
        elif name == 'occupancy':
            self.mode = 'home' if value != 0 else 'away'
            self._update_target_temperature()
        elif name == 'occupied_heating_setpoint':
            self._update_target_temperature()
        elif name == 'unoccupied_heating_setpoint':
            self._update_target_temperature()

    @method.arg('mode', type=climate_mode_type)
    def set_mode(self, mode):
        if mode == 'away':
            self.z.write_attribute_request(self.addr, self.endpoint, 0x0201, [(0x0002, 0x18, 0)])
        else:
            self.z.write_attribute_request(self.addr, self.endpoint, 0x0201, [(0x0002, 0x18, 1)])

    def set_target_temperature(self, temperature):
        temperature = int(temperature * 100)
        if self.mode == 'away':
            attr = 0x0014
        else:
            attr = 0x0012
        self.z.write_attribute_request(self.addr, self.endpoint, 0x0201, [(attr, 0x29, temperature)])


class ZigateGenericColourDimmableLightDevice(ZigateBaseDevice, RGBWLight):

    @classmethod
    def isvalid_ep(cls, plugin, zdev, endpoint):
        device_id = zdev.endpoints[endpoint].get('device', 0xffff)
        # 0x0102: Colour Dimmable Light
        if device_id == 0x0102:
            return True

        actions = zdev.available_actions(endpoint).get(endpoint)

        return zigate.ACTIONS_ONOFF in actions and zigate.ACTIONS_LEVEL in actions and zigate.ACTIONS_HUE in actions

    def process_attr(self, name, value, attribute):
        if name == 'onoff':
            self.state = value
        elif name == 'current_level': # [0-100]
            self.level = value
        elif name == 'current_hue': # [0-360]
            self.hue = value
        elif name == 'current_saturation': # [0-100]
            self.saturation = value

    def setState(self, state):
        onoff = zigate.ON if state else zigate.OFF
        ep = self.endpoint

        res = self.z.action_onoff(self.addr, ep, onoff)

        if not res:
            # command status is bad !
            raise Exception('unable to reach the device')

    def setLevel(self, level):
        onoff = zigate.ON if level > 0 else zigate.OFF
        ep = self.endpoint

        res = self.z.action_move_level_onoff(self.addr, ep, onoff, level)

        if not res:
            # command status is bad !
            raise Exception('unable to reach the device')

    def setColor(self, hue, saturation):
        ep = self.endpoint

        res = self.z.action_move_hue_saturation(self.addr, ep, hue, saturation)

        if not res:
            # command status is bad !
            raise Exception('unable to reach the device')


class ZigateGenericDimmableLightDevice(ZigateBaseDevice, DimmableLight):

    @classmethod
    def isvalid_ep(cls, plugin, zdev, endpoint):
        device_id = zdev.endpoints[endpoint].get('device', 0xffff)
        # 0x0101: Dimmable Light
        if device_id == 0x0101:
            return True

        actions = zdev.available_actions(endpoint).get(endpoint)

        return zigate.ACTIONS_ONOFF in actions and zigate.ACTIONS_LEVEL in actions

    def process_attr(self, name, value, attribute):
        if name == 'onoff':
            self.state = value
        elif name == 'current_level':
            self.level = value

    def setState(self, state):
        onoff = zigate.ON if state else zigate.OFF
        ep = self.endpoint

        res = self.z.action_onoff(self.addr, ep, onoff)

        if not res:
            # command status is bad !
            raise Exception('unable to reach the device')

    def setLevel(self, level):
        onoff = zigate.ON if level > 0 else zigate.OFF
        ep = self.endpoint

        res = self.z.action_move_level_onoff(self.addr, ep, onoff, level)

        if not res:
            # command status is bad !
            raise Exception('unable to reach the device')


class ZigateGenericLightDevice(ZigateBaseDevice, Light):

    @classmethod
    def isvalid_ep(cls, plugin, zdev, endpoint):
        device_id = zdev.endpoints[endpoint].get('device', 0xffff)
        # 0x0100: ON/OFF Light
        if device_id == 0x0100:
            return True

    def process_attr(self, name, value, attribute):
        if name == 'onoff':
            self.state = value

    def setState(self, state):
        onoff = zigate.ON if state else zigate.OFF
        ep = self.endpoint

        if ep is None:
            res = self.zdevice.action_onoff(onoff)
        else:
            res = self.z.action_onoff(self.addr, ep, onoff)

        if not res:
            # command status is bad !
            raise Exception('unable to reach the device')


class ZigateGenericDimmerDevice(ZigateBaseDevice, Dimmer):

    @classmethod
    def isvalid_ep(cls, plugin, zdev, endpoint):

        device_id = zdev.endpoints[endpoint].get('device', 0xffff)
        if device_id == 0x0104: # 0x0104: Dimmer Switch
            return True

        actions = zdev.available_actions(endpoint).get(endpoint)
        if len(actions) > 0:
            # sensor does not have any actions !
            return

        in_clusters = zdev.endpoints[endpoint].get('in_clusters', [])

        return 0x0006 in in_clusters and 0x0008 in in_clusters

    def process_attr(self, name, value, attribute):
        if name == 'onoff':
            self.level = 100 if value else 0
        elif name == 'current_level':
            self.level = value


@dynamic
@meta(icon='mdi-access-point')
class ZigateGenericSensorDevice(ZigateBaseDevice):

    @classmethod
    def isvalid_ep(cls, plugin, zdev, endpoint):

        actions = zdev.available_actions(endpoint).get(endpoint)
        if len(actions) > 0:
            # sensor does not have any actions !
            return

        interfaces = set()

        # scan the attributes
        for attribute in zdev.attributes:
            if attribute['endpoint'] != endpoint or attribute['cluster'] < 5:
                continue

            name = attribute.get('name')

            if name:
                if 'temperature' in name:
                    interfaces.add(Thermometer)
                elif 'humidity' in name:
                    interfaces.add(HumiditySensor)
                elif 'luminosity' in name:
                    interfaces.add(LightSensor)
                elif 'pressure' in name:
                    interfaces.add(PressureSensor)

        if interfaces:
            return create_dynamic_class(cls, *interfaces)

    def process_attr(self, name, value, attribute):
        if 'temperature' in name and self.typeof(Thermometer):
            self.temperature = value
        elif 'humidity' in name and self.typeof(PressureSensor):
            self.humidity = value
        elif 'pressure' in name and self.typeof(HumiditySensor):  # mbar
            self.pressure = round(value * 100.)
        elif 'luminosity' in name and self.typeof(LightSensor):  # lm
            self.light_level = value


class ZigateOccupencySensorDevice(ZigateBaseDevice, OccupencySensor):

    @classmethod
    def isvalid_ep(cls, plugin, zdev, endpoint):

        actions = zdev.available_actions(endpoint).get(endpoint)
        if len(actions) > 0:
            # sensor does not have any actions !
            return

        # scan the attributes
        for attribute in zdev.attributes:
            if attribute['endpoint'] != endpoint or attribute['cluster'] < 5:
                continue

            name = attribute.get('name')

            if name:
                if 'presence' in name:
                    return True

    def process_attr(self, name, value, attribute):
        if 'presence' in name:
            self.state = bool(value)


class ZigateGenericBinarySensorDevice(ZigateBaseDevice, Switch):

    @classmethod
    def isvalid_ep(cls, plugin, zdev, endpoint):

        actions = zdev.available_actions(endpoint).get(endpoint)
        if len(actions) > 0:
            # switch does not have any actions !
            return

        # scan the attributes
        for attribute in zdev.attributes:
            if attribute['endpoint'] != endpoint or attribute['cluster'] < 5:
                continue

            name = attribute.get('name')

            if name:
                if 'onoff' in name:
                    return True

    def process_attr(self, name, value, attribute):
        if 'onoff' in name:
            self.state = bool(value)


class ZigateGenericRelayDevice(ZigateBaseDevice, Relay):

    @classmethod
    def isvalid_ep(cls, plugin, zdev, endpoint):
        actions = zdev.available_actions(endpoint).get(endpoint)
        return zigate.ACTIONS_ONOFF in actions

    def process_attr(self, name, value, attribute):
        if name == 'onoff':
            self.state = value

    def setState(self, state):
        onoff = zigate.ON if state else zigate.OFF
        ep = self.endpoint

        res = self.z.action_onoff(self.addr, ep, onoff)

        if not res:
            # command status is bad !
            raise Exception('unable to reach the device')
