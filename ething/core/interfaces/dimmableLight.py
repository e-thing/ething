# coding: utf-8
from .light import Light
from .dimmable import Dimmable
from ..Interface import interface


@interface
class DimmableLight(Light, Dimmable):

    def setState(self, state):
        if not state:
            if self.level>0:
                setattr(self, '_level', self.level) # cache
            self.setLevel(0)
        else:
            self.setLevel(getattr(self, '_level', 100))

    def setLevel(self, level):
        self.level = level
        self.state = level > 0
