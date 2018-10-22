# coding: utf-8

from .MySensorsSensor import MySensorsSensor
from .helpers import *
from collections import Sequence


class MySensorsGenericSensor (MySensorsSensor):

    def _set_data(self, datatype, value):
        super(MySensorsGenericSensor, self)._set_data(datatype, value)

        name = valueTypeToName(datatype)

        dvalue = value
        if isinstance(value, Sequence):
            dvalue = ','.join(value)

        self.data[name] = dvalue

        self.store(name, value)

