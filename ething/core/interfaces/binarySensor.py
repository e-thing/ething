# coding: utf-8

from .sensor import Sensor, sensor_attr
from ..Interface import *


@interface
@sensor_attr('state', type = Boolean(), default = False, force_watch = False)
class BinarySensor(Sensor):
    pass
