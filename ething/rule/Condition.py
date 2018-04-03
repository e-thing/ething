
from .RuleItem import RuleItem
from . import InvalidRuleException
from ething.meta import MetaCondition



class Condition(RuleItem):
    
    __metaclass__ = MetaCondition
    
    def evaluate(self, signal):
        if self.valid:
            
            # reset error
            self.error = False
            
            try:
                return bool(self.call(signal))
            except InvalidRuleException as e:
                # this exception is fired when this condition is no more valid.
                self.valid = False
                self.error = e
                self.ething.log.exception("Fatal error in condition %s" % self)
            
            except Exception as e:
                self.error = e
                self.ething.log.exception("Error in condition %s" % self)
        
        return False
    
    
    def call(self, signal):
        raise NotImplementedError()
