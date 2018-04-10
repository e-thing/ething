# coding: utf-8

from . import Signal
from .RuleItem import RuleItem
from . import InvalidRuleException
from ething.meta import MetaEvent
from future.utils import with_metaclass


class Event(with_metaclass(MetaEvent,RuleItem)):
    
    
    def match(self, signal):
        if self.valid:
            
            # reset error
            self.error = False
            
            try:
                return bool(self.call(signal))
            
            except InvalidRuleException as e:
                # this exception is fired when this event is no more valid.
                self.valid = False
                self.error = e
                self.ething.log.exception("Fatal error in event %s" % self)
            
            except Exception as e:
                self.error = e
                self.ething.log.exception("Error in event %s" % self)
        
        return False
    
    
    def call(self, signal):
        return True
    
    @classmethod
    def emit(cls, attribute = {}):
        return Signal(cls.__name__, attribute)
    
