# coding: utf-8

from ..Interface import Interface
from ..reg import *
from ..Signal import ResourceSignal


class ButtonClicked(ResourceSignal):
    def __init__(self, resource, type='single'):
        super(ButtonClicked, self).__init__(resource)
        self.type = type


@throw(ButtonClicked)
class Button(Interface):
    pass

