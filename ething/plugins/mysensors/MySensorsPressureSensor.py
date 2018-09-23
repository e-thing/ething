# coding: utf-8

from .MySensorsSensor import MySensorsSensor
from ething.core.interfaces import PressureSensor
from .helpers import *


class MySensorsPressureSensor (MySensorsSensor, PressureSensor):

    def _set_data(self, datatype, value):
        super(MySensorsPressureSensor, self)._set_data(datatype, value)
        if datatype == V_PRESSURE:
            self._pressure = value
