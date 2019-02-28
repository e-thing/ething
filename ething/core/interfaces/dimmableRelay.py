# coding: utf-8

from .relay import Relay
from .dimmable import Dimmable
from ..Interface import interface


@interface
class DimmableRelay(Relay, Dimmable):

    def setState(self, state):
        self.setLevel((self.level or 100) if state else 0)
