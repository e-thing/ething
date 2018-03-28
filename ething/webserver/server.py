
from flask import Flask, request, Response, send_from_directory, redirect, url_for
from flask_cors import CORS
from werkzeug.exceptions import HTTPException
from .server_utils import *
from auth import install_auth, auth
import json as js
import os, sys, re
import csv, StringIO
from ething.ShortId import ShortId
import traceback
import base64
import logging


root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

app = Flask(__name__, static_url_path='', root_path=root_path)

app.wsgi_app = HTTPMethodOverrideMiddleware(app.wsgi_app)

CORS(app, resources={r"/api/*": {"origins": "*"}})

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)


core = None

debug = False




def error_handler(e):
	
	error = {
		'message' : str(e),
		'code': 400
	}
	
	if isinstance(e, HTTPException):
		error['code'] = e.get_response().status_code
	
	if debug :
		exc_type, exc_obj, exc_tb = sys.exc_info()
		error['stack'] = traceback.format_exc()
		error['file'] = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
		error['line'] = exc_tb.tb_lineno
		
	
	return Response(js.dumps(error), status=400, mimetype='application/json')
	


# static files

@app.route('/favicon.ico')
def favicon():
	return ('', 404)
	#return send_from_directory(os.path.join(app.root_path, 'static'),'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/')
def root():
	return redirect(url_for('static_client', path = 'index.html'))

@app.route('/client')
def root_client():
	return redirect(url_for('static_client', path = 'index.html'))

@app.route('/client/<path:path>')
def static_client(path):
	return send_from_directory('webui', path)



# API

@app.route('/api/auth', methods=['GET'])
@auth.required()
def api_auth():
	
	auth = g.auth
	
	d = {
		'type': auth.type
	}
	
	if auth.resource:
		d['resource'] = auth.resource
	
	if auth.scope is not None:
		d['scope'] = auth.scope
	
	return jsonify(d)

@app.route('/api/usage', methods=['GET'])
@auth.required('resource:read')
def usage():
	return jsonify(core.usage())

@app.route('/api/settings', methods=['GET', 'PATCH'])
@auth.required(GET = 'settings:read', PATCH = 'settings:write')
def settings():
	if request.method == 'PATCH':
		core.config.set(request.get_json())
	
	return jsonify(core.config())

@app.route('/api/resources', methods=['GET'])
@auth.required('resource:read resource:write file:read file:write table:read table:write table:append device:read device:write app:read app:write')
def resources():
	
	query = getParameter('q',CHK_STRING,True)
	limit = getParameter('limit',CHK_UNSIGNED_INT,True)
	skip = getParameter('skip',CHK_UNSIGNED_INT,True)
	sort = getParameter('sort',CHK_STRING,True)
	
	auth = g.auth
	
	if auth.scope is not None:
		
		scopes = filter(None, auth.scope.split(" "))
		
		allowed_types = []
		for scope in scopes:
			type = scope.split(':')[0].capitalize()
			if type not in allowed_types:
				allowed_types.append(type)
		
		if 'resource' not in allowed_types:
			# restrict the search to the allowed_types
			
			typeQuery = {
				'extends' : { '$in' : allowed_types }
			}
			
			if query:
				query = {
					'$and' : [core.resourceQueryParser.parse(query), typeQuery]
				}
			else:
				query = typeQuery
	
	return jsonEncodeFilterByFields(core.find(query = query, limit = limit, skip = skip, sort = sort), getParameter('fields',CHK_STRING_ARRAY, True))

@app.route('/api/resources/<id>', methods=['GET', 'DELETE', 'PATCH'])
@auth.required(GET = 'resource:read resource:write file:read file:write table:read table:write table:append device:read device:write app:read app:write', DELETE = 'resource:admin', PATCH = 'resource:admin')
def resource(id):
	r = getResource(core, id)
	
	if request.method == 'GET':
		return jsonEncodeFilterByFields(r, getParameter('fields',CHK_STRING_ARRAY, True))
	
	elif request.method == 'PATCH':
		
		data = request.get_json()
		
		if isinstance(data, dict):
			
			content = None
		
			if r.type == 'Http':
				content = attr.pop('content', None)
			elif r.type == 'MQTT':
				content = attr.pop('subscription', None)
			
			for key, value in data.iteritems():
				setattr(r, key, value)
			
			r.save()
			
			if content:
				if r.type == 'Http':
					r.setSpecification(base64.b64decode(content))
				elif r.type == 'MQTT':
					r.setSubscription(content)
			
			return jsonEncodeFilterByFields(r, getParameter('fields',CHK_STRING_ARRAY, True))
		
		raise Exception('Invalid request');
	
	elif request.method == 'DELETE':
		r.remove(getParameter('children',CHK_LOGIC, True, False))
		return ('', 204)




@app.route('/api/files', methods=['POST'])
@auth.required('file:write resource:write')
def files():
	
	attr = request.get_json()
	
	if isinstance(attr, dict):
		
		content = None
		
		if 'content' in attr:
			content = base64.b64decode(attr['content'])
			attr.pop('content')
		
		attr.setdefault('createdBy', g.auth.resource)
		
		r = core.create('File', attr)
		
		if r:
			
			if content:
				r.write(content)
			
			response = jsonEncodeFilterByFields(r, getParameter('fields',CHK_STRING_ARRAY, True))
			response.status_code = 201
			return response
		else:
			raise Exception('Unable to create the file');
	
	raise Exception('Invalid request');


@app.route('/api/files/<id>', methods=['GET', 'PUT'])
@auth.required(GET = 'file:read resource:read', PUT = 'file:write resource:write')
def file(id):
	r = getResource(core, id, ['File'])
	
	if request.method == 'GET':
		return Response(r.read(), mimetype = r.mime)
	
	elif request.method == 'PUT':
		
		content = request.data
		
		if getParameter('APPEND',CHK_LOGIC,True,False):
			r.append(content)
		else:
			r.write(content)
		
		return jsonEncodeFilterByFields(r, getParameter('fields',CHK_STRING_ARRAY, True))


@app.route('/api/files/<id>/<action>')
@auth.required('file:read resource:read')
def file_action(id, action):
	r = getResource(core, id, ['File'])
	
	if action == 'thumbnail':
		
		thumb = r.readThumbnail()
		
		if not thumb:
			raise Exception('No thumbnail available')
		
		return Response(thumb, mimetype='image/png')
	
	elif action == 'execute':
		
		if r.mime == 'application/javascript':
			
			args = getParameter('args',CHK_STRING, True)
			
			res = ScriptEngine.runFromFile(r, args)
			
			if not res:
				raise Exception('Unable to execute')
			
			jsonify(res);
			
		else:
			raise Exception('Not executable');
	
	raise Exception('Invalid request');




@app.route('/api/apps', methods=['POST'])
@auth.required('app:write resource:write')
def apps():
	
	attr = request.get_json()
	
	if isinstance(attr, dict):
		
		content = None
		icon = None
		
		if 'content' in attr:
			content = base64.b64decode(attr['content'])
			attr.pop('content')
		
		if 'icon' in attr:
			icon = base64.b64decode(attr['icon'])
			attr.pop('icon')
		
		attr.setdefault('createdBy', g.auth.resource)
		
		r = core.create('App', attr)
		
		if r:
			
			if content:
				r.setScript(content)
			
			if icon:
				r.setIcon(content)
			
			response = jsonEncodeFilterByFields(r, getParameter('fields',CHK_STRING_ARRAY, True))
			response.status_code = 201
			return response
		else:
			raise Exception('Unable to create the app');
	
	raise Exception('Invalid request');


@app.route('/api/apps/<id>', methods=['GET', 'PUT'])
@auth.required(GET = 'app:read resource:read', PUT = 'app:write resource:write')
def rapp(id):
	r = getResource(core, id, ['App'])
	
	if request.method == 'GET':
		
		content = r.readScript()
		
		if getParameter('exec',CHK_LOGIC,True,False):
			
			# replace some SUPER GLOBALS
			
			content = content.replace("__API_URL__", request.url_root + "api")
			content = content.replace("__API_KEY__", r.apikey)
			content = content.replace("__ID__", r.id)
			content = content.replace("__NAME__", r.name)
			
			return Response(content, mimetype = 'text/html')
			
		# for security reason, will not be executed in browsers
		return Response(content, mimetype = 'text/plain')
	
	elif request.method == 'PUT':
		
		r.setScript(request.data)
		
		return jsonEncodeFilterByFields(r, getParameter('fields',CHK_STRING_ARRAY, True))

@app.route('/api/files/<id>/icon', methods=['GET', 'PUT'])
@auth.required(GET = 'app:read resource:read', PUT = 'resource:admin')
def apps_icon(id):
	r = getResource(core, id, ['App'])
	
	if request.method == 'GET':
		icon = r.readIcon()
		
		if not icon:
			raise Exception('No icon available')
		
		return Response(icon, mimetype='image/png')
	
	elif request.method == 'PUT':
		
		r.setIcon(request.data)
		
		return jsonEncodeFilterByFields(r, getParameter('fields',CHK_STRING_ARRAY, True))


@app.route('/api/tables', methods=['POST'])
@auth.required('table:write resource:write')
def tables():
	
	attr = request.get_json()
	
	if isinstance(attr, dict):
		
		content = None
		
		if 'content' in attr:
			content = attr['content']
			attr.pop('content')
		
		attr.setdefault('createdBy', g.auth.resource)
		
		r = core.create('Table', attr)
		
		if r:
			
			if content:
				r.importData(content)
			
			response = jsonEncodeFilterByFields(r, getParameter('fields',CHK_STRING_ARRAY, True))
			response.status_code = 201
			return response
		else:
			raise Exception('Unable to create the table');
	
	raise Exception('Invalid request');


@app.route('/api/tables/<id>', methods=['GET', 'PUT', 'POST'])
@auth.required(GET = 'table:read resource:read', PUT = 'table:write resource:write', POST = 'table:write table:append resource:write')
def table(id):
	r = getResource(core, id, ['Table'])
	
	if request.method == 'GET':
		
		args = {}
		args['start'] = getParameter('START',CHK_INT,True,0)
		args['length'] = getParameter('LENGTH',CHK_UNSIGNED_INT,True)
		args['fields'] = getParameter('FIELDS',CHK_STRING_ARRAY,True)
		args['sort'] = getParameter('SORT',CHK_STRING,True)
		args['query'] = getParameter('Q',CHK_STRING,True)
		args['date_format'] = getParameter('DATEFMT',CHK_DATEFORMAT,True,date_formats['rfc3339'])
		
		format = getParameter('FMT',CHK_FORMAT,True,FMT_JSON)
		
		if format == FMT_JSON:
			return jsonify(r.select(**args))
		elif format == FMT_JSON_PRETTY:
			return jsonify(r.select(**args), indent=4)
		elif format == FMT_CSV or format == FMT_CSV_NOHEADER:
			args['show_header'] = format == FMT_CSV
			return Response(r.writeCSV(**args), mimetype='text/csv')
		
		raise Exception('Invalid request');
	
	elif request.method == 'PUT':
		
		data = request.get_json()
		
		invalidFieldMode = getParameter('INVALID_FIELD',CHK_INVALIDFIELDMODE,True,invalid_field_modes['rename'])
		skipError = getParameter('SKIP_ERROR',CHK_LOGIC,True,True)
		
		if data:
			r.importData(data,invalidFieldMode,skipError)
			return jsonEncodeFilterByFields(r, getParameter('fields',CHK_STRING_ARRAY, True))
		else:
			raise Exception('No data.');
	
	elif request.method == 'POST':
		
		data = request.get_json()
		
		invalidFieldMode = getParameter('INVALID_FIELD',CHK_INVALIDFIELDMODE,True,invalid_field_modes['rename'])
		
		if data:
			r.insert(data,invalidFieldMode)
			return jsonEncodeFilterByFields(r, getParameter('fields',CHK_STRING_ARRAY, True))
		else:
			raise Exception('No data.');

@app.route('/api/tables/<id>/<action>', methods=['POST'])
@auth.required('table:write resource:write')
def table_action(id, action):
	r = getResource(core, id, ['Table'])
	
	if action == 'remove':
		
		if request.json:
			ids = request.json
		else:
			ids = getParameter('id', None, True, '').split(',')
		
		if isinstance(ids, basestring):
			ids = [ids]
		
		if isinstance(ids, list) and len(ids)>0:
			for id in ids:
				if not ShortId.validate(id):
					raise Exception('Must be an array of record id.')
			
			nb = r.remove_rows(ids)
		
			if nb == len(ids):
				# all the specified documents/rows were removed
				return jsonEncodeFilterByFields(r, getParameter('fields',CHK_STRING_ARRAY, True))
			else:
				# all or only certain documents/rows could not have been removed
				raise Exception('Some or all documents could not have been removed.')
		
		raise Exception('The key ids must be an array of record id.')
		
		
	elif action == 'replace':
		
		query = getParameter('q',CHK_STRING)
		
		data = request.get_json()
		
		upsert = getParameter('UPSERT',CHK_LOGIC,True,False)
		invalidFieldMode = getParameter('INVALID_FIELD',CHK_INVALIDFIELDMODE,True,invalid_field_modes['rename'])
		
		if data:
			r.replaceRow(query, data, invalidFieldMode, upsert)
			return jsonEncodeFilterByFields(r, getParameter('fields',CHK_STRING_ARRAY, True))
		else:
			raise Exception('No data.');
		
	raise Exception('Invalid request');


@app.route('/api/tables/<id>/statistics')
@auth.required('table:read resource:read')
def table_statistics(id):
	r = getResource(core, id, ['Table'])
	
	key = getParameter('key',CHK_STRING);
	query = getParameter('q',CHK_STRING, True);
	
	return jsonify(r.computeStatistics(key, query))


@app.route('/api/tables/<id>/id/<doc_id>', methods=['GET', 'DELETE', 'PATCH'])
@auth.required(GET = 'table:read resource:read', DELETE = 'table:write resource:write', PATCH = 'table:write resource:write')
def table_cell_id(id, doc_id):
	r = getResource(core, id, ['Table'])
	
	if request.method == 'GET':
		
		doc = r.getRow(doc_id)
		
		if doc is None:
			raise Exception('The document with id=%s does not exist.' % doc_id)
		
		return jsonEncodeFilterByFields(doc, getParameter('fields',CHK_STRING_ARRAY, True))
	
	elif request.method == 'DELETE':
		r.remove_row(doc_id)
		return ('', 204)
	
	elif request.method == 'PATCH':
		
		data = request.get_json()
		invalidFieldMode = getParameter('INVALID_FIELD',CHK_INVALIDFIELDMODE,True,invalid_field_modes['rename'])
		
		if data:
			doc = r.replaceRowById(doc_id, data, invalidFieldMode)
			if doc:
				return jsonEncodeFilterByFields(doc, getParameter('fields',CHK_STRING_ARRAY, True))
			else:
				raise Exception('The document with id=%s does not exist.' % doc_id)
		else:
			raise Exception('No data')


@app.route('/api/devices', methods=['POST'])
@auth.required('device:write resource:write')
def devices():
	
	attr = request.get_json()
	
	if isinstance(attr, dict):
		
		if 'type' not in attr:
			raise Exception('the "type" attribute is mandatory')
		
		type = attr.pop('type')
		content = None
		
		if type == 'Http':
			content = attr.pop('content', None)
		elif type == 'MQTT':
			content = attr.pop('subscription', None)
		
		attr.setdefault('createdBy', g.auth.resource)
		
		r = core.create(type, attr)
		
		if r:
			
			if content:
				if r.type == 'Http':
					r.setSpecification(base64.b64decode(content))
				elif r.type == 'MQTT':
					r.setSubscription(content)
			
			response = jsonEncodeFilterByFields(r, getParameter('fields',CHK_STRING_ARRAY, True))
			response.status_code = 201
			return response
		else:
			raise Exception('Unable to create the device (type = %s)' % type);
	
	raise Exception('Invalid request')


@app.route('/api/devices/<id>/api')
@auth.required('device:read resource:read')
def device_apis(id):
	r = getResource(core, id, ['Device'])
	return jsonify(r.interface)


@app.route('/api/devices/<id>/api/<operationId>')
@auth.required('device:read resource:read')
def device_api(id, operationId):
	r = getResource(core, id, ['Device'])
	return jsonify(r.interface.get_method(operationId))


@app.route('/api/devices/<id>/call/<operationId>', methods=['GET', 'POST'])
@auth.required('device:write resource:write')
def device_api_call(id, operationId):
	r = getResource(core, id, ['Device'])
	
	method = r.interface.get_method(operationId)
	
	args = []
	kwargs = {}
	
	if request.method == 'GET':
		
		for arg_name in list(set(request.args.keys()).intersection(method.args.keys())):
			kwargs[arg_name] = method.args[arg_name]
		
	elif request.method == 'POST':
		try:
			data = request.get_json()
			if isinstance(data, dict):
				kwargs = data
			elif isinstance(data, list):
				args = data
			else:
				args.append(data)
		except:
			pass
	
	return_type = method.return_type
	
	if return_type:
		
		if re.search('^[^/]+/[^/]+$', return_type):
			return Response(method.call(*args, **kwargs), mimetype=return_type)
		else:
			return jsonify(method.call(*args, **kwargs))
		
	else:
		method.call(*args, **kwargs)
		return ('', 204)


@app.route('/api/devices/<id>/specification')
@auth.required('device:read resource:read')
def device_http_specification(id):
	r = getResource(core, id, ['Http'])
	return jsonify(r.getSpecification())


@app.route('/api/devices/<id>/subscription')
@auth.required('device:read resource:read')
def device_mqtt_subscription(id):
	r = getResource(core, id, ['MQTT'])
	return jsonify(r.getSubscription())


@app.route('/api/rules', methods=['GET', 'POST'])
@auth.required(GET = 'rule:read', POST = 'rule:write')
def rules():
	
	if request.method == 'GET':
		return jsonEncodeFilterByFields(core.findRules(), getParameter('fields',CHK_STRING_ARRAY, True))
	
	elif request.method == 'POST':
		
		data = request.get_json()
		
		if isinstance(data, dict):
			rule = core.createRule(data)
			if rule:
				response = jsonEncodeFilterByFields(rule, getParameter('fields',CHK_STRING_ARRAY, True))
				response.status_code = 201
				return response
			else:
				raise Exception('Unable to create the rule');
		
		raise Exception('Invalid request');


@app.route('/api/rules/<id>', methods=['GET', 'DELETE', 'PATCH'])
@auth.required(GET = 'rule:read', DELETE = 'rule:admin', PATCH = 'rule:admin')
def rule(id):
	
	rules = core.findRules({
		'_id' : id
	});
	
	if len(rules) == 0:
		raise Exception('Unknown rule with id = %s' % id);
	
	rule = rules[0]
	
	if request.method == 'GET':
		return jsonEncodeFilterByFields(rule, getParameter('fields',CHK_STRING_ARRAY, True))
	
	elif request.method == 'DELETE':
		rule.remove()
		return ('', 204)
	
	elif request.method == 'PATCH':
		
		data = request.get_json()
		
		if isinstance(data, dict) and rule.set(data):
			return jsonEncodeFilterByFields(rule, getParameter('fields',CHK_STRING_ARRAY, True))
		
		raise Exception('Invalid request');


@app.route('/api/notification', methods=['POST'])
@auth.required('notification')
def notify():
	data = request.get_json()
	if isinstance(data, dict):
		data.setdefault('subject', None)
		data.setdefault('body', None)
		core.notify(data['subject'], data['body'])
	else:
		raise Exception('Invalid request');


# SSE "protocol" is described here: http://mzl.la/UPFyxY
@app.route('/api/events')
@auth.required()
def events():
	
	def gen():
		
		client = core.rpc.subscribe('signal')
		
		try:
			while True:
				msg = client.get()
				if msg is None:
					# rpc server disconnected
					break
				signal = msg.message
				
				data = toJson(signal)
				
				lines = ["data:{value}".format(value=line) for line in data.splitlines()]
				lines.insert(0, "event:message")
				
				yield "\n".join(lines) + "\n\n"
				
		except GeneratorExit: # Or maybe use flask signals
			client.stop()
	
	return Response(gen(), mimetype="text/event-stream")


@app.route('/utils/serial_ports_list')
@auth.required()
def serial_ports_list():
	import serial.tools.list_ports

	ports = list(serial.tools.list_ports.comports())

	info = [];

	for port in ports:
		info.append({
			'device': port.device,
			'name': port.name,
			'description': port.description,
			'hwid': port.hwid,
			'vid': port.vid,
			'pid': port.pid,
			'serial_number': port.serial_number,
			'location': port.location,
			'manufacturer': port.manufacturer,
			'product': port.product,
			'interface': port.interface
		})


	return jsonify(info, indent=4)

	
@app.route('/utils/net_list')
@auth.required()
def net_list():
	import ething.utils.net_scan
	return jsonify(ething.utils.net_scan.scan(), indent=4)



@app.route('/utils/read_log')
@auth.required()
def read_log():
	logfilename = None
	lines = []
	linenb = getParameter('line',CHK_UNSIGNED_INT, 50)
	
	for h in core.log.handlers:
		try:
			logfilename = h.baseFilename
			break
		except:
			pass
	
	def tail(fname, lines):
		bufsize = 8192
		fsize = os.stat(fname).st_size

		iter = 0
		data = []
		with open(fname) as f:
			if bufsize > fsize:
				bufsize = fsize-1
			while True:
				iter +=1
				f.seek(fsize-bufsize*iter)
				data.extend(f.readlines())
				if len(data) >= lines or f.tell() == 0:
					break
		
		return [ l.strip() for l in data[-lines:]]

	if logfilename:
		lines = tail(logfilename, linenb)
	
	return jsonify(lines)





@app.errorhandler(Exception)
def unhandled_exception(e):
	return error_handler(e)

for cls in HTTPException.__subclasses__():
	app.register_error_handler(cls, error_handler)




def run(core_):
	global app, core, debug
	
	core = core_
	
	core.log.info("web server root path = %s" % root_path)
	
	debug = bool(core.config['debug'])
	
	install_auth(app, core)
	
	app.run(host='0.0.0.0', port=core.config['webserver']['port'], threaded=True)
	
	return


if __name__ == "__main__": 
	
	from ething.core import Core
	
	core = Core({
		'db':{
			'database': 'test'
		},
		'webserver': {
			'port': 8000
		},
		'log': {
			'level': 'DEBUG'
		}
	})
	
	run(core)


