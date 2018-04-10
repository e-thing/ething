# coding: utf-8
from future.utils import string_types

from .ResourceEvent import ResourceEvent


class ResourceMetaUpdated(ResourceEvent):
    
    
    @classmethod
    def emit(cls, resource, attributes):
        return super(ResourceMetaUpdated, cls).emit(resource, {
            'attributes': attributes # list of names of the attributes that has been updated
        })
    
    @staticmethod
    def validate (attributes, context):
        
        attributes.setdefault('attributes', None)
        
        other = {}
        
        for key in attributes:
            
            value = attributes[key]
            
            if key == 'attributes':
                
                if value is None:
                    pass
                elif isinstance(value, list):
                    for v in value:
                        if not isinstance(v, string_types):
                            raise Exception("the key '%s' must be an array of string" % key)
                else:
                    raise Exception("the key '%s' must be an array of string" % key)
                
            else:
                other[key] = value
        
        return ResourceEvent.validate(other, context)
    
    
    def call(self, signal):
        
        if self['attributes'] is not None:
            
            a = self['attributes']
            b = signal['attributes']
            f = False
            for val in a:
                if val in b:
                    f = True
                    break
            if not f:
                return False
        
        return super(ResourceMetaUpdated, self).call(signal)
    


