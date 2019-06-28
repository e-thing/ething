# coding: utf-8

from .sensor import Sensor, SensorValueChanged
from ..Interface import *


@interface
@attr('presence', type = Boolean(), default = False, mode = READ_ONLY, history = True, force_watch = False, description = "True if a presence has been detected")
class OccupencySensor(Sensor):

    def on_attr_update(self, attr, new_value, old_value):
        super(OccupencySensor, self).on_attr_update(attr, new_value, old_value)

        if attr == 'presence':
            self.dispatchSignal(SensorValueChanged(self, attr, new_value, old_value))
