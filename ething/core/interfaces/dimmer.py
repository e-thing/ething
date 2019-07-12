# coding: utf-8

from ..Interface import *
from ..Device import Device
from ..Signal import ResourceSignal


class LevelChanged(ResourceSignal):
    def __init__(self, resource, new_value, old_value = None):
        super(LevelChanged, self).__init__(resource)
        self.payload = {
            'level': new_value
        }
        if old_value is not None:
            self.payload['level_old'] = old_value


@throw(LevelChanged)
@interface
@meta(icon='mdi-contrast-circle')
@attr('level', type = Range(0, 100), default = 0, mode = READ_ONLY, history = True, force_watch = True, description = "the level of this dimmer")
class Dimmer(Device):

    def on_attr_update(self, attr, new_value, old_value):
        super(Dimmer, self).on_attr_update(attr, new_value, old_value)

        if attr == 'level':
            self.dispatchSignal(LevelChanged(self, new_value, old_value))
