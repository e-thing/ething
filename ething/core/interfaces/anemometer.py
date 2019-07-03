# coding: utf-8

from .sensor import Sensor, sensor_attr
from ..Interface import *


@interface
@meta(icon='mdi-weather-windy')
@sensor_attr('wind_direction', type = Nullable(Number(min = 0, max = 360)), default = None, description = "The direction of wind (deg)", unit="deg", icon="mdi-compass", label="wind direction")
@sensor_attr('wind_speed', type = Number(), default = 0, description = "The speed of wind (m/s)", unit="m/s", icon="mdi-weather-windy", label="wind speed")
class Anemometer(Sensor):
    pass
