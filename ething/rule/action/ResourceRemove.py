# coding: utf-8

from .ResourceAction import ResourceAction


class ResourceRemove(ResourceAction):
    
    def call(self, signal):
        for r in self.getResourcesFromSignal(signal):
            r.remove()
        
    
    