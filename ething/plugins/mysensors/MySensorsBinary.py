# coding: utf-8

from .MySensorsSensor import MySensorsSensor
from ething.core.interfaces import Switch
from .helpers import *


class MySensorsBinary (MySensorsSensor, Switch):

    def _set_data(self, datatype, value):
        super(MySensorsBinary, self)._set_data(datatype, value)
        if datatype == V_STATUS or datatype == V_LIGHT:
            self._state = value

    def setState(self, state):
        self.send(SET, V_STATUS, state, done = lambda _: setattr(self, '_state', state))
