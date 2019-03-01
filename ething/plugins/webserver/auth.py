# coding: utf-8
from future.utils import string_types
from flask import g, request
from .session import Session
from .apikey import Apikey
from functools import wraps
import re
from netaddr import IPAddress
from .server_utils import ServerException


class AuthContext(object):

    def __init__(self, type, scope=None, resource=None):
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

        if isinstance(self.scope, string_types):  # check permissions

            permissions = [p for p in permissions.split(" ") if p]
            scopes = [s for s in self.scope.split(" ") if s]

            for scope in scopes:
                if scope in permissions:
                    return True

        return False


class Auth(object):

    def __init__(self, app, config):
        self.app = app
        self.core = app.core
        self.config = config
        self.session = Session(config)

    def required(self, *args, **type_specific_perms):

        global_permissions = ' '.join(args)

        def d(f):
            @wraps(f)
            def wrapper(*args, **kwds):

                permissions = ' '.join(
                    [global_permissions, type_specific_perms.get(request.method, '')]).strip()

                self.check(permissions)

                return f(*args, **kwds)
            return wrapper
        return d

    def check(self, permissions = None):

        authctx = self.check_localhost() or self.check_session() or self.check_apikey() or self.check_basic() or self.check_public()

        if authctx and isinstance(authctx, AuthContext):
            g.auth = authctx

            if permissions:
                if not authctx.check_permissions(permissions):
                    raise ServerException('not authorized', 403)

            return

        raise ServerException('not authenticated', 401)

    def check_localhost(self):
        if request.remote_addr == '127.0.0.1' and self.config['auth']['no_auth_for_localhost']:
            return AuthContext('localhost')

    def check_session(self):
        if self.session and self.session.isAuthenticated(request, False):
            return AuthContext('session')

    def check_apikey(self):
        apikey_value = request.headers.get(
            'HTTP_X_API_KEY') or request.args.get('api_key')

        if apikey_value:
            apikeys = self.core.db.os.find(Apikey, lambda x: x.value == apikey_value)

            if len(apikeys) > 0:
                apikey = apikeys[0]
                return AuthContext('apikey', scope=apikey.scope, resource=None)
            else:
                raise ServerException('invalid apikey', 401)

    def check_basic(self):

        auth = request.authorization

        if auth:
            if auth.username == self.config.get('auth', {}).get('username') and auth.password == self.config.get('auth', {}).get('password'):
                return AuthContext('basic')
            else:
                raise ServerException('invalid credentials', 401)

    def check_public(self):
        matches = re.search(
            '^/api/([^/]+)/([a-zA-Z0-9_-]{7})($|/|\\?)', str(request.path))

        if matches:
            id = matches.group(2)
            resource = self.core.get(id)
            if resource:
                public = resource.public
                if public == 'readonly':
                    return AuthContext('public', scope='resource:read')
                elif public == 'readwrite':
                    return AuthContext('public', scope='resource:read resource:write device:execute')


def install_auth(app):

    auth = Auth(app, app.conf)

    if app.conf['auth']['localonly']:
        @app.before_request
        def check_local_only():

            ip = IPAddress(request.remote_addr)

            if not (ip.is_private() or ip.is_loopback()):
                raise ServerException('not allowed', 403)

    return auth
