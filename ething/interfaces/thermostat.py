# coding: utf-8

from .sensor import Sensor, sensor_attr
from ..Interface import *
from .thermometer import Thermometer
from ..Device import Device


@interface
@meta(icon='mdi-thermostat')
@attr('target_temperature', type=Number(), mode=READ_ONLY, default=0, unit="°C", description='the target temperature.',
      icon="mdi-thermometer")
class Thermostat(Device):

    @method.arg('temperature', type=Number(), description='the target temperature')
    def set_target_temperature(self, temperature):
        """
        Set new target temperatures of the current mode
        """
        self.target_temperature = temperature
