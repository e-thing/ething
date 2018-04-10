# coding: utf-8
from future.utils import string_types

from .base import Validator

class Scope(object):
    
    
    list = {
        
        'resource:read' : {
            'description' : 'read the content of any resource'
        },
        'resource:write' : {
            'description' : 'create resources of any kind and modify the content of any resource'
        },
        'resource:admin' : {
            'description' : 'modify resource properties, delete resource and access to apikeys'
        },
        'file:read' : {
            'description' : 'read the content of any file'
        },
        'file:write' : {
            'description' : 'create files and modify the content of any file'
        },
        'table:read' : {
            'description' : 'read the content of any table'
        },
        'table:write' : {
            'description' : 'create tables and modify the content of any table'
        },
        'table:append' : {
            'description' : 'append data to any existing table'
        },
        'app:read' : {
            'description' : 'read the raw script content of any apps'
        },
        'app:write' : {
            'description' : 'create and edit apps'
        },
        'app:execute' : {
            'description' : 'execute apps'
        },
        'device:read' : {
            'description' : 'send GET request to any device'
        },
        'device:write' : {
            'description' : 'send POST,PUT,PATCH,DELETE request to any device'
        },
        'notification' : {
            'description' : 'send notification'
        },
        'settings:read' : {
            'description' : 'read the settings'
        },
        'settings:write' : {
            'description' : 'modify the settings'
        },
        'rule:read' : {
            'description' : 'read rules attributes'
        },
        'rule:write' : {
            'description' : 'create rules'
        },
        'rule:execute' : {
            'description' : 'execute rules'
        },
        'rule:admin' : {
            'description' : 'delete rules'
        }
        
    }
    
    
    @staticmethod
    def validate (scopes):
        if isinstance(scopes, string_types):
            for scope in scopes.split(' '):
                if scope:
                    if scope not in Scope.list:
                        return False
            return True
        return False
    

class ScopeValidator(Validator):
    def validate(self, value):
        if (not isinstance(value, string_types)) or (not Scope.validate(value)):
            raise ValueError('not a valid scope')
        return value
    
    def schema(self):
        return {"type":"string"}



