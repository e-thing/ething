# coding: utf-8

from ..Interface import Interface
from ..reg import *
from ..rule.event import ResourceSignal, ResourceEvent


class SensorValueChanged(ResourceSignal):
    def __init__(self, resource, name, new_value, old_value = None):
        super(SensorValueChanged, self).__init__(resource)
        self.name = name
        self.new_value = new_value
        self.old_value = old_value


@abstract
@attr('last_state', mode=PRIVATE, default=False)
@attr('repeat', type=Boolean(), default=False)
@attr('name', type=String(), default='', description='If the sensor emits multiple kind of value (ie: temperature, humidity ...), enter the name of the property to filter only the signal corresponding to this property.')
class SensorValueChangedEvent(ResourceEvent):
    signal = SensorValueChanged

    def _test(self, new_value, old_value):
        raise NotImplementedError()

    def _filter(self, signal, core, rule):
        if super(SensorValueChangedEvent, self)._filter(signal, core, rule):

            new_value = signal.new_value
            old_value = signal.old_value
            result = False

            try:
                result = self._test(new_value, old_value)
            except Exception:
                pass

            last_state = self._last_state
            self._last_state = result

            if result:
                if not self.repeat:
                    if last_state:
                        result = False

            return result


@attr('threshold', type=Number(), default=0)
@attr('trigger_mode', type=Enum((None, 'above threshold', 'below threshold', 'equal to')), default=None)
class NumericSensorValueChangedEvent(SensorValueChangedEvent):
    def _test(self, new_value, old_value):
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

        return result


@attr('trigger_mode', type=Enum((None, 'raising edge', 'falling edge')), default=None)
class LogicalSensorValueChangedEvent(SensorValueChangedEvent):
    def _test(self, new_value, old_value):
        trigger_mode = self.trigger_mode
        result = False

        if trigger_mode is None:
            result = True
        elif trigger_mode == 'raising edge':
            result = bool(new_value) == True and bool(old_value) == False
        elif trigger_mode == 'falling edge':
            result = bool(new_value) == False and bool(old_value) == True

        return result


@attr('pattern', type=String(), default='')
@attr('trigger_mode', type=Enum((None, 'match')), default=None)
class StringSensorValueChangedEvent(SensorValueChangedEvent):
    def _test(self, new_value, old_value):
        trigger_mode = self.trigger_mode
        result = False

        if trigger_mode is None:
            result = True
        elif trigger_mode == 'match':
            result = bool(re.search(self.pattern, new_value))

        return result


@abstract
@throw(SensorValueChanged)
class Sensor(Interface):
    pass
