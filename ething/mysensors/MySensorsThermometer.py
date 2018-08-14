# coding: utf-8

from .MySensorsSensor import MySensorsSensor
from ething.interfaces import Thermometer
from .helpers import *


class MySensorsThermometer (MySensorsSensor, Thermometer):

    def _set_data(self, datatype, value):
        super(MySensorsThermometer, self)._set_data(datatype, value)
        if datatype == V_TEMP:
            self._temperature = value
