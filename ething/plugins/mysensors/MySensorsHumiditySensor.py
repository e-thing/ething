# coding: utf-8

from .MySensorsSensor import MySensorsSensor
from ething.core.interfaces import HumiditySensor
from .helpers import *


class MySensorsHumiditySensor (MySensorsSensor, HumiditySensor):

    def _set_data(self, datatype, value):
        super(MySensorsHumiditySensor, self)._set_data(datatype, value)
        if datatype == V_HUM:
            self.humidity = value
