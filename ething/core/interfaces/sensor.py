# coding: utf-8

from ..Interface import Interface
from ..reg import *
from ..Signal import ResourceSignal


class SensorValueChanged(ResourceSignal):
    def __init__(self, resource, name, new_value, old_value = None):
        super(SensorValueChanged, self).__init__(resource)
        self.payload = {}
        self.payload[name] = new_value
        if old_value is not None:
            self.payload[name+'_old'] = old_value


@abstract
@throw(SensorValueChanged)
class Sensor(Interface):
    pass
