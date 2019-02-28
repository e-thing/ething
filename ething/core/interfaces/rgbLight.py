# coding: utf-8

from ..Interface import *
from .light import Light


@interface
@attr('color', type = Color(), default = '#FFFFFF', mode = READ_ONLY, history = True, description = "the color of the light (#ffffff format)")
class RGBLight (Light):

    @method.arg('color', type=Color(), format='color')
    def setColor(self, color):
        """
        set the color of the light (#ffffff format)
        """
        self.color = color
