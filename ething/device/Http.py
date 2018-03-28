
	

"""
 @swagger-definition
 "Http":{ 
   "type": "object",
   "description": "Http Device resource representation",
	 "allOf": [
		{
		   "$ref":"#/definitions/Device"
		},
		{  
		   "type": "object",
		   "properties":{
			 "url": {
				  "type":"string",
				  "description":"The URL of the device, or null if there is none defined. No URL defined means that the device cannot be reached.
Only device with an URL set has a Swagger specification (see /device/<id>/specification endpoint).
The specification object define all the available HTTP requests this device accepts."
			   },
			 "scope": {
				  "type":"string",
				  "description":"
The allowed scopes for this device (space separated list). Restrict the Http api access.
Default to an empty string (no access).
"
			   },
			 "auth": {
				"type":"object",
				  "properties":{  
					"type":{
					   "type":"string",
					   "enum":["basic","digest"],
					   "description":"the HTTP authentication method to use."
					},
					"user":{  
					   "type":"string",
					   "description":"the username to use for the authentication."
					},
					"password":{  
					   "type":"string",
					   "description":"the password to use for the authentication."
					}
				},
				  "description":"An object describing the authentication method to use on HTTP request."
			   },
			 "apikey": {
				  "type":"string",
				  "description":"The apikey for authenticating this device.",
				  "readOnly": true
			   }
		   }
		}
   ]
 }
"""


from ething.Device import Device, method, attr, isString, isNone, isObject, READ_ONLY, PRIVATE, Validator
from ething.utils import pingable
import urlparse
from ething.Scope import Scope
from ething.ApiKey import ApiKey
import json
from ething.swagger import Reader
import requests





class ScopeValidator(Validator):
	def validate(self, value):
		if not Scope.validate(value):
			raise ValueError('not a valid scope')


@pingable
@attr('url', validator = isNone() | isString(allow_empty = False, regex = '^https?://'), default = None)
@attr('scope', validator = isString() & ScopeValidator(), default = '')
@attr('auth', validator = isNone() | isObject(user=isString(allow_empty=False), password=isString(allow_empty=False), type=isString(enum=['basic', 'digest'])), default=None)
@attr('#apikey', default = lambda _: ApiKey.generate(), mode = READ_ONLY)
@attr('specification', default = None, mode = PRIVATE)
class Http(Device):
	
	
	
	@property
	def apikey (self):
		return getattr(self, '#apikey')
	
	@property
	def isServer (self):
		return self.url is not None
	
	
	@property
	def isAuthenticate (self):
		return bool(self.auth)
	
	@property
	def authMode (self):
		return self.auth.get('type', None) if self.auth else None
	
	@property
	def authUser (self):
		return self.auth.get('user', None) if self.auth else None
	
	@property
	def authPassword (self):
		return self.auth.get('password', None) if self.auth else None
	
	
	def dynamic_interface(self):
		
		if not self.isServer:
			return
		
		reader = Reader(self.getSpecification())
		
		def generate_dyn_method(op):
			
			response = None
			produces = op.produces
			if produces:
				response = produces[0]
			
			
			@method.bind_to(self)
			@method.name(op.name)
			@method.description(op.description)
			@method.return_type(response)
			def req(self, **kwargs):
				
				request_ = op.createRequest(kwargs)
				
				# cf. https://gist.github.com/gear11/8006132
				
				r = self.make_request(request_['url'], method = request_['method'], headers = request_['headers'], body = request_['body'])
				
				content_type = r.headers.get('content-type', None)
				content_length = r.headers.get('content-length', None)
				isjson = False
				stream = False
				
				if content_type == 'application/json':
					isjson = True
					stream = False
				else:
					if content_length is None or content_length > 15000:
						stream = True
				
				if stream:
					
					def generate():
						try:
							for chunk in r.iter_content(1024):
								yield chunk
						except:
							r.close()
					
					return generate()
				
				else:
					if isjson:
						try:
							content = json.loads(r.content)
						except:
							content = r.content
					else:
						content = r.content
						
					return content
			
			
			if op.parameters:
				
				# call the method.arg in reverse order to preserve the original argument order (first decorator call correspond to the last argument !)
				# 
				# method.arg('arg2')(req)
				# method.arg('arg1')(req)
				# 
				# is equivalent to
				#
				# @method.arg('arg1')
				# @method.arg('arg2')
				# def req(arg1, arg2):
				#    ...
				for param in reversed(op.parameters): 
					schema = param.toJsonSchema()
					method.arg(param.name, required=param.isRequired, **schema)(req)
			
		
		
		for op in reader.operations:
			generate_dyn_method(op)
		
	
	
	def make_request(self, path, method = 'get', headers = {}, body = None ):
		
		auth = None
		
		ref = urlparse.urlsplit(self.url)
		new = urlparse.urlsplit(path)
		
		# join path
		path = ref.path.rstrip('/') + '/' + new.path.lstrip('/')
		
		# join the query string
		query = dict_recursive_update({}, urlparse.parse_qs(ref.new), urlparse.parse_qs(ref.query))
		
		if self.isAuthenticate and self.authMode == 'query':
			query['user'] = [self.authUser]
			query['password'] = [self.authPassword]
		
		q = []
		for k,vv in query.iteritems():
			for v in vv:
				q.append((k,v))
		
		query = urllib.urlencode(q)
		
		url = urlparse.urlunparse((ref.scheme, ref.netloc, path, '', query, ''))
		
		self.ething.log.debug("Http request: %s", url)
		
		if self.isAuthenticate:
			if self.authMode == 'basic':
				auth = requests.auth.HTTPBasicAuth(self.authUser, self.authPassword)
			elif self.authMode == 'digest':
				auth = requests.auth.HTTPDigestAuth(self.authUser, self.authPassword)
		
		s = requests.Session()
		if auth is not None:
			s.auth = auth
		
		#s.config['keep_alive'] = False # cf. https://stackoverflow.com/questions/10115126/python-requests-close-http-connection
		
		req = requests.Request(method.upper(), url, headers)
		prepped = s.prepare_request(req)
		
		if body:
			prepped.body = body
		
		resp = s.send(prepped,
			timeout=(6.05, 15)
		)
		
		self.ething.log.debug("Http response: %d", resp.status_code)
		
		return resp


	@staticmethod
	def checkSpecification (ething, swagger):
		
		# sanitize the specification
		if isinstance(swagger, basestring):
			swagger = json.loads(swagger)
		
		
		swagger = dict_recursive_update({
			'swagger': '2.0',
			'info':{
				'title': "untitled",
				'version': '0.1.0'
			},
			'paths': {}
		}, swagger)
		
		r = requests.post("http://online.swagger.io/validator/debug", data=json.dumps(swagger))
		
		if r.status_code != 200:
			raise Exception('unable to reach http://online.swagger.io/validator/debug')
		
		# the response must be valid JSON data containing an array of errors
		try:
			result = json.loads(r.text)
		except:
			result = None
		
		if result:
			
			if isinstance(result, dict) and 'schemaValidationMessages' in result:
				message = result['schemaValidationMessages'][0]['message']
			else:
				message = 'unknown error'
			
			raise Exception('invalid swagger API specification: %s' % message)
		
		
		return swagger
	
	
	
	def setSpecification (self, swagger):
		if not self.isServer:
			raise Exception('this device has no URL set')
		
		if isinstance(swagger, basestring):
			# must be json !
			swagger = json.loads(swagger)
		
		self.ething.fs.removeFile(self._specification)
		self._specification = None
		
		if swagger is not None:
			self._specification = self.ething.fs.storeFile('Device/%s/specification' % self.id, json.dumps(swagger), {
				'parent' : self.id
			})
		
		self.update_interface()
	
	
	
	def getSpecification (self):
		if not self.isServer:
			raise Exception('this device has no API specification')
		spec = self.ething.fs.retrieveFile(self._specification)
		return json.loads(spec) if spec else self.defaultSpecification()
	
	
	def defaultSpecification(self):
		# return a minimal swagger object
		return {
			'swagger': '2.0',
			'info':{
				'title': self.name,
				'version': '0.1.0'
			},
			'paths': {}
		}
	
	
	
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
	
	name = 'http.device.test'
	
	device = ething.findOne({
		'name': name
	})
	
	#if device :
	#	device.remove()
	#	device = None
	
	if not device:
		device = ething.create('Http', {
			'name': name,
			'url': 'http://localhost'
		})
		
		import urllib2
		contents = urllib2.urlopen("https://raw.githubusercontent.com/OAI/OpenAPI-Specification/master/examples/v2.0/json/petstore.json").read()
		
		device.setSpecification(contents)
	
	
	print device
	
	print json.dumps(device.interface.toJson(), indent=4)
	
	#print Http.checkSpecification(None, {})
	



