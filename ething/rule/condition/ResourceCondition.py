
from .. import Condition
from .. import Signal
from .. import InvalidRuleException
from ething.ShortId import ShortId
from ething.ResourceQueryParser import ResourceQueryParser


class ResourceCondition(Condition):
    
    @staticmethod
    def validate (attributes, context, onlyTypes=None):
        
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
                
                if isinstance(resourceFilter, basestring):
                    # can either be an id or an expression or #emitter
                    
                    if resourceFilter == '#emitter':
                        pass
                    elif ShortId.validate(resourceFilter):
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
    
    
    
    def getResourcesFromSignal(self, signal):
        
        rs = []
        
        resourceFilter = self['resource']
        
        if isinstance(resourceFilter, basestring): # can either be an id or an expression or #emitter
            
            if resourceFilter == '#emitter':
                
                resourceIdFromSignal = signal['resource']
                if resourceIdFromSignal is not None:
                    r = self.ething.get(resourceIdFromSignal)
                    if r is None:
                        raise Exception("unable to find the resource with id '%s'" % resourceIdFromSignal)
                    rs.append(r)
                else:
                    raise Exception('this signal was not emitted by a resource')
            
            elif ShortId.validate(resourceFilter):
                r = self.ething.get(resourceFilter)
                if r is None:
                    raise InvalidRuleException("unable to find the resource with id '%s'" % resourceFilter)
                rs.append(r)
            else:
                # expression
                rs = self.ething.find(resourceFilter)
            
        elif isinstance(resourceFilter, list): # array of resource ids
            
            notFound = []
            for id in resourceFilter:
                r = self.ething.get(id)
                if r is None:
                    notFound.append(id)
                rs.append(r)
            
            
            if notFound:
                if len(rs)==0:
                    raise InvalidRuleException("unable to find the resources with id : %s" % (','.join(notFound)))
                else:
                    raise Exception("unable to find the resources with id : %s" % (','.join(notFound)))
        
        
        return rs
    
    
    