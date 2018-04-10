# coding: utf-8

from .ResourceAction import ResourceAction


class ResourceClear(ResourceAction):
    
    @staticmethod
    def validate (attributes, context):
        return ResourceAction.validate(attributes, context, onlyTypes=['File','Table'])
    
    
    
    def call(self, signal):
        
        for r in self.getResourcesFromSignal(signal):
            if r.type == 'Table':
                r.clear()
            elif r.type == 'File':
                r.write('')
        
        
