# coding: utf-8
from future.utils import string_types
from .. import Event
from .. import Signal


class Custom(Event):
    
    
    @staticmethod
    def validate (attributes, context):
        
        attributes.setdefault('name', None)
        
        for key in attributes:
            
                
            if key == 'name':
                
                name = attributes[key]
                
                if not(isinstance(name, string_types) and name ):
                    raise Exception("name must be a non empty string.");
                
            else:
                raise Exception("%s: invalid" % key)
        
        return True
    
    
    def call(self, signal):
        return signal['name'] == self['name']
    
    @classmethod
    def emit(cls, name):
        return super(Custom, cls).emit({
            'name' : name
        })
        
        
