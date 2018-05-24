# coding: utf-8

from ething.meta import interface
from .rgbLight import RGBLight
from .dimmable import Dimmable


@interface
class RGBWLight (RGBLight, Dimmable):

    def getState(self):
        level = self.getLevel()
        return level > 0

    def setState(self, state):
        self.setLevel(100 if state else 0)
