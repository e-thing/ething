# coding: utf-8

from .MySensorsSensor import MySensorsSensor
from ething.core.interfaces import DimmableSwitch
from .helpers import *


class MySensorsDimmer (MySensorsSensor, DimmableSwitch):

    def _set_data(self, datatype, value):
        super(MySensorsDimmer, self)._set_data(datatype, value)

        if datatype == V_PERCENTAGE or datatype == V_DIMMER:
            self.level = value
        elif datatype == V_STATUS or datatype == V_LIGHT:
            self.state = value

    def setState(self, state):
        self.send(SET, V_STATUS, state, done = lambda _: setattr(self, 'state', state))

    def setLevel(self, level):
        self.send(SET, V_PERCENTAGE, level, done=lambda _: setattr(self, 'level', level))
