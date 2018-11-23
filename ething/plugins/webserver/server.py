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
        self.app = FlaskApp(self.core, config=self.config, logger=self.log, root_path=root_path)

    def start(self):
        super(WebServer, self).start()
        self.start_process()

    def stop(self):
        super(WebServer, self).stop()
        self.stop_process()

    def start_process(self):
        self.process = WebServerProcess(self.app)
        self.process.start()

    def stop_process(self):
        if hasattr(self, 'process'):
            self.process.stop()
            del self.process

    def export_data(self):
        return [apikey.export_instance() for apikey in self.app.apikey_manager.list()]

    def import_data(self, data):
        akm = self.app.apikey_manager
        for apikey in data:
            Apikey.import_instance(apikey, context={'manager': akm})


class FlaskApp(Flask):

    def __init__(self, core, config=None, logger = None, **kwargs):
        kwargs.setdefault('static_url_path', '')
        super(FlaskApp, self).__init__(__name__, **kwargs)

        self.core = core
        self._config = config

        if logger is None:
            self.log = logging.getLogger("ething.FlaskApp")
        else:
            self.log = logger

        # debug
        self.debug = bool(self._config.get('debug'))
        if self.debug:
            self.log.info('webserver: debug mode enabled')

        # for PATCH request
        self.wsgi_app = HTTPMethodOverrideMiddleware(self.wsgi_app)

        #CORS
        cors_opt = {"origins": "*", "supports_credentials": True}

        CORS(self, resources={
            r"/api/*": cors_opt,
            r"/auth/*": cors_opt
        })

        # compress
        compress = Compress()
        compress.init_app(self)

        # auth
        self.auth = install_auth(self, self._config)

        # socketio
        socketio = SocketIO()
        socketio.init_app(self, async_mode='eventlet', logger=self.debug, engineio_logger=self.debug)
        self.socketio = socketio

        @socketio.on('connect')
        def connect_handler():
            self.auth.check()

        #logging
        logging.getLogger('werkzeug').setLevel(logging.ERROR)

        #error handler
        @self.errorhandler(Exception)
        def unhandled_exception(e):
            return self.error_handler(e)

        for cls in HTTPException.__subclasses__():
            self.register_error_handler(cls, self.error_handler)

        # apikeys manager
        self.apikey_manager = ApikeyManager(core)

        self.running = threading.Event()

        # routes
        install_routes(core=self.core, app=self, auth=self.auth, debug=self.debug)

    def run(self):
        port = self._config.get('port', 80)

        # retrieve current ip:
        current_ip = None
        try:
            current_ip = [l for l in (
                [ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")][:1], [
                    [(s.connect(('8.8.8.8', 53)), s.getsockname()[0], s.close()) for s in
                     [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) if l][0][0]
        except:
            pass

        self.log.info("web server started at http://%s:%d" % (current_ip or 'localhost', port))
        self.log.info("web server root path = %s" % self.root_path)

        self.running.set()

        self.socketio.run(self, host='0.0.0.0', port=port, use_reloader=False, minimum_chunk_size=0)

    def stop(self):
        self.running.clear()

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
    def __init__(self, app):
        super(WebServerProcess, self).__init__(name='webserver')
        self.app = app

    def stop(self):
        self.app.stop()
        super(WebServerProcess, self).stop()

    def main(self):
        self.app.run()

