# coding: utf-8

from .sensor import Sensor, SensorValueChanged
from ..Interface import *


@interface
@attr('power', type = Number(), default = 0, mode = READ_ONLY, history = True, force_watch = True, description = "the power measured by the sensor.")
class PowerMeter(Sensor):

    def on_attr_update(self, attr, new_value, old_value):
        super(PowerMeter, self).on_attr_update(attr, new_value, old_value)

        if attr == 'power':
            self.dispatchSignal(SensorValueChanged(self, attr, new_value, old_value))
