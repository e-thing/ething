# coding: utf-8

from ething.meta import interface
from .switch import Switch
from .dimmable import Dimmable


@interface
class DimmableSwitch(Switch, Dimmable):

    def getState(self):
        level = self.getLevel()
        return level > 0

    def setState(self, state):
        self.setLevel(100 if state else 0)
