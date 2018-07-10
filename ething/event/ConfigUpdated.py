# coding: utf-8

from .Signal import Signal
from .Event import Event


class ConfigUpdated(Signal):

    def __init__(self, changes):
        super(ConfigUpdated, self).__init__()
        self.changes = changes


class ConfigUpdatedEvent(Event):

    signal = ConfigUpdated
