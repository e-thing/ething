from flask import redirect,request,url_for, make_response, send_from_directory, g
from session import Session
import os
from functools import wraps
import re
from netaddr import IPAddress


class AuthContext(object):
	
	def __init__(self, type, scope = None, resource = None):
		self._type = type
		self._scope = scope
		self._resource = resource
	
	@property
	def scope(self):
		return self._scope
	
	@property
	def resource(self):
		return self._resource
	
	@property
	def type(self):
		return self._type
	
	def check_permissions(self, permissions):
		
		if self.scope is None:
			return True
		
		if isinstance(self.scope, basestring): # check permissions
			
			permissions = filter(None, permissions.split(" "))
			scopes = filter(None, self.scope.split(" "))
			
			for scope in scopes:
				if scope in permissions:
					return True
		
		return False


class Auth(object):
	
	def __init__(self, core):
		self.core = core
	
	
	def required(self, *args, **type_specific_perms):
		
		global_permissions = ' '.join(args)
		
		def d(f):
			@wraps(f)
			
			def wrapper(*args, **kwds):
				
				permissions = ' '.join([global_permissions, type_specific_perms.get(request.method, '')]).strip()
				
				self.check(permissions)
				
				return f(*args, **kwds)
			return wrapper
		return d
	
	
	def check(self, permissions):
		
		authctx = self.check_session() or self.check_apikey() or self.check_basic() or self.check_public()
		
		if authctx and isinstance(authctx, AuthContext):
			g.auth = authctx
			
			if permissions:
				if not authctx.check_permissions(permissions):
					raise Exception('not authorized')
			
			return
		
		raise Exception('not authenticated')
	
	
	
	def check_session(self):
		if session and session.isAuthenticated(request, False):
			return AuthContext('session')
	
	
	def check_apikey(self):
		apikey = request.headers.get('HTTP_X_API_KEY') or request.args.get('api_key')
		
		if apikey:
			
			authenticated_resource = self.core.findOne({
				'#apikey' : apikey
			})
			
			if authenticated_resource:
				return AuthContext('apikey', scope = authenticated_resource.scope, resource = authenticated_resource)
			else:
				raise Exception('invalid apikey')
	
	
	def check_basic(self):
		
		auth = request.authorization
		
		if auth :
			if auth.username == 'ething' and auth.password == self.core.config['auth']['password']:
				return AuthContext('basic')
			else:
				raise Exception('invalid credentials')
			
	
	def check_public(self):
		
		matches = re.search('^/api/([^/]+)/([a-zA-Z0-9_-]{7})($|/|\\?)', str(request.url_rule))
		
		if matches:
			id = matches.group(1)
			resource = self.core.get(id)
			
			if resource:
				
				public = resource.public
				
				if public == 'readonly':
					g.scope = 'resource:read'
					return AuthContext('public', scope = 'resource:read')
				elif public == 'readwrite':
					return AuthContext('public', scope = 'resource:read resource:write')
				
	

session = None
auth = Auth(None)

def install_auth(app, core):
	global session, auth
	
	auth.core = core
	
	dir_html = os.path.abspath(os.path.dirname(__file__))

	session = Session(core)
	
	if core.config['auth']['localonly']:
		@app.before_request
		def check_local_only():
			
			ip = IPAddress(request.remote_addr)
			
			if not (ip.is_private() or ip.is_loopback()):
				raise Exception('not allowed')
	
	
	@app.route('/auth/password', methods=['POST'])
	def auth_password():
		
		password = request.values.get('password')
		redirect_uri = request.values.get('redirect_uri') or url_for('root_client')
		
		if len(password) > 0:
			resp = make_response(redirect(redirect_uri))
			if session.authenticate(password, request, resp):
				return resp
			
		
		raise Exception('invalid authentication credentials !')



	@app.route('/auth/logout')
	def auth_logout():
		
		redirect_uri = request.values.get('redirect_uri') or ''
		
		resp = make_response(redirect(url_for('auth_login', redirect_uri = redirect_uri)))
		
		session.unauthenticate(request, resp)
		
		return resp
		

	@app.route('/auth/login')
	def auth_login():
		
		redirect_uri = request.values.get('redirect_uri') or url_for('root_client')
		
		if session.isAuthenticated(request):
			
			return redirect(redirect_uri)
		
		else:
			core.log.info(dir_html)
			return send_from_directory(dir_html, 'login.html')




	