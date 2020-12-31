# coding: utf-8

from ..Interface import *
from ..Device import Device


@interface
@meta(icon='mdi-contrast-circle')
@attr('level', type=Number(min=0, max=100), default=0, mode=READ_ONLY, description="the level of this dimmable switch")
class Dimmable(Device):

    @method.arg('level', type=Range(0, 100))
    def setLevel(self, level):
        """
        set the current level of this dimmable switch
        """
        self.level = level
