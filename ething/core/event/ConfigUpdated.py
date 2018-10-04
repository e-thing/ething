# coding: utf-8

from .Signal import Signal
from .Event import Event


__all__ = ["ConfigUpdated", "ConfigUpdatedEvent"]


class ConfigUpdated(Signal):

    def __init__(self, updated_keys):
        super(ConfigUpdated, self).__init__()
        self.updated_keys = updated_keys


class ConfigUpdatedEvent(Event):

    signal = ConfigUpdated
