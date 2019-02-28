# coding: utf-8

from .sensor import Sensor, SensorValueChanged
from ..Interface import *


@interface
@attr('moisture', type = Number(), default = 0, mode = READ_ONLY, history = True, force_watch = True, description = "the moisture level measured by this sensor.")
class MoistureSensor(Sensor):

    def on_attr_update(self, attr, new_value, old_value):
        super(MoistureSensor, self).on_attr_update(attr, new_value, old_value)

        if attr == 'moisture':
            self.dispatchSignal(SensorValueChanged(self, attr, new_value, old_value))
