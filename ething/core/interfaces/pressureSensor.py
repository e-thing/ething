# coding: utf-8

from .sensor import Sensor, sensor_attr
from ..Interface import *


@interface
@sensor_attr('pressure', type = Number(), default = 0, description = "the pressure measured by the sensor in Pa.")
class PressureSensor(Sensor):
    pass
