# coding: utf-8

from ..Interface import Interface
from ..reg import *
from ..Signal import ResourceSignal


class LevelChanged(ResourceSignal):
    def __init__(self, resource, new_value, old_value = None):
        super(LevelChanged, self).__init__(resource)
        self.level = new_value


@throw(LevelChanged)
@attr('level', type = Number(min=0, max=100), default = 0, mode = READ_ONLY, history = True, watch = True, description = "the level of this dimmer")
class Dimmer(Interface):

    def _watch(self, attr, new_value, old_value):
        super(Dimmer, self)._watch(attr, new_value, old_value)

        if attr == 'state':
            if new_value != old_value:
                self.dispatchSignal(LevelChanged(self, new_value, old_value))
