# coding: utf-8

from .sensor import Sensor, sensor_attr
from ..Interface import *


@interface
@meta(icon='mdi-power-socket-eu')
@sensor_attr('power', type = Number(), default = 0, description = "the power measured by the sensor.")
class PowerMeter(Sensor):
    pass
