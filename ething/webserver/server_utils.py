# coding: utf-8
from flask import request, Response, g
from ething.ShortId import ShortId
from ething.Table import Table
from ething.Helpers import toJson
import json as js
import re
import datetime
import traceback
import sys
import os

from webargs.flaskparser import use_args as webargs_use_args
from marshmallow.fields import Field
from webargs.flaskparser import parser
from webargs import fields, validate

from functools import wraps

root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

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
    
    fields = request.args.get('fields')
    
    if fields is not None:
        fields = fields.replace(' ',',').replace(';',',').replace('|',',').split(',')
    
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



class ServerException(Exception):
    def __init__(self, message, status_code = 400):
        
        super(ServerException, self).__init__(message)
        
        self.status_code = status_code



_re_tb_extract = re.compile('File "(.*)", line (\d+)')

def tb_extract_info():
    
    file = None
    lineno = None
    
    for l in reversed(traceback.format_exception(*sys.exc_info())):
        matches = _re_tb_extract.search(l)
        if matches:
            file = matches.group(1)
            lineno = int(matches.group(2))
            
            if file.startswith(root_path):
                break
    
    return (file, lineno)


def parse_multipart_data(stream, boundary):
    boundary = boundary.encode()
    next_boundary = boundary and b'--' + boundary or None
    last_boundary = boundary and b'--' + boundary + b'--' or None
 
    stack = []
 
    state = 'boundary'
    line = next(stream).rstrip()
    assert line == next_boundary
    for line in stream:
        
        if line.rstrip() == last_boundary:
            break
 
        if state == 'boundary':
            state = 'headers'
            if stack:
                headers, body = stack.pop()
                yield headers, b''.join(body)
            stack.append(({}, []))
 
        if state == 'headers':
            if line == b'\r\n':
                state = 'body'
                continue
            headers = stack[-1][0]
            line = line.decode()
            key, value = map(lambda i: i.strip(), line.split(':'))
            headers[key] = value
 
        if state == 'body':
            if line.rstrip() == next_boundary:
                state = 'boundary'
                continue
            stack[-1][1].append(line)
 
    if stack:
        headers, body = stack.pop()
        yield headers, b''.join(body)
