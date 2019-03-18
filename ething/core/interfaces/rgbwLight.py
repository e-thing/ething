# coding: utf-8

from .rgbLight import RGBLight
from .dimmable import Dimmable
from ..Interface import *


@interface
class RGBWLight (RGBLight, Dimmable):

    def setState(self, state):
        self.setLevel(100 if state else 0)

    def setLevel(self, level):
        self.level = level
        self.state = level > 0

