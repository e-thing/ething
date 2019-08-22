# coding: utf-8

from .sensor import Sensor, sensor_attr
from ..Interface import *


@interface
@meta(icon='mdi-brightness-6')
@sensor_attr('light_level', type = Number(), default = 0, description = "the light level measured by the sensor.", icon="mdi-brightness-6", unit='lux', label="light level")
class LightSensor(Sensor):
    pass
