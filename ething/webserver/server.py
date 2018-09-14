# coding: utf-8

from flask import Flask, Response, request, g
from flask_cors import CORS
from flask_compress import Compress
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
from future.utils import binary_type
from .method_override import HTTPMethodOverrideMiddleware
from .server_utils import ServerException, tb_extract_info, root_path
from ething.core.plugin import Plugin
from ething.core.Process import Process
from ething.core.Helpers import filter_obj
from ething.core.reg import get_registered_class
from collections import OrderedDict

try:
    from cheroot.wsgi import Server as WSGIServer
except ImportError:
    from cherrypy.wsgiserver import CherryPyWSGIServer as WSGIServer


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
        self.start_process()

    def unload(self):
        super(WebServer, self).unload()
        self.stop_process()

    def on_config_change(self, changes):
        self.stop_process()
        self.start_process()

    def start_process(self):
        self.process = WebServerProcess(self.core, self.config)
        self.process.start()

    def stop_process(self):
        if hasattr(self, 'process'):
            self.process.stop()
            del self.process


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
            instance =  cls.fromJson(attr, create=True, ething=self.core)
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
    def __init__(self, core, config=None):
        super(WebServerProcess, self).__init__('webserver')
        self.core = core
        self.config = config or {}
        self.debug = False
        self.server = None

    def stop(self):
        if self.server:
            self.server.stop()
        self.server = None

    def main(self):

        app = FlaskApp(self.core, self.log, root_path=root_path)

        self.log.info("web server root path = %s" % root_path)

        compress = Compress()
        compress.init_app(app)

        port = self.config['port']

        self.server = WSGIServer(
            bind_addr=('0.0.0.0', port),
            wsgi_app=app,
            server_name=socket.gethostname()
        )

        auth = install_auth(core=self.core, app=app, config=self.config, debug=self.debug, server = self.server)

        install_routes(core=self.core, app=app, auth=auth, debug=self.debug, server = self.server)

        current_ip = None
        try:
            current_ip = [l for l in (
            [ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")][:1], [
                [(s.connect(('8.8.8.8', 53)), s.getsockname()[0], s.close()) for s in
                 [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) if l][0][0]
        except:
            pass

        self.log.info("webserver: started at http://%s:%d" % (current_ip or 'localhost', port))

        self.server.start()

        #app.run(host='0.0.0.0', port=port, threaded=True)


