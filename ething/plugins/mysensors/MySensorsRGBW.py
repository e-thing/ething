# coding: utf-8

from .MySensorsSensor import MySensorsSensor
from ething.core.interfaces import RGBWLight
from .helpers import *


class MySensorsRGBW (MySensorsSensor, RGBWLight):

    def _set_data(self, datatype, value):
        super(MySensorsRGBW, self)._set(datatype, value)
        if datatype == V_RGB:
            self._color = value
        elif datatype == V_RGBW:
            color, level = value
            self._color = color
            self._level = level
        elif datatype == V_STATUS:
            self._state = value
        elif datatype == V_PERCENTAGE or datatype == V_DIMMER:
            self._level = value

    def setState(self, state):
        self.send(SET, V_STATUS, state, done = lambda _: setattr(self, '_state', state))

    def setColor(self, color):
        self.send(SET, V_RGBW, (color, self.level), done = lambda _: setattr(self, '_color', color))

    def setLevel(self, level):
        self.send(SET, V_RGBW, (self.color, level), done=lambda _: setattr(self, '_level', level))