# coding: utf-8

from .sensor import Sensor, sensor_attr
from ..Interface import *
from .thermometer import Thermometer
from ..Device import Device


mode_type = String(allow_empty=False)

@interface
@meta(icon='mdi-home-thermometer')
@attr('target_temperature', type=Number(), mode=READ_ONLY, default=0, unit="°C", description='the target temperature.', icon="mdi-thermometer")
@attr('mode', type=mode_type, mode=READ_ONLY, description='the current mode of the climate.')
class Climate(Thermometer):

    @method.arg('mode', type=Number(), description='the target temperature')
    def set_target_temperature(self, temperature):
        """
        Set new target temperatures of the current mode
        """
        raise NotImplementedError()

    @method.arg('mode', type=mode_type, description='the mode of the climate')
    def set_mode(self, mode):
        """
        Set the climate mode
        """
        raise NotImplementedError()