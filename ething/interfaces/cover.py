# coding: utf-8

from .sensor import Sensor, sensor_attr
from ..Interface import *
from ..Device import Device


@interface
@meta(icon='mdi-window-closed')
@attr('position', type=Number(min=0, max=100), mode=READ_ONLY, default=100, unit="%", description='the position of the cover in percent. If the value is 0, the cover is closed.')
class Cover(Device):

    @method
    def open_cover(self):
        """
        open the cover
        """
        raise NotImplementedError()

    @method
    def close_cover(self):
        """
        close the cover
        """
        raise NotImplementedError()

    @method
    def stop_cover(self):
        """
        stop the cover
        """
        raise NotImplementedError()
