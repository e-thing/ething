# coding: utf-8

from .sensor import Sensor, sensor_attr
from ..Interface import *


@interface
@meta(icon='mdi-water-percent')
@sensor_attr('moisture', type = Number(min = 0, max = 100), default = 0, description = "the moisture level measured by this sensor.")
class MoistureSensor(Sensor):
    pass
