# coding: utf-8

from . import Signal, Event
from ething.core.reg import *


__all__ = ["Custom", "CustomEvent"]


class Custom(Signal):

    def __init__(self, name):
        super(Custom, self).__init__()
        self.name = name


@attr('name', type=String(allow_empty=False), description="The name of the custom signal")
class CustomEvent(Event):

    signal = Custom

    def _filter(self, signal):

        return signal.name == self.name
