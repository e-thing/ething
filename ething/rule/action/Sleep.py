# coding: utf-8
from .. import Action
import time


class Sleep(Action):
    
    @staticmethod
    def validate (attributes, context):
        
        attributes.setdefault('duration', None)
        
        for key in attributes:
            
            
            if key == 'duration':
                
                duration = attributes[key]
                
                if not((isinstance(duration, int) or isinstance(duration, float)) and duration > 0 and duration < 3600 ):
                    raise Exception("duration must be a number of seconds greater than 0 and lower than 1 hour.");
                
            else:
                raise Exception("%s: invalid" % key)
        
        return True
    
    
    
    def call(self, signal):
        time.sleep(self['duration'])
    
