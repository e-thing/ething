# coding: utf-8

from ething.Interface import Interface
from ething.reg import *


@attr('pressure', type = Number(), default = 0, mode = READ_ONLY, history = True, description = "the pressure measured by the sensor in Pa.")
class PressureSensor(Interface):
    pass
