# coding: utf-8

from ..Interface import Interface
from ..reg import *


@attr('humidity', type = Number(min = 0, max = 100), default = 0, mode = READ_ONLY, history = True, description = "the humidity measured by the sensor in percent.")
class HumiditySensor(Interface):
    pass
