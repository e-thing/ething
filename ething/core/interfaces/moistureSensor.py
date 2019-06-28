# coding: utf-8

from .sensor import Sensor, sensor_attr
from ..Interface import *


@interface
@sensor_attr('moisture', type = Number(), default = 0, description = "the moisture level measured by this sensor.")
class MoistureSensor(Sensor):
    pass
