# coding: utf-8

from .sensor import Sensor, SensorValueChanged
from ..reg import *


@attr('light_level', type = Number(), default = 0, mode = READ_ONLY, history = True, watch = True, description = "the light level measured by the sensor.")
class LightSensor(Sensor):

    def _watch(self, attr, new_value, old_value):
        super(LightSensor, self)._watch(attr, new_value, old_value)

        if attr == 'light_level':
            if new_value != old_value:
                self.dispatchSignal(SensorValueChanged(self, attr, new_value, old_value))