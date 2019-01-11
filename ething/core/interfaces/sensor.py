# coding: utf-8

from ..Interface import Interface
from ..reg import *
from ..Signal import ResourceSignal


class SensorValueChanged(ResourceSignal):
    def __init__(self, resource, name, new_value, old_value = None):
        super(SensorValueChanged, self).__init__(resource)
        setattr(self, name, new_value)


@abstract
@throw(SensorValueChanged)
class Sensor(Interface):
    pass
