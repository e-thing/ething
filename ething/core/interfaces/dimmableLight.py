# coding: utf-8
from .light import Light
from .dimmable import Dimmable
from ..Interface import interface


@interface
class DimmableLight(Light, Dimmable):

    def setState(self, state):
        self.setLevel(100 if state else 0)

    def setLevel(self, level):
        self.level = level
        self.state = level > 0
