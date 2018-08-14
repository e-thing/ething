# coding: utf-8

from ething.Interface import Interface
from ething.reg import *


@attr('moisture', type = Number(), default = 0, mode = READ_ONLY, history = True, description = "the moisture level measured by this sensor.")
class MoistureSensor(Interface):
    pass
