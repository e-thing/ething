# coding: utf-8

from .sensor import Sensor, SensorValueChanged
from ..reg import *


@attr('state', type = Boolean(), default = False, mode = READ_ONLY, history = True, watch = True, description = u"the state of the door. True if open.")
class DoorSensor(Sensor):

    def _watch(self, attr, new_value, old_value):
        super(DoorSensor, self)._watch(attr, new_value, old_value)

        if attr == 'state':
            if new_value != old_value:
                self.dispatchSignal(SensorValueChanged(self, attr, new_value, old_value))
