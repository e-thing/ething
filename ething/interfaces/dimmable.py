# coding: utf-8

from ething.Interface import Interface
from ething.reg import *


@attr('level', type = Number(min=0, max=100), default = 0, mode = READ_ONLY, history = True, description = "the level of this dimmable switch")
class Dimmable(Interface):

    @method.arg('level', type=Number(min=0, max=100))
    def setLevel(self, level):
        """
        set the current level of this dimmable switch
        """
        self._level = level
