# coding: utf-8

from .Signal import Signal
from .Event import Event
from ..reg import *


class Custom(Signal):

    def __init__(self, name):
        super(Custom, self).__init__()
        self.name = name


@attr('name', type=String(allow_empty=False), description="The name of the custom signal")
class CustomEvent(Event):

    signal = Custom

    def _filter(self, signal):

        return signal.name == self.name
