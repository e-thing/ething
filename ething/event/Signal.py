# coding: utf-8

from ething.meta import MetaSignal
from future.utils import with_metaclass
import time



class Signal(with_metaclass(MetaSignal,object)):
    
    
    def __init__ (self):
        super(Signal, self).__setattr__('_Signal__ts', time.time())
    
    @property
    def timestamp (self):
        return self.__ts
    
    def __str__(self):
        return type(self).__name__
    
    def __repr__(self):
        return type(self).__name__
    
    def toJson (self):
        js = {
            'type': type(self).__name__,
            'ts' : self.timestamp
        }
        
        js.update(self.__dict__)
        
        return js
    
    # deprecated: just for compatibility
    def __getitem__ (self, name):
        return getattr(self, name, None)
    