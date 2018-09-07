# coding: utf-8

from ..Interface import Interface
from ..reg import *


@attr('temperature', type = Number(), default = 0, mode = READ_ONLY, history = True, description = u"the temperature of the sensor")
class Thermometer(Interface):
    pass
