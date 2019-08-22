# coding: utf-8

from .sensor import Sensor, sensor_attr
from ..Interface import *


@interface
@sensor_attr('presence', type = Boolean(), default = False, force_watch = False, description = "True if a presence has been detected")
class OccupencySensor(Sensor):
    pass
