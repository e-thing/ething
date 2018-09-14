# coding: utf-8

from .sensor import Sensor, SensorValueChanged
from ..reg import *


@attr('pressure', type = Number(), default = 0, mode = READ_ONLY, history = True, watch = True, description = "the pressure measured by the sensor in Pa.")
class PressureSensor(Sensor):

    def _watch(self, attr, new_value, old_value):
        super(PressureSensor, self)._watch(attr, new_value, old_value)

        if attr == 'pressure':
            if new_value != old_value:
                self.dispatchSignal(SensorValueChanged(self, attr, new_value, old_value))
