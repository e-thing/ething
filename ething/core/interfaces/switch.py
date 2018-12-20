# coding: utf-8

from ..Interface import Interface
from ..reg import *
from ..rule.event import ResourceSignal, ResourceEvent


class StateChanged(ResourceSignal):
    def __init__(self, resource, state):
        super(StateChanged, self).__init__(resource)
        self.state = state


@attr('trigger_mode', type=Enum(('on', 'off', 'both')), default=None)
class StateChangedEvent(ResourceEvent):
    signal = StateChanged

    def _filter(self, signal, core, rule):
        if super(StateChangedEvent, self)._filter(signal, core, rule):

            state = signal.state
            trigger_mode = self.trigger_mode
            result = False

            if trigger_mode == 'both':
                result = True
            elif trigger_mode == 'on':
                result = bool(state) == True
            elif trigger_mode == 'off':
                result = bool(state) == False

            return result


@attr('state', type = Boolean(), default = False, mode = READ_ONLY, history = True, watch = True, description = "the state of the device")
class Switch(Interface):

    def _watch(self, attr, new_value, old_value):
        super(Switch, self)._watch(attr, new_value, old_value)

        if attr == 'state':
            if new_value != old_value:
                self.dispatchSignal(StateChanged(self, new_value))
