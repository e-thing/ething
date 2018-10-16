# coding: utf-8

from . import Signal, Event


__all__ = ["ConfigUpdated", "ConfigUpdatedEvent"]


class ConfigUpdated(Signal):

    def __init__(self, updated_keys, config):
        super(ConfigUpdated, self).__init__()
        self.updated_keys = updated_keys
        self.config = config


class ConfigUpdatedEvent(Event):

    signal = ConfigUpdated
