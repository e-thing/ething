# coding: utf-8

from .sensor import Sensor, SensorValueChanged
from ..Interface import *


@interface
@attr('pressure', type = Number(), default = 0, mode = READ_ONLY, history = True, force_watch = True, description = "the pressure measured by the sensor in Pa.")
class PressureSensor(Sensor):

    def on_attr_update(self, attr, new_value, old_value):
        super(PressureSensor, self).on_attr_update(attr, new_value, old_value)

        if attr == 'pressure':
            self.dispatchSignal(SensorValueChanged(self, attr, new_value, old_value))
