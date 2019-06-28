# coding: utf-8

from .sensor import Sensor, sensor_attr
from ..Interface import *


@interface
@sensor_attr('temperature', type = Number(), default = 0, description = u"the temperature of the sensor")
class Thermometer(Sensor):
    pass
