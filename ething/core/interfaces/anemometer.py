# coding: utf-8

from .sensor import Sensor, SensorValueChanged
from ..Interface import *


@interface
@attr('wind_direction', type = Nullable(Number()), default = None, mode = READ_ONLY, history = True, force_watch = True, description = "The direction of wind (deg)")
@attr('wind_speed', type = Number(), default = 0, mode = READ_ONLY, history = True, force_watch = True, description = "The speed of wind (m/s)")
class Anemometer(Sensor):

    def on_attr_update(self, attr, new_value, old_value):
        super(Anemometer, self).on_attr_update(attr, new_value, old_value)

        if attr == 'wind_speed' or attr == 'wind_direction':
            self.dispatchSignal(SensorValueChanged(self, attr, new_value, old_value))
