# coding: utf-8

from ..Device import Device
from ..Interface import *
from ..Signal import ResourceSignal


class SensorValueChanged(ResourceSignal):
    def __init__(self, resource, name, value):
        data = dict()
        data[name] = value
        super(SensorValueChanged, self).__init__(resource, **data)


def schema_mod(attr, schema):
    schema['sensor'] = True
    schema['history'] = attr.get('history')


def sensor_attr(*args, **kwargs):
    if 'type' not in kwargs:
        kwargs['type'] = Scalar()
        kwargs.setdefault('default', None)

    kwargs.setdefault('unit', None)
    kwargs.setdefault('history', True)
    kwargs.setdefault('force_watch', True)
    kwargs.setdefault('mode', READ_ONLY)
    kwargs.setdefault('schema_mod', schema_mod)

    kwargs['sensor'] = True
    return attr(*args, **kwargs)


@interface
@throw(SensorValueChanged)
@meta(icon='mdi-access-point')
class Sensor(Device):

    def __init__(self, data=None, context=None):
        super(Sensor, self).__init__(data, context)

        # list sensor attributes
        self._sensor_attributes_names = [a.name for a in list_registered_attr(self) if a.get('sensor')]

    def on_attr_update(self, attr, new_value, old_value):
        super(Sensor, self).on_attr_update(attr, new_value, old_value)

        if attr in self._sensor_attributes_names:
            self.emit(SensorValueChanged(self, attr, new_value))
