from flask import request, Response, g
from ething.ShortId import ShortId
from ething.Table import Table
from ething.Helpers import toJson
import json as js
import re
import datetime


CHK_STRING = 4
CHK_LOGIC = 10
CHK_INT = 13
CHK_UNSIGNED_INT = 15
CHK_URL = 19
CHK_ID = 20
CHK_STRING_ARRAY = 34
CHK_FORMAT = 35
CHK_DATEFORMAT = 36
CHK_INVALIDFIELDMODE = 38


FMT_JSON = 1
FMT_JSON_PRETTY = 2
FMT_CSV  = 5
FMT_CSV_NOHEADER = 6

table_output_formats = {
	"json": FMT_JSON,
	"json_pretty": FMT_JSON_PRETTY,
	"csv": FMT_CSV,
	"csv_no_header": FMT_CSV_NOHEADER
}

date_formats = {
	"timestamp": Table.TIMESTAMP,
	"timestamp_ms": Table.TIMESTAMP_MS,
	"rfc3339": None
}

invalid_field_modes = {
	"rename": Table.INVALID_FIELD_RENAME,
	"stop": Table.INVALID_FIELD_STOP,
	"skip": Table.INVALID_FIELD_SKIP,
	"none": Table.INVALID_FIELD_NONE
}



def jsonify(obj, **kwargs):
	return Response(toJson(obj, **kwargs), mimetype='application/json')

def getParameter(key, checker = None, optional = False, default = None):
	
	key = key.lower()
	value = None
	
	found = True
	for k in request.values:
		if k.lower() == key:
			found = True
			value = request.values[k]
			break
	
	if not found:
		# not found
		if not optional:
			raise Exception('The key "%s" is mandatory' % key)
	
	if checker and value is not None:
		# check the type of the value
		
			
		if checker == CHK_ID:
			if not ShortId.validate(value):
				raise Exception("The key %s is not a regular resource identifier ('%s')." % (key,value))
		elif checker == CHK_LOGIC:
			if re.search('^(false|0)$', value, re.IGNORECASE):
				value = False
			elif re.search('^(true|1)$', value, re.IGNORECASE):
				value = True
			else:
				raise Exception("The key %s is not a regular boolean ('%s')." % (key,value))
		elif checker == CHK_INT or checker == CHK_UNSIGNED_INT:
			
			try:
				v = int(value)
			except ValueError:
				raise Exception("The key %s is not a regular numeric value ('%s')." % (key,value))
			
			value = v
			
			if checker == CHK_UNSIGNED_INT and value<0:
				raise Exception("The key %s must be positive ('%s')." % (key,value))
		
		elif checker == CHK_URL: # accept empty string
			if not re.search('^https?:\/\/([0-9a-zA-Z\.-]+)(:[0-9]+)?(\/[a-zA-Z0-9_\-\s\.\/\?\%\#\&\=]*)?$', value):
				raise Exception("The key %s is not regular url ('%s')." % (key,value))
		elif checker == CHK_STRING:
			pass
		elif checker == CHK_STRING_ARRAY: # accept comma separated values
			value = value.split(',')
		elif checker == CHK_FORMAT:
			value = value.lower()
			
			if value not in table_output_formats:
				raise Exception("The key %s is a unknown table output format '%s'" % (key,value))
			
			value = table_output_formats[value]
			
		elif checker == CHK_DATEFORMAT:
			
			value = value.lower()
			
			if value not in date_formats:
				raise Exception("The key %s is a unknown date format '%s'" % (key,value))
			
			value = date_formats[value]
			
		elif checker == CHK_INVALIDFIELDMODE:
			
			value = value.lower()
			
			if value not in invalid_field_modes:
				raise Exception("The key %s is a unknown mode '%s'" % (key,value))
			
			value = invalid_field_modes[value]
	
	if value is None:
		value = default
	
	return value


def getResource(ething, id, restrictToTypes = None):
	
	authenticated = hasattr(g, 'auth')
	
	if id == 'me' and authenticated and g.auth.resource:
		# special case, needs api key auth
		r = g.auth.resource
	else:
		r = ething.get(id)
	
	if r is None:
		raise Exception('resource not found')
	
	if restrictToTypes is not None:
		ok = False
		for type in restrictToTypes:
			if r.isTypeof(type):
				ok = True
				break
		if not ok:
			raise Exception('resource not found')
	
	
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
					raise Exception('resource not found')
	
	
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

class HTTPMethodOverrideMiddleware(object):
    allowed_methods = frozenset([
        'GET',
        'HEAD',
        'POST',
        'DELETE',
        'PUT',
        'PATCH',
        'OPTIONS'
    ])
    bodyless_methods = frozenset(['GET', 'HEAD', 'OPTIONS', 'DELETE'])

    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        method = environ.get('HTTP_X_HTTP_METHOD_OVERRIDE', '').upper()
        if method in self.allowed_methods:
            method = method.encode('ascii', 'replace')
            environ['REQUEST_METHOD'] = method
        if method in self.bodyless_methods:
            environ['CONTENT_LENGTH'] = '0'
        return self.app(environ, start_response)


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
	
	