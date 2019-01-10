# coding: utf-8

from ..Interface import Interface
from ..reg import *
from ..rule.event import ResourceSignal, ResourceEvent, ResourceFilter


class LevelChanged(ResourceSignal):
    def __init__(self, resource, new_value, old_value = None):
        super(LevelChanged, self).__init__(resource)
        self.new_value = new_value
        self.old_value = old_value


@attr('last_state', mode=PRIVATE, default=False)
@attr('repeat', type=Boolean(), default=False)
@attr('threshold', type=Number(), default=0)
@attr('trigger_mode', type=Enum((None, 'above threshold', 'below threshold', 'equal to')), default=None)
@attr('resource', type=ResourceFilter(must_throw=LevelChanged))
class LevelChangedEvent(ResourceEvent):
    signal = LevelChanged

    def _filter(self, signal, core):
        if super(LevelChangedEvent, self)._filter(signal, core):

            new_value = signal.new_value
            old_value = signal.old_value
            trigger_mode = self.trigger_mode
            threshold = self.threshold
            result = False

            if trigger_mode is None:
                result = True
            elif trigger_mode == 'above threshold':
                result = new_value >= threshold and old_value < threshold
            elif trigger_mode == 'below threshold':
                result = new_value <= threshold and old_value > threshold
            elif trigger_mode == 'equal to':
                result = new_value == threshold

            last_state = self.last_state
            self.last_state = result

            if result:
                if not self.repeat:
                    if last_state:
                        result = False

            return result


@attr('level', type = Number(min=0, max=100), default = 0, mode = READ_ONLY, history = True, watch = True, description = "the level of this dimmer")
class Dimmer(Interface):

    def _watch(self, attr, new_value, old_value):
        super(Dimmer, self)._watch(attr, new_value, old_value)

        if attr == 'state':
            if new_value != old_value:
                self.dispatchSignal(LevelChanged(self, new_value, old_value))
