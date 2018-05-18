# coding: utf-8


from . import ResourceSignal, ResourceEvent
from ething.base import attr, isString, isArray, isNone


class ResourceMetaUpdated(ResourceSignal):
    
    def __init__(self, resource, attributes):
        super(ResourceMetaUpdated, self).__init__(resource)
        self.attributes = attributes


@attr('attributes', validator = isArray(min_len = 1, item = isString(allow_empty = False)) | isNone(), default = None)
class ResourceMetaUpdatedEvent(ResourceEvent):
    """
    is emitted each time a resource attribute has been updated
    """
    
    signal = ResourceMetaUpdated
    
    def _filter(self, signal):
        
        if super(ResourceMetaUpdatedEvent, self)._filter(signal):
            a = self.attributes
            
            if not a:
                return True
            
            b = signal.attributes
            for val in a:
                if val in b:
                    return True
        
        return False


