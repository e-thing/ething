# coding: utf-8

from ..Device import Device
from ..Interface import *
from ..Signal import ResourceSignal


class ButtonClicked(ResourceSignal):
    def __init__(self, resource, type=None):
        super(ButtonClicked, self).__init__(resource, type=type or 'single')


@interface
@meta(icon='mdi-radiobox-marked')
@throw(ButtonClicked)
class Button(Device):

    def click(self, type=None):
        self.emit(ButtonClicked(self, type=type))

