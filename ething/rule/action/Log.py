# coding: utf-8
from future.utils import string_types
from .. import Action



class Log(Action):
    
    @staticmethod
    def validate (attributes, context):
        
        attributes.setdefault('message', None)
        
        for key in attributes:
            
            value = attributes[key]
            
            if key == 'message':
                
                if not( isinstance(value, string_types) and len(value)>0 ):
                    raise Exception("%s: must be a non empty string." % key)
            
            else:
                raise Exception("%s: invalid" % key)
        
        return True
    
    
    
    def call(self, signal):
        self.ething.log.info(self['message'])
    
    
