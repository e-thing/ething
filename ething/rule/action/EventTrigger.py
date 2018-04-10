# coding: utf-8
from future.utils import string_types
from .. import Action
from ething.rule.event import Custom

class EventTrigger(Action):
    
    @staticmethod
    def validate (attributes, context):
        
        attributes.setdefault('name', None)
        
        for key in attributes:
            
            value = attributes[key]
            
            if key == 'name':
                
                if not( isinstance(value, string_types) and len(value)>0 ):
                    raise Exception("must be a non empty string.")
            
            else:
                raise Exception("%s: invalid" % key)
        
        return True
    
    
    
    def call(self, signal):
        self.ething.dispatchSignal(Custom.emit(self['name']))
    