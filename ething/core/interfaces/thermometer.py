# coding: utf-8

from .sensor import Sensor, SensorValueChanged
from ..reg import *


@attr('temperature', type = Number(), default = 0, mode = READ_ONLY, history = True, watch = True, description = u"the temperature of the sensor")
class Thermometer(Sensor):

    def _watch(self, attr, new_value, old_value):
        super(Thermometer, self)._watch(attr, new_value, old_value)

        if attr == 'temperature':
            if new_value != old_value:
                self.dispatchSignal(SensorValueChanged(self, attr, new_value, old_value))
