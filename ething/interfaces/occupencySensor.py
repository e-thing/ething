# coding: utf-8

from .sensor import Sensor, sensor_attr
from ..Interface import *
from ..Signal import ResourceSignal


class OccupencySensorOut(ResourceSignal):
    """
    is emitted each time a person go out
    """
    pass

# deprecated: moved in OccupencySensor interface
class OccupencySensorIn(ResourceSignal):
    """
    is emitted each time a person go in
    """
    pass


@interface
@throw(OccupencySensorIn, OccupencySensorOut)
@sensor_attr('presence', type=Boolean(), default=False, force_watch=False, description="True if a presence has been detected")
@meta(icon='mdi-home')
class OccupencySensor(Sensor):

    def on_attr_update(self, attr, new_value, old_value):
        super(OccupencySensor, self).on_attr_update(attr, new_value, old_value)

        if attr == 'presence' and new_value != old_value:
            if new_value:
                self.emit(OccupencySensorIn(self))
            else:
                self.emit(OccupencySensorOut(self))
