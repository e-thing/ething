# coding: utf-8


from .MihomeDevice import MihomeDevice
from ething.interfaces import Thermometer, HumiditySensor, PressureSensor


class MihomeSensorHT(MihomeDevice, Thermometer, HumiditySensor, PressureSensor):
    """
    Mihome temperature/humidity/pressure Sensor Device class.
    """

    @classmethod
    def isvalid(cls, gateway, model):
        return model in ['sensor_ht', 'weather.v1']

    def process_attr(self, name, value):

        if name == 'temperature':
            self.temperature = int(value)/100.0
        elif name == 'humidity':
            self.humidity = int(value)/100.0
        elif name == 'pressure':  # hPa
            self.pressure = int(value)

