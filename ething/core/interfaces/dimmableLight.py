# coding: utf-8
from .light import Light
from .dimmable import Dimmable
from ..Interface import interface


@interface
class DimmableLight(Light, Dimmable):

    def setState(self, state):
        self.setLevel((self.level or 100) if state else 0)
