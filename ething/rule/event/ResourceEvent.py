# coding: utf-8
from future.utils import string_types

from .. import Event
from .. import Signal
from ething.ShortId import ShortId
from ething.ResourceQueryParser import ResourceQueryParser


class ResourceEvent(Event):
    
    @staticmethod
    def validate (attributes, context, onlyTypes = None):
        
        attributes.setdefault('resource', None)
        
        for key in attributes:
            
                
            if key == 'resource':
                
                resourceFilter = attributes[key]
                
                def checkId(id):
                    # resource id 
                    resource = context['ething'].get(resourceFilter)
                    if resource is None:
                        raise Exception("the resource with id '%s' does not exist." % resourceFilter)
                    if onlyTypes:
                        # check the type
                        passed = False
                        for type in onlyTypes:
                            if resource.isTypeof(type):
                                passed = True
                                break
                        if not passed:
                            raise Exception("the resource %s must be one of the following types : %s" % (str(resource), ', '.join(onlyTypes)))
                
                if resourceFilter is None: # this event will be fired on every resource
                    pass
                elif isinstance(resourceFilter, string_types):
                    # can either be an id or an expression
                    
                    if ShortId.validate(resourceFilter):
                        # resource id 
                        checkId(resourceFilter)
                    else:
                        # expression
                        ok, message =  ResourceQueryParser.check(resourceFilter)
                        if not ok:
                            raise Exception('invalid expression: %s' % message)
                
                elif isinstance(resourceFilter, list):
                    if len(resourceFilter)==0:
                        raise Exception("not a valid array of resource's id.")
                    
                    # must be an array of ids
                    for id in resourceFilter:
                        if ShortId.validate(id):
                            checkId(id)
                        else:
                            raise Exception("not a valid array of resource's id.")
                
                else:
                    raise Exception("%s: invalid" % key)
            
            else:
                raise Exception("%s: invalid" % key)
        
        
        return True
    
    
    
    def filter(self, signal):
        
        resourceIdFromSignal = signal['resource']
        
        if resourceIdFromSignal is not None:
            # the event accepts only signal emitted from a resource
            
            resourceFilter = self['resource']
            
            if resourceFilter is None: # no filtering
                return True
            elif isinstance(resourceFilter, string_types): # can either be an id or an expression
                
                if ShortId.validate(resourceFilter):
                    return resourceFilter == resourceIdFromSignal
                else: # query string
                    # check if the resource from the signal match the expression
                    return bool( self.ething.findOne( {
                        '$and' : {
                            { '_id' : resourceIdFromSignal },
                            self.ething.resourceQueryParser.parse(resourceFilter)
                        }
                    } ) )
                
            elif isinstance(resourceFilter, list): # array of resource ids
                return resourceIdFromSignal in resourceFilter
        
        return False
    
    
    def call(self, signal):
        return self.filter(signal)
    
    
    @classmethod
    def emit(cls, resource, attribute = {}):
        
        attr = {
            'resource' : resource.id,
            'rName' : resource.name,
            'rType' : resource.type,
            'rModifiedDate': resource.modifiedDate
        }
        
        attr.update(attribute)
        
        return super(ResourceEvent, cls).emit(attr)
    

