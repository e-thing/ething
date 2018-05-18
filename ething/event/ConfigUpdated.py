# coding: utf-8

from .Signal import Signal
from .Event import Event


class ConfigUpdated(Signal):
    pass



class ConfigUpdatedEvent(Event):
    
    signal = ConfigUpdated

