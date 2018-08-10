# coding: utf-8

from ething.Interface import Interface
from ething.reg import *


@attr('temperature', type = Number(), default = 0, mode = READ_ONLY, history = True, description = "the temperature of the sensor")
class Thermometer(Interface):
    pass
