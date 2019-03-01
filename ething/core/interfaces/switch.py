# coding: utf-8

from ..Device import Device
from ..Interface import *
from ..Signal import ResourceSignal


class StateChanged(ResourceSignal):
    def __init__(self, resource, new_value, old_value = None):
        super(StateChanged, self).__init__(resource)
        self.payload = {
            'state': new_value
        }
        if old_value is not None:
            self.payload['state_old'] = old_value


@interface
@throw(StateChanged)
@attr('state', type = Boolean(), default = False, mode = READ_ONLY, history = True, force_watch = True, description = "the state of the device")
class Switch(Device):

    def on_attr_update(self, attr, new_value, old_value):
        super(Switch, self).on_attr_update(attr, new_value, old_value)

        if attr == 'state':
            self.dispatchSignal(StateChanged(self, new_value, old_value))
