# coding: utf-8

from ..Interface import Interface
from ..reg import *
from .sensor import Sensor, SensorValueChanged


@attr('state', type = Boolean(), default = False, mode = READ_ONLY, history = True, watch = True, description = "the state of the device")
class Switch(Interface):

    def _watch(self, attr, new_value, old_value):
        super(Switch, self)._watch(attr, new_value, old_value)

        if attr == 'state':
            if new_value != old_value:
                self.dispatchSignal(SensorValueChanged(self, attr, new_value, old_value))
