# coding: utf-8

from ..Device import Device
from ..Interface import *
from .sensor import SensorValueChanged


@interface
@throw(SensorValueChanged)
@attr('state', type = Boolean(), default = False, mode = READ_ONLY, history = True, force_watch = True, description = "the state of the device")
class Switch(Device):

    def on_attr_update(self, attr, new_value, old_value):
        super(Switch, self).on_attr_update(attr, new_value, old_value)

        if attr == 'state':
            self.dispatchSignal(SensorValueChanged(self, attr, new_value, old_value))
