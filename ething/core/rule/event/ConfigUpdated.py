# coding: utf-8

from . import Signal, Event
from ...reg import meta


__all__ = ["ConfigUpdated", "ConfigUpdatedEvent"]


class ConfigUpdated(Signal):

    def __init__(self, updated_keys, config):
        super(ConfigUpdated, self).__init__()
        self.updated_keys = updated_keys
        self.config = config


@meta(label='Configuration updated', icon='mdi-settings')
class ConfigUpdatedEvent(Event):
    """
    is emitted when the configuration has changed
    """
    signal = ConfigUpdated
