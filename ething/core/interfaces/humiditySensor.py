# coding: utf-8

from .sensor import Sensor, sensor_attr
from ..Interface import *


@interface
@sensor_attr('humidity', type = Number(min = 0, max = 100), default = 0, description = "the humidity measured by the sensor in percent.", unit="%", icon="mdi-water-percent")
class HumiditySensor(Sensor):
    pass
