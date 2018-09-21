# coding: utf-8

from .sensor import Sensor, SensorValueChanged
from ..reg import *


@attr('wind_direction', type = Nullable(Number()), default = None, mode = READ_ONLY, history = True, watch = True, description = "The direction of wind (deg)")
@attr('wind_speed', type = Number(), default = 0, mode = READ_ONLY, history = True, watch = True, description = "The speed of wind (m/s)")
class Anemometer(Sensor):

    def _watch(self, attr, new_value, old_value):
        super(Anemometer, self)._watch(attr, new_value, old_value)

        if attr == 'wind_speed' or attr == 'wind_direction':
            if new_value != old_value:
                self.dispatchSignal(SensorValueChanged(self, attr, new_value, old_value))
