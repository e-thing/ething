# coding: utf-8
from future.utils import string_types
from .. import Condition
from croniter import croniter
import time

DELTA = 2

class Cron(Condition):
    
    @staticmethod
    def validate (attributes, context):
        
        attributes.setdefault('cron', None)
        
        for key in attributes:
            
                
            if key == 'cron':
                
                expr = attributes[key]
                
                if not( isinstance(expr, string_types) and croniter.is_valid(expr) ):
                    raise Exception("not a valid cron expression.")
                
            else:
                raise Exception("%s: invalid" % key)
        
        return True
    
    
    
    def call(self, signal):
        
        ts = signal['ts']
        expr = self['cron']
        
        iter = croniter(expr, int(ts - DELTA))
        
        c = iter.get_current()
        n = iter.get_next()
        
        if n - c <= 2*DELTA:
            return True
        else:
            return False
    