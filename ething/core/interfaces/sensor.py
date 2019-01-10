# coding: utf-8

from ..Interface import Interface
from ..reg import *
from ..rule.event import ResourceSignal, ResourceEvent, ResourceFilter


class SensorValueChanged(ResourceSignal):
    def __init__(self, resource, name, new_value, old_value = None):
        super(SensorValueChanged, self).__init__(resource)
        setattr(self, name, new_value)


@attr('name', type=String(), default='', description='If the sensor emits multiple kind of value (ie: temperature, humidity ...), enter the name of the property to filter only the signal corresponding to this property.')
@attr('resource', type=ResourceFilter(must_throw=SensorValueChanged))
class SensorValueChangedEvent(ResourceEvent):
    signal = SensorValueChanged

    def _test(self, new_value, old_value):
        raise NotImplementedError()

    def _filter(self, signal, core):
        if super(SensorValueChangedEvent, self)._filter(signal, core):

            if self.name:
                return hasattr(signal, self.name)

            return True


@abstract
@throw(SensorValueChanged)
class Sensor(Interface):
    pass
