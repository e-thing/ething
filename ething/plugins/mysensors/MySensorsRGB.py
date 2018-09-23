# coding: utf-8

from .MySensorsSensor import MySensorsSensor
from ething.core.interfaces import RGBLight
from .helpers import *


class MySensorsRGB (MySensorsSensor, RGBLight):

    def _set_data(self, datatype, value):
        super(MySensorsRGB, self)._set_data(datatype, value)
        if datatype == V_RGB:
            self._color = value
        elif datatype == V_STATUS:
            self._state = value

    def setState(self, state):
        self.send(SET, V_STATUS, state, done=lambda _: setattr(self, '_state', state))

    def setColor(self, color):
        self.send(SET, V_RGB, color, done=lambda _: setattr(self, '_color', color))
