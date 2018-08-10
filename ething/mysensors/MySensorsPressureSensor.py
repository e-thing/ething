# coding: utf-8

from .MySensorsSensor import MySensorsSensor
from ething.interfaces import PressureSensor
from .helpers import *


class MySensorsPressureSensor (MySensorsSensor, PressureSensor):

    def _set(self, datatype, value):
        super(MySensorsPressureSensor, self)._set(datatype, value)
        if datatype == V_PRESSURE:
            self._pressure = value
