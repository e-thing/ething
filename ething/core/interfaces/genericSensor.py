# coding: utf-8

from .sensor import Sensor, sensor_attr
from ..Interface import *


@interface
@sensor_attr('value', type = Scalar(), default = None)
class GenericSensor(Sensor):
    pass
