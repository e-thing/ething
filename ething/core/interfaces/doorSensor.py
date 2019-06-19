# coding: utf-8

from .sensor import Sensor, SensorValueChanged
from ..Interface import *


@interface
@attr('state', type = Boolean(), default = False, mode = READ_ONLY, history = True, force_watch = False, description = u"the state of the door. True if open.")
class DoorSensor(Sensor):

    def on_attr_update(self, attr, new_value, old_value):
        super(DoorSensor, self).on_attr_update(attr, new_value, old_value)

        if attr == 'state':
            self.dispatchSignal(SensorValueChanged(self, attr, new_value, old_value))
