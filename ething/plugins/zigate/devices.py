# coding: utf-8
import zigate
from ething.core import Device
from ething.core.reg import *
from ething.core.interfaces import Thermometer, HumiditySensor, PressureSensor


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


class ZMihomeSensorHT(ZigateBaseDevice, Thermometer, HumiditySensor, PressureSensor):
    """
    Mihome temperature/humidity/pressure Sensor Device class.
    """

    @classmethod
    def isvalid(cls, gateway, zigate_device_instante):
        return zigate_device_instante.get_property_value('type') == 'lumi.weather'

    def process_signal(self, signal, kwargs):

        super(ZMihomeSensorHT, self).process_signal(signal, kwargs)

        if signal == zigate.ZIGATE_ATTRIBUTE_UPDATED or signal == zigate.ZIGATE_ATTRIBUTE_ADDED:
            attribute = kwargs.get('attribute')
            name = attribute.get('name')
            value = attribute.get('value')

            if name == 'temperature':
                self.temperature = value
            elif name == 'humidity':
                self.humidity = value
            elif name == 'pressure':  # mbar
                self.pressure = value * 100.
            elif name == 'battery': # volt
                self.battery = min(100. * value / 3.3, 100)

