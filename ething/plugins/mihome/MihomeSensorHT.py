# coding: utf-8


from .MihomeDevice import MihomeDevice
from ething.core.interfaces import Thermometer, HumiditySensor, PressureSensor


class MihomeSensorHT(MihomeDevice, Thermometer, HumiditySensor, PressureSensor):
    """
    Mihome temperature/humidity/pressure Sensor Device class.
    """

    def processAttr(self, name, value):

        if name == 'temperature':
            self._temperature = int(value)/100.0
        elif name == 'humidity':
            self._humidity = int(value)/100.0
        elif name == 'pressure':  # hPa
            self._pressure = int(value)

