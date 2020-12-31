# coding: utf-8

from .sensor import Sensor, sensor_attr
from ..Interface import *


@interface
@meta(icon='mdi-thermometer')
@sensor_attr('temperature', type=Number(), default=0, description=u"the temperature of the sensor", unit="°C",
             icon="mdi-thermometer")
class Thermometer(Sensor):
    pass
