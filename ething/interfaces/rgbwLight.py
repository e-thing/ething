# coding: utf-8

from .dimmableLight import DimmableLight
from ..Interface import *


@interface
@attr('hue', type = Number(min=0, max=360), default = 0, mode = READ_ONLY, description = "the hue component of the light")
@attr('saturation', type = Number(min=0, max=100), default = 100, mode = READ_ONLY, description = "the saturation component of the light")
class RGBWLight (DimmableLight):

    def setState(self, state):
        if not state:
            if self.level > 0:
                setattr(self, '_level', self.level)  # cache
            self.setLevel(0)
        else:
            self.setLevel(getattr(self, '_level', 100))

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
