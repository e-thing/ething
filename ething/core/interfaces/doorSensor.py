# coding: utf-8

from .sensor import Sensor, sensor_attr
from ..Interface import *


@interface
@sensor_attr('state', type = Boolean(), default = False, force_watch = False, description = u"the state of the door. True if open.")
class DoorSensor(Sensor):
    pass
