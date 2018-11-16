# coding: utf-8

from flask import Flask, Response, request, g
from flask_cors import CORS
from flask_compress import Compress
from flask_socketio import SocketIO
from werkzeug.exceptions import HTTPException
from werkzeug.http import unquote_etag
from .auth import install_auth
from .routes import install_routes
import json
import traceback
import logging
import socket
import datetime
import pytz
import threading
from future.utils import binary_type, string_types
from .method_override import HTTPMethodOverrideMiddleware
from .server_utils import ServerException, tb_extract_info, root_path, use_args, use_multi_args
from .apikey import ApikeyManager, Apikey
from ething.core.plugin import Plugin
from ething.core.Process import Process
from ething.core.Helpers import filter_obj
from ething.core.reg import get_registered_class
from collections import OrderedDict

try:
    from cheroot.wsgi import Server as WSGIServer
except ImportError:
    from cherrypy.wsgiserver import CherryPyWSGIServer as WSGIServer


use_eventlet=True


class WebServer(Plugin):
    CONFIG_DEFAULTS = {
        'port': 8000,
        'debug': True,
        'auth': {
            'username': 'ething',
            'password': 'admin',
            'localonly': False
        },
        'session': {
            'expiration': 86400,  # in seconds, the time after which a session is expired
            'cookie_name': 'ething_session',
            'secret': 'taupesecretstring'  # must not be shared
        },
    }

    CONFIG_SCHEMA = {
        'type': 'object',
        'properties': OrderedDict([
            ('port', {
                'type': 'integer',
                'minimum': 1,
                'maximum': 65535
            }),
            ('auth', {
                'type': 'object',
                'required': ['username', 'password'],
                'properties': OrderedDict([
                    ('username', {
                        'type': 'string',
                        'minLength': 1
                    }),
                    ('password', {
                        'type': 'string',
                        "format": "password",
                        'minLength': 4
                    }),
                    ('localonly', {
                        'type': 'boolean'
                    })
                ])
            })
        ])
    }

    def load(self):
        super(WebServer, self).load()

        if not hasattr(self, '_installers'):
            self._installers = []

    def start(self):
        super(WebServer, self).start()
        self.start_process()

    def stop(self):
        super(WebServer, self).stop()
        self.stop_process()

    def on_config_change(self):
        self.stop_process()
        self.start_process()

    def start_process(self):
        self.process = WebServerProcess(self.core, self.config, custom_installers = getattr(self, '_installers', None))
        self.process.start()

    def stop_process(self):
        if hasattr(self, 'process'):
            self.process.stop()
            del self.process

    def export_data(self):
        akm = ApikeyManager(self.core)
        return [apikey.export_instance() for apikey in akm.list()]

    def import_data(self, data):
        akm = ApikeyManager(self.core)
        for apikey in data:
            Apikey.import_instance(apikey, context={'manager': akm})

    def register_installer(self, installer):
        if not hasattr(self, '_installers'):
            self._installers = []
        self._installers.append(installer)

    def unregister_installer(self, installer):
        if hasattr(self, '_installers') and installer in self._installers:
            self._installers.remove(installer)
            # restart webserver if it was started
            if hasattr(self, 'process'):
                self.stop_process()
                self.start_process()


class FlaskApp(Flask):

    def __init__(self, core, log = None, **kwargs):
        kwargs.setdefault('static_url_path', '')
        super(FlaskApp, self).__init__(__name__, **kwargs)

        self.core = core

        if log is None:
            self.log = logging.getLogger("ething.FlaskApp")
        else:
            self.log = log

        # for PATCH request
        self.wsgi_app = HTTPMethodOverrideMiddleware(self.wsgi_app)

        #CORS
        cors_opt = {"origins": "*", "supports_credentials": True}

        CORS(self, resources={
            r"/api/*": cors_opt,
            r"/auth/*": cors_opt
        })

        #logging
        logging.getLogger('werkzeug').setLevel(logging.ERROR)

        # debug
        self.debug = bool(self.core.config.get('debug'))
        if self.debug:
            self.log.info('webserver: debug mode enabled')

        #error handler
        @self.errorhandler(Exception)
        def unhandled_exception(e):
            return self.error_handler(e)

        for cls in HTTPException.__subclasses__():
            self.register_error_handler(cls, self.error_handler)

        # apikeys manager
        self.apikey_manager = ApikeyManager(core)


    def error_handler(self, e):

        error = {
            'message': str(e),
            'code': 400
        }

        if isinstance(e, HTTPException):
            error['code'] = e.get_response().status_code
        elif isinstance(e, ServerException):
            error['code'] = e.status_code

        if self.debug:
            file, line = tb_extract_info()
            error['stack'] = traceback.format_exc()
            error['file'] = file
            error['line'] = line

            self.log.exception('http request exception')

        return Response(json.dumps(error), status=error['code'], mimetype='application/json')

    def jsonify(self, obj, **kwargs):

        fields = request.args.get('fields')

        if fields is not None:
            fields = fields.replace(' ', ',').replace(
                ';', ',').replace('|', ',').split(',')

        return Response(self.toJson(obj, **kwargs), mimetype='application/json')

    def toJson(self, obj, fields=None, **kwargs):

        # filter by keys
        if fields is not None:
            if isinstance(obj, dict):
                obj = filter_obj(obj, fields)
            elif isinstance(obj, list):
                obj = [filter_obj(o, fields) for o in obj]

        return json.dumps(obj, default=self.serialize, **kwargs)

    def serialize(self, obj):
        """JSON serializer for objects not serializable by default json code"""
        if hasattr(obj, 'toJson'):
            return obj.toJson()
        if isinstance(obj, datetime.datetime):
            return obj.replace(tzinfo=pytz.utc).astimezone(self.core.local_tz).isoformat()
        if isinstance(obj, binary_type):
            return obj.decode('utf8')
        return obj.__dict__

    def getResource(self, id, restrictToTypes=None):

        message = 'resource with id="%s" not found or has not the right type' % id

        authenticated = hasattr(g, 'auth')

        if id == 'me' and authenticated and g.auth.resource:
            # special case, needs api key auth
            r = g.auth.resource
        else:
            r = self.core.get(id)

        if r is None:
            raise Exception(message)

        if restrictToTypes is not None:
            ok = False
            for type in restrictToTypes:
                if r.isTypeof('resources/' + type):
                    ok = True
                    break
            if not ok:
                raise Exception(message)

        if authenticated:
            scope = g.auth.scope

            if scope is not None:

                scopes = [s for s in g.auth.scope.split(" ") if s]

                allowed_types = []
                for scope in scopes:
                    type = scope.split(':')[0].capitalize()
                    if type not in allowed_types:
                        allowed_types.append(type)

                if 'Resource' not in allowed_types:
                    # restrict the search to the allowed_types
                    ok = False
                    for allowed_type in allowed_types:
                        if r.isTypeof('resources/' + allowed_type):
                            ok = True
                            break
                    if not ok:
                        raise Exception(message)

        return r

    def create(self, type, attr):
        cls = get_registered_class(type)
        if cls is not None:
            instance =  cls.fromJson(attr, context = {'ething': self.core})
            instance.save()
            return instance
        else:
            raise Exception('the type "%s" is unknown' % type)

    def etag_match(self, etag):
        req_etag = request.headers.get('If-None-Match')
        if req_etag and etag == unquote_etag(req_etag)[0]:
            return True
        return False

    def set_etag(self, resp, etag = None):
        if etag is not None:
            resp.set_etag(etag)
            resp.headers['Cache-Control'] = 'must-revalidate'
        return resp


class WebServerProcess(Process):
    def __init__(self, core, config=None, custom_installers = None):
        super(WebServerProcess, self).__init__('webserver')
        self.core = core
        self.config = config or {}
        self.debug = False
        self.server = None
        self.auth = None
        self.app = FlaskApp(self.core, self.log, root_path=root_path)
        self.custom_installers = custom_installers or []

    def stop(self):
        if self.server:
            self.server.stop()

        super(WebServerProcess, self).stop()

    def end(self):
        self.server = None

    def main(self):

        self.log.info("web server root path = %s" % root_path)

        compress = Compress()
        compress.init_app(self.app)

        if use_eventlet:
            socketio = SocketIO()
            socketio.init_app(self.app, async_mode='eventlet', logger=True, engineio_logger=True)
            self.socketio = socketio

        port = self.config['port']

        if not use_eventlet:
            self.server = WSGIServer(
                bind_addr=('0.0.0.0', port),
                wsgi_app=self.app,
                server_name=socket.gethostname()
            )

        auth = install_auth(core=self.core, app=self.app, config=self.config, debug=self.debug, server = self)

        self.auth = auth

        install_route_args = dict(core=self.core, app=self.app, auth=auth, debug=self.debug, server = self)

        install_routes(**install_route_args)

        # install registered routes :
        for installer in self.custom_installers:
            installer(**install_route_args)

        # retrieve current ip:
        current_ip = None
        try:
            current_ip = [l for l in (
            [ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")][:1], [
                [(s.connect(('8.8.8.8', 53)), s.getsockname()[0], s.close()) for s in
                 [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) if l][0][0]
        except:
            pass

        self.log.info("webserver: started at http://%s:%d" % (current_ip or 'localhost', port))

        if use_eventlet:
            socketio.run(self.app, host='0.0.0.0', port=port, use_reloader=False, minimum_chunk_size=0)
        else:
            self.server.start()

    def install_route(self, url, fn, **options):

        endpoint = options.pop('endpoint', fn.__name__)

        if self.app:
            view_func = fn

            # handle permissions
            permissions = options.pop('permissions', '')
            if permissions is not False:
                view_func = self.auth.required(permissions)(view_func)

            #args
            args = options.pop('args', None)
            if args:
                view_func = use_args(args)(view_func)

            self.app.add_url_rule(url, endpoint, view_func=view_func, **options)
        else:
            self.log.error('unable to install route "%s" : %s' % (endpoint, url))

