# coding: utf-8

from .Signal import Signal
from .Event import Event
from ething.base import attr, isString


class Custom(Signal):
    
    def __init__(self, name):
        super(Custom, self).__init__()
        self.name = name

@attr('name', validator = isString(allow_empty = False), description="The name of the custom signal")
class CustomEvent(Event):
    
    signal = Custom
    
    def _filter(self, signal):
        
        return signal.name == self.name

