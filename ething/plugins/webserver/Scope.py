# coding: utf-8
from future.utils import string_types
from ething.core.reg import *


list = {
    'resource:read': {
        'description': 'read the content of any resource'
    },
    'resource:write': {
        'description': 'create resources of any kind or update the resource\'s metadata'
    },
    'file:read': {
        'description': 'read the content of any file'
    },
    'file:write': {
        'description': 'modify the content of any file'
    },
    'table:read': {
        'description': 'read the content of any table'
    },
    'table:write': {
        'description': 'modify the content of any table'
    },
    'device:execute': {
        'description': 'execute a device command'
    },
    'settings:read': {
        'description': 'read the settings'
    },
    'settings:write': {
        'description': 'modify the settings'
    },
    'flow:inject': {
        'description': 'inject data into flows'
    }
}


def validate(scopes):
    if isinstance(scopes, string_types):
        for scope in scopes.split(' '):
            if scope:
                if scope not in list:
                    return False
        return True
    return False


class ScopeType(String):

    def validate(self, value, context = None):
        super(ScopeType, self).validate(value, context)
        if not validate(value):
            raise ValueError('not a valid scope')

    def toSchema(self, context = None):
        s = super(ScopeType, self).toSchema(context)
        s['$component'] = 'scope'
        return s
