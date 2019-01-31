# coding: utf-8

from ..Interface import Interface
from ..reg import *


@attr('level', type = Number(min=0, max=100), default = 0, mode = READ_ONLY, history = True, description = "the level of this dimmable switch")
class Dimmable(Interface):

    @method.arg('level', type=Range(0, 100))
    def setLevel(self, level):
        """
        set the current level of this dimmable switch
        """
        self.level = level
