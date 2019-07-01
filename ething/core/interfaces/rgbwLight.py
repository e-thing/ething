# coding: utf-8

from .light import Light
from .dimmable import Dimmable
from ..Interface import *


@interface
@attr('hue', type = Number(min=0, max=360), default = 0, mode = READ_ONLY, description = "the hue component of the light")
@attr('saturation', type = Number(min=0, max=100), default = 100, mode = READ_ONLY, description = "the saturation component of the light")
class RGBWLight (Light, Dimmable):

    def setState(self, state):
        self.setLevel(100 if state else 0)

    def setLevel(self, level):
        """
        Set the brightness
        """
        self.level = level
        self.state = level > 0

    @method.arg('hue', type=Number(min=0, max=360), default=0)
    @method.arg('saturation', type=Number(min=0, max=100), default=100)
    def setColor(self, hue, saturation):
        """
        set the color of the light
        """
        self.hue = hue
        self.saturation = saturation
