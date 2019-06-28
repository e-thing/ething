# coding: utf-8

from .sensor import Sensor, sensor_attr
from ..Interface import *


@interface
@sensor_attr('wind_direction', type = Nullable(Number()), default = None, description = "The direction of wind (deg)")
@sensor_attr('wind_speed', type = Number(), default = 0, description = "The speed of wind (m/s)")
class Anemometer(Sensor):
    pass
