# coding: utf-8

from .sensor import Sensor, sensor_attr
from ..Interface import *


@interface
@sensor_attr('light_level', type = Number(), default = 0, description = "the light level measured by the sensor.")
class LightSensor(Sensor):
    pass
