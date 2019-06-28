# coding: utf-8
import zigate
from ething.core import Device
from ething.core.reg import *
from ething.core.interfaces import *
from colour import Color


zigate_device_classes = list()


class ZigateDeviceMetaClass(MetaReg):
    def __new__(meta, name, bases, dct):
        cls = MetaReg.__new__(meta, name, bases, dct)

        if getattr(cls, '_REGISTER_', True) is not False and (hasattr(cls, 'isvalid') or hasattr(cls, 'isvalid_ep')):
            zigate_device_classes.append(cls)

        return cls


@abstract
@meta(icon='mdi-alpha-z-box')
@attr('lqi', type=Number(), default=0, mode = READ_ONLY, description="percentage of link quality indicator")
@attr('endpoint', type=Nullable(Integer()), mode = READ_ONLY, description="If set, this device is only bind to a single endpoint")
@attr('ieee', type=String(allow_empty=False), mode = READ_ONLY, description="The ieee address of the device")
@attr('addr', type=String(), default='', mode = READ_ONLY, description="The network address of the device")
@attr('typename', type=String(), default='', mode = READ_ONLY, description="The type name of the device")
@attr('manufacturer', type=String(), default='', mode = READ_ONLY, description="The manufacturer of the device")
class ZigateBaseDevice(with_metaclass(ZigateDeviceMetaClass, Device)):

    @property
    def z(self):
        return self.createdBy.z

    @property
    def zdevice(self):
        return self.z.get_device_from_ieee(self.ieee)

    def process_signal(self, signal, kwargs):
        zdevice = kwargs.get('device')

        if signal == zigate.ZIGATE_DEVICE_ADDRESS_CHANGED:
            self.addr = kwargs.get('new_addr')
        elif signal == zigate.ZIGATE_DEVICE_NEED_DISCOVERY:
            self.error = 'need discovery'
        elif signal == zigate.ZIGATE_DEVICE_ADDED:
            self.typename = zdevice.get_property_value('type', '')
            self.manufacturer = zdevice.get_property_value('manufacturer', '')

        self.lqi = zdevice.lqi_percent

        if zdevice.info.get('power_type', 0) == 1:
            self.battery = None # plugged
        else:
            self.battery = zdevice.battery_percent

        connected = not zdevice.missing
        if connected != self.connected:
            self.connected = connected

        if signal == zigate.ZIGATE_ATTRIBUTE_UPDATED or signal == zigate.ZIGATE_ATTRIBUTE_ADDED:
            attribute = kwargs.get('attribute') # {'endpoint': 1, 'cluster': 1026, 'addr': 'abcd', 'attribute': 0, 'name': 'temperature', 'value': 13.58, 'unit': '°C', 'type': <class 'float'>, 'data': 1358}
            ep = attribute.get('endpoint')
            if self.endpoint is None or self.endpoint == ep:
                name = attribute.get('name')
                value = attribute.get('value')
                self.processAttr(name, value, attribute)

    def processAttr(self, name, value, attribute):
        pass

    @classmethod
    def create_device(cls, gateway, zigate_device_instante, endpoint=None, **kwargs):
        name = zigate_device_instante.get_property_value('type', cls.__name__)
        if endpoint is not None:
            name = '%s %d' % (name, endpoint)

        attrs = {
            'name': name,
            'ieee': zigate_device_instante.ieee,
            'addr': zigate_device_instante.addr,
            'lqi': zigate_device_instante.lqi_percent,
            'endpoint': endpoint,
            'createdBy': gateway.id
        }

        attrs.update(kwargs)

        return gateway.core.create(cls, attrs)


# class ZMihomeWeather(ZigateBaseDevice, Thermometer, HumiditySensor, PressureSensor):
#     """
#     Mihome temperature/humidity/pressure Sensor Device class.
#     """
#
#     @classmethod
#     def isvalid(cls, gateway, zigate_device_instante):
#         return zigate_device_instante.get_property_value('type') == 'lumi.weather'
#
#     def processAttr(self, name, value, attribute):
#         if name == 'temperature':
#             self.temperature = value
#         elif name == 'humidity':
#             self.humidity = value
#         elif name == 'pressure':  # mbar
#             self.pressure = value * 100.


# class ZMihomeSensorHT(ZigateBaseDevice, Thermometer, HumiditySensor):
#     """
#     Mihome temperature/humidity Sensor Device class.
#     """
#
#     @classmethod
#     def isvalid(cls, gateway, zigate_device_instante):
#         return zigate_device_instante.get_property_value('type') == 'lumi.sensor_ht'
#
#     def processAttr(self, name, value, attribute):
#         if name == 'temperature':
#             self.temperature = value
#         elif name == 'humidity':
#             self.humidity = value


class ZMihomeMagnet(ZigateBaseDevice, DoorSensor):
    """
    Mihome door Sensor.
    """

    @classmethod
    def isvalid(cls, gateway, zigate_device_instante):
        return zigate_device_instante.get_property_value('type') in ['lumi.sensor_magnet', 'lumi.sensor_magnet.aq2']

    def processAttr(self, name, value, attribute):
        if name == 'onoff':
            self.state = value


class ZMihomeSwitch(ZigateBaseDevice, Switch):
    """
    Mihome button.
    """

    @classmethod
    def isvalid(cls, gateway, zigate_device_instante):
        return zigate_device_instante.get_property_value('type') in ['lumi.ctrl_ln1', 'lumi.sensor_86sw1']

    def processAttr(self, name, value, attribute):
        if name == 'onoff':
            self.state = value


class ZMihomeButton(ZigateBaseDevice, Button):
    """
    Mihome button.
    """

    @classmethod
    def isvalid(cls, gateway, zigate_device_instante):
        return zigate_device_instante.get_property_value('type') in ['lumi.sensor_switch', 'lumi.sensor_switch.aq2', 'lumi.sensor_switch.aq3', 'lumi.remote.b1acn01', 'lumi.remote.b286acn01']

    def processAttr(self, name, value, attribute):
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

class ZigateGenericLightDevice(ZigateBaseDevice, Light):

    @classmethod
    def isvalid_ep(cls, gateway, zdev, endpoint):
        device_id = zdev.endpoints[endpoint].get('device', 0xffff)
        in_clusters = zdev.endpoints[endpoint].get('in_clusters', [])
        # 0x0100: ON/OFF Light
        # 0x0006: 'General: On/Off'
        return device_id == 0x0100 and 0x0006 in in_clusters

    def processAttr(self, name, value, attribute):
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

class ZigateGenericDimmableLightDevice(ZigateBaseDevice, DimmableLight):

    @classmethod
    def isvalid_ep(cls, gateway, zdev, endpoint):
        device_id = zdev.endpoints[endpoint].get('device', 0xffff)
        # 0x0101: Dimmable Light
        return device_id == 0x0101

    def processAttr(self, name, value, attribute):
        if name == 'onoff':
            self.state = value
        elif name == 'current_level':
            self.level = value

    def setLevel(self, level):
        onoff = zigate.ON if level > 0 else zigate.OFF
        ep = self.endpoint

        if ep is None:
            res = self.zdevice.action_move_level_onoff(onoff, level)
        else:
            res = self.z.action_move_level_onoff(self.addr, ep, onoff, level)

        if not res:
            # command status is bad !
            raise Exception('unable to reach the device')

class ZigateGenericColourDimmableLightDevice(ZigateBaseDevice, RGBWLight):

    @classmethod
    def isvalid_ep(cls, gateway, zdev, endpoint):
        device_id = zdev.endpoints[endpoint].get('device', 0xffff)
        # 0x0102: Colour Dimmable Light
        return device_id == 0x0102

    def processAttr(self, name, value, attribute):
        if name == 'onoff':
            self.state = value
        elif name == 'current_level':
            self.level = value
        elif name == 'current_hue':
            c = Color(self.color)
            c.set_hue(value / 360.)
            self.color = c.get_hex_l()
        elif name == 'current_saturation':
            c = Color(self.color)
            c.set_saturation(value / 100.)
            self.color = c.get_hex_l()

    def setLevel(self, level):
        onoff = zigate.ON if level > 0 else zigate.OFF
        ep = self.endpoint

        if ep is None:
            res = self.zdevice.action_move_level_onoff(onoff, level)
        else:
            res = self.z.action_move_level_onoff(self.addr, ep, onoff, level)

        if not res:
            # command status is bad !
            raise Exception('unable to reach the device')

    def setColor(self, color):
        ep = self.endpoint

        if ep is None:
            res = self.zdevice.action_move_hue_hex(color)
        else:
            res = self.z.action_move_hue_hex(self.addr, ep, color)

        if not res:
            # command status is bad !
            raise Exception('unable to reach the device')

class ZigateGenericRelayDevice(ZigateBaseDevice, Relay):

    @classmethod
    def isvalid_ep(cls, gateway, zdev, endpoint):
        device_id = zdev.endpoints[endpoint].get('device', 0xffff)
        in_clusters = zdev.endpoints[endpoint].get('in_clusters', [])
        # 0x0002: ON/OFF Output
        # 0x0006: 'General: On/Off'
        return device_id == 0x0002 and 0x0006 in in_clusters

    def processAttr(self, name, value, attribute):
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

class ZigateGenericSwitchDevice(ZigateBaseDevice, Switch):

    @classmethod
    def isvalid_ep(cls, gateway, zdev, endpoint):
        device_id = zdev.endpoints[endpoint].get('device', 0xffff)
        in_clusters = zdev.endpoints[endpoint].get('in_clusters', [])
        # 0x0000: ON/OFF Switch
        # 0x0103: ON/OFF Light Switch
        # 0x0006: 'General: On/Off'
        return (device_id == 0x0 or device_id == 0x0103) and 0x0006 in in_clusters

    def processAttr(self, name, value, attribute):
        if name == 'onoff':
            self.state = value

class ZigateGenericDimmerDevice(ZigateBaseDevice, Dimmer):

    @classmethod
    def isvalid_ep(cls, gateway, zdev, endpoint):
        device_id = zdev.endpoints[endpoint].get('device', 0xffff)
        # 0x0104: Dimmer Switch
        return device_id == 0x0104

    def processAttr(self, name, value, attribute):
        if name == 'onoff':
            self.level = 100 if value else 0
        elif name == 'current_level':
            self.level = value

class ZigateGenericSmartPlugDevice(ZigateGenericRelayDevice):

    @classmethod
    def isvalid_ep(cls, gateway, zdev, endpoint):
        device_id = zdev.endpoints[endpoint].get('device', 0xffff)
        # 0x0051: Smart Plug
        return device_id ==  0x0051

@dynamic
@meta(icon='mdi-access-point')
class ZigateGenericSensorDevice(ZigateBaseDevice):

    @classmethod
    def isvalid_ep(cls, gateway, zdev, endpoint):
        in_clusters = zdev.endpoints[endpoint].get('in_clusters', [])
        # guess by cluster id
        # 0x0402: 'Measurement: Temperature'
        # 0x0403: 'Measurement: Atmospheric Pressure'
        # 0x0405: 'Measurement: Humidity'

        interfaces = []
        if 0x0400 in in_clusters:
            interfaces.append(LightSensor)
        if 0x0402 in in_clusters:
            interfaces.append(Thermometer)
        if 0x0403 in in_clusters:
            interfaces.append(PressureSensor)
        if 0x0405 in in_clusters:
            interfaces.append(HumiditySensor)
        if 0x0406 in in_clusters:
            interfaces.append(OccupencySensor)

        if interfaces:
            return create_dynamic_class(cls, *interfaces)

    def processAttr(self, name, value, attribute):
        if name == 'temperature' and self.isTypeof(Thermometer):
            self.temperature = value
        elif name == 'humidity' and self.isTypeof(PressureSensor):
            self.humidity = value
        elif name == 'pressure' and self.isTypeof(HumiditySensor):  # mbar
            self.pressure = value * 100.
        elif name == 'luminosity' and self.isTypeof(LightSensor):  # lm
            self.light_level = value
        elif name == 'presence' and self.isTypeof(OccupencySensor):
            self.presence = value
