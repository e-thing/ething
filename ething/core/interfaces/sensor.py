# coding: utf-8

from ..Device import Device
from ..Interface import *
from ..Signal import ResourceSignal


class SensorValueChanged(ResourceSignal):
    def __init__(self, resource, name, new_value, old_value = None):
        super(SensorValueChanged, self).__init__(resource)
        self.payload = {}
        self.payload[name] = new_value
        if old_value is not None:
            self.payload[name+'_old'] = old_value


@interface
@throw(SensorValueChanged)
class Sensor(Device):
    pass
