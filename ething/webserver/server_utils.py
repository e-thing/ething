from flask import request, Response, g
from ething.ShortId import ShortId
from ething.Table import Table
from ething.Helpers import toJson
import json as js
import re
import datetime

from webargs.flaskparser import use_args as webargs_use_args
from marshmallow.fields import Field
from webargs.flaskparser import parser
from webargs import fields, validate

from functools import wraps


VALID_METHODS = [
    'GET',
    'POST',
    'PUT',
    'PATCH',
    'DELETE',
    'HEAD',
    'OPTIONS',
]



# Field patch
__field_init = getattr(Field, '__init__', None)

def __field_init_patched(self, *args, **kwargs):
    kwargs.setdefault('default', None)
    __field_init(self, *args, **kwargs)

setattr(Field, '__init__', __field_init_patched)



def use_args(args, **kwargs):
    def d(view):
        
        webargs = getattr(view, 'webargs', None)
        
        if webargs is None:
            webargs = {
                '*': {
                    'schema': args,
                    'options': kwargs
                }
            }
        else:
            raise Exception('two or more successive call of "use_args" has been made for the view %s' % str(view))
        
        setattr(view, 'webargs', webargs)
        
        return webargs_use_args(args, **kwargs)(view)
    
    return d

def use_multi_args(**kwargs):
    def d(view):
        
        webargs = getattr(view, 'webargs', None)
        
        if webargs is None:
            webargs = {}
        else:
            raise Exception('two or more successive call of "use_multi_args" has been made for the view %s' % str(view))
        
        for m in VALID_METHODS:
            args = kwargs.pop(m, None)
            if args:
                
                schema = None
                options = {}
                
                if isinstance(args, list) or isinstance(args, tuple):
                    if len(args)>0:
                        schema = args[0]
                    if len(args)>1:
                        if isinstance(args, dict):
                            options = args[1]
                        else:
                            options['locations'] = args[1]
                else:
                    schema = args
                
                if schema:
                    webargs[m] = {
                        'schema': schema,
                        'options': options
                    }
        
        if kwargs:
            for m in webargs:
                options = {}
                options.update(kwargs)
                options.update(webargs[m]['options'])
                webargs[m]['options'] = options
        
        setattr(view, 'webargs', webargs)
        
        @wraps(view)
        def wrapper(*args, **kwds):
            
            if request.method in webargs:
                wa_args = parser.parse(webargs[request.method]['schema'], request, **webargs[request.method]['options'])
            else:
                wa_args = {}
            
            args = (wa_args,) + args
            
            return view(*args, **kwds)
            
        
        return wrapper
    
    return d


def jsonify(obj, **kwargs):
    return Response(toJson(obj, **kwargs), mimetype='application/json')


def getResource(core, id, restrictToTypes = None):
    
    message = 'resource with id="%s" not found or has not the right type' % id
    
    authenticated = hasattr(g, 'auth')
    
    if id == 'me' and authenticated and g.auth.resource:
        # special case, needs api key auth
        r = g.auth.resource
    else:
        r = core.get(id)
    
    if r is None:
        raise Exception(message)
    
    if restrictToTypes is not None:
        ok = False
        for type in restrictToTypes:
            if r.isTypeof(type):
                ok = True
                break
        if not ok:
            raise Exception(message)
    
    
    if authenticated:
        scope = g.auth.scope
        
        if scope is not None:
            
            scopes = filter(None, auth.scope.split(" "))
            
            allowed_types = []
            for scope in scopes:
                type = scope.split(':')[0].capitalize()
                if type not in allowed_types:
                    allowed_types.append(type)
            
            if 'resource' not in allowed_types:
                # restrict the search to the allowed_types
                ok = False
                for allowed_type in allowed_types:
                    if r.isTypeof(allowed_type):
                        ok = True
                        break
                if not ok:
                    raise Exception(message)
    
    
    return r


def dict_intersect_keys(dict1, *dicts):
    '''
    returns an dict containing all the entries of dict1 which have keys that are present in all other dicts.

    :param dict1: dict with master keys to check
    :type dict1: dict
    :param \*dicts: dicts to compare keys against
    :type \*dicts: dict
    :return: dict containing all the entries of dict1 which have keys that are present in all other dicts
    :rtype: dict
    '''
    keys = dict1.viewkeys()
    for dict in dicts:
        keys &= dict.viewkeys()

    return {k: dict1[k] for k in keys}


def jsonEncodeFilterByFields(resources,fields = None):
    if isinstance(fields, list):
        fields = dict(zip(fields, range(len(fields))))
        if isinstance(resources, list):
            out = [];
            for resource in resources:
                out.append(dict_intersect_keys(resource.toJson(), fields))
        else:
            out = dict_intersect_keys(resources.toJson(), fields)
    else:
        out = resources
    return jsonify(out)



if __name__ == '__main__':
    
    from ething.core import Core
    
    ething = Core({
        'db':{
            'database': 'test'
        },
        'log':{
            'level': 'debug'
        }
    })
    
    resp = jsonEncodeFilterByFields(ething.find(), ['id'])
    print resp.response
    
    