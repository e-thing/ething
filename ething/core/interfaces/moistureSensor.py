# coding: utf-8

from .sensor import Sensor, SensorValueChanged
from ..reg import *


@attr('moisture', type = Number(), default = 0, mode = READ_ONLY, history = True, watch = True, description = "the moisture level measured by this sensor.")
class MoistureSensor(Sensor):

    def _watch(self, attr, new_value, old_value):
        super(MoistureSensor, self)._watch(attr, new_value, old_value)

        if attr == 'moisture':
            if new_value != old_value:
                self.dispatchSignal(SensorValueChanged(self, attr, new_value, old_value))
