# coding: utf-8

from .sensor import Sensor, SensorValueChanged
from ..reg import *


@attr('light_level', type = Number(), default = 0, mode = READ_ONLY, history = True, force_watch = True, description = "the light level measured by the sensor.")
class LightSensor(Sensor):

    def on_attr_update(self, attr, new_value, old_value):
        super(LightSensor, self).on_attr_update(attr, new_value, old_value)

        if attr == 'light_level':
            self.dispatchSignal(SensorValueChanged(self, attr, new_value, old_value))
