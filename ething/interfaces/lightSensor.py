# coding: utf-8

from ething.Interface import Interface
from ething.reg import *


@attr('light_level', type = Number(), default = 0, mode = READ_ONLY, history = True, description = "the light level measured by the sensor.")
class LightSensor(Interface):
    pass
