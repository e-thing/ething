# coding: utf-8

from .MySensorsSensor import MySensorsSensor
from ething.core.interfaces import Relay
from .helpers import *


class MySensorsBinary (MySensorsSensor, Relay):

    def _set_data(self, datatype, value):
        super(MySensorsBinary, self)._set_data(datatype, value)
        if datatype == V_STATUS or datatype == V_LIGHT:
            self.state = value

    def setState(self, state):
        self.send(SET, V_STATUS, state, done = lambda _: setattr(self, 'state', state))
