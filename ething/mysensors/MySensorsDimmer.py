# coding: utf-8

from .MySensorsSensor import MySensorsSensor
from ething.interfaces import DimmableSwitch
from .helpers import *


class MySensorsDimmer (MySensorsSensor, DimmableSwitch):

    def _set(self, datatype, value):
        super(MySensorsDimmer, self)._set(datatype, value)

        if datatype == V_PERCENTAGE or datatype == V_DIMMER:
            self._level = value
        elif datatype == V_STATUS or datatype == V_LIGHT:
            self._state = value

    def setState(self, state):
        self.send(SET, V_STATUS, state, done = lambda _: setattr(self, '_state', state))

    def setLevel(self, level):
        self.send(SET, V_PERCENTAGE, level, done=lambda _: setattr(self, '_level', level))
