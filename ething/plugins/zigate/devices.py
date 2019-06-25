# coding: utf-8
import zigate
from ething.core import Device
from ething.core.reg import *
from ething.core.interfaces import *
from colour import Color


zigate_device_classes = set()


class ZigateDeviceMetaClass(MetaReg):
    def __new__(meta, name, bases, dct):
        cls = MetaReg.__new__(meta, name, bases, dct)

        if not is_abstract(cls):
            zigate_device_classes.add(cls)

        return cls


@abstract
@attr('lqi', type=Number(), default=0, mode = READ_ONLY, description="percentage of link quality indicator")
@attr('ieee', type=String(allow_empty=False), mode = READ_ONLY, description="The ieee address of the device")
@attr('addr', type=String(), default='', mode = READ_ONLY, description="The network address of the device")
class ZigateBaseDevice(with_metaclass(ZigateDeviceMetaClass, Device)):

    @property
    def z(self):
        return self.createdBy.z

    @property
    def zdevice(self):
        return self.z.get_device_from_ieee(self.ieee)

    def process_signal(self, signal, kwargs):
        if signal == zigate.ZIGATE_DEVICE_ADDRESS_CHANGED:
            self.addr = kwargs.get('new_addr')

        device = kwargs.get('device')

        self.lqi = device.lqi_percent

        if device.info.get('power_type', 0) == 1:
            self.battery = None # plugged
        else:
            self.battery = device.battery_percent

        self.connected = True

        if signal == zigate.ZIGATE_ATTRIBUTE_UPDATED or signal == zigate.ZIGATE_ATTRIBUTE_ADDED:
            attribute = kwargs.get('attribute') # {'endpoint': 1, 'cluster': 1026, 'addr': 'abcd', 'attribute': 0, 'name': 'temperature', 'value': 13.58, 'unit': '°C', 'type': <class 'float'>, 'data': 1358}
            name = attribute.get('name')
            value = attribute.get('value')
            self.log.debug('zigate: attribute changed: %s', attribute)
            self.processAttr(name, value, attribute)

    def processAttr(self, name, value, attribute):
        pass

    @classmethod
    def create_device(cls, gateway, zigate_device_instante):
        return gateway.core.create(cls, {
            'name': cls.__name__,
            'ieee': zigate_device_instante.ieee,
            'addr': zigate_device_instante.addr,
            'lqi': zigate_device_instante.lqi_percent,
            'createdBy': gateway.id
        })

    @classmethod
    def isvalid(cls, gateway, zigate_device_instante):
        return False


class ZMihomeWeather(ZigateBaseDevice, Thermometer, HumiditySensor, PressureSensor):
    """
    Mihome temperature/humidity/pressure Sensor Device class.
    """

    @classmethod
    def isvalid(cls, gateway, zigate_device_instante):
        return zigate_device_instante.get_property_value('type') == 'lumi.weather'

    def processAttr(self, name, value, attribute):
        if name == 'temperature':
            self.temperature = value
        elif name == 'humidity':
            self.humidity = value
        elif name == 'pressure':  # mbar
            self.pressure = value * 100.


class ZMihomeSensorHT(ZigateBaseDevice, Thermometer, HumiditySensor):
    """
    Mihome temperature/humidity Sensor Device class.
    """

    @classmethod
    def isvalid(cls, gateway, zigate_device_instante):
        return zigate_device_instante.get_property_value('type') == 'lumi.sensor_ht'

    def processAttr(self, name, value, attribute):
        if name == 'temperature':
            self.temperature = value
        elif name == 'humidity':
            self.humidity = value


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


class ZDimmableLight(ZigateBaseDevice, DimmableLight):
    """
    Mihome dimmable light.
    """

    @classmethod
    def isvalid(cls, gateway, zigate_device_instante):
        return False # todo !

    def setLevel(self, level):
        if not self.zdevice.action_move_level_onoff(zigate.ON if level > 0 else zigate.OFF, level):
            # command status is bad !
            raise Exception('unable to reach the device')

    def processAttr(self, name, value, attribute):
        if name == 'onoff':
            self.state = value
        elif name == 'current_level':
            self.level = value


class ZRGBWLight(ZigateBaseDevice, RGBWLight):
    """
    Mihome color light.
    """

    @classmethod
    def isvalid(cls, gateway, zigate_device_instante):
        return False # todo !

    def setLevel(self, level):
        if not self.zdevice.action_move_level_onoff(zigate.ON if level > 0 else zigate.OFF, level):
            # command status is bad !
            raise Exception('unable to reach the device')

    def setColor(self, color):
        if not self.zdevice.action_move_hue_hex(color):
            # command status is bad !
            raise Exception('unable to reach the device')

        # or depending of the device
        #if not self.zdevice.action_move_colour_hex(color):
        #    # command status is bad !
        #    raise Exception('unable to reach the device')


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
