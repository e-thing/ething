# coding: utf-8

from .sensor import Sensor, SensorValueChanged
from ..reg import *


@attr('humidity', type = Number(min = 0, max = 100), default = 0, mode = READ_ONLY, history = True, watch = True, description = "the humidity measured by the sensor in percent.")
class HumiditySensor(Sensor):

    def _watch(self, attr, new_value, old_value):
        super(HumiditySensor, self)._watch(attr, new_value, old_value)

        if attr == 'humidity':
            if new_value != old_value:
                self.dispatchSignal(SensorValueChanged(self, attr, new_value, old_value))
