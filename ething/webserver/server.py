# coding: utf-8

from flask import Flask, Response
from flask_cors import CORS
from werkzeug.exceptions import HTTPException
from .auth import install_auth
from .routes import install_routes
import json as js
import traceback
import logging
import socket
from .method_override import HTTPMethodOverrideMiddleware
from .server_utils import ServerException, tb_extract_info, root_path
from ething.plugin import Plugin
from ething.Process import Process

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
        'properties': {
            'port': {
                'type': 'integer',
                'minimum': 1,
                'maximum': 65535
            },
            'auth': {
                'type': 'object',
                'required': ['username', 'password'],
                'properties': {
                    'username': {
                        'type': 'string',
                        'minLength': 1
                    },
                    'password': {
                        'type': 'string',
                        'minLength': 4
                    },
                    'localonly': {
                        'type': 'boolean'
                    }
                }
            }
        }
    }

    def load(self):
        self.process = WebServerProcess(self.core, self.config)
        self.process.start()

    def unload(self):
        if hasattr(self, 'process'):
            self.process.stop()
            del self.process



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

        app = Flask(__name__, static_url_path='', root_path=root_path)

        app.wsgi_app = HTTPMethodOverrideMiddleware(app.wsgi_app)

        cors_opt = {"origins": "*", "supports_credentials": True}

        CORS(app, resources={
            r"/api/*": cors_opt,
            r"/auth/*": cors_opt
        })

        log = logging.getLogger('werkzeug')
        log.setLevel(logging.ERROR)

        self.log.info("web server root path = %s" % root_path)

        self.debug = bool(self.config['debug'])
        port = self.config['port']

        if self.debug:
            self.log.info('webserver: debug mode enabled')

        self.server = WSGIServer(
            bind_addr=('0.0.0.0', port),
            wsgi_app=app,
            server_name=socket.gethostname()
        )

        @app.errorhandler(Exception)
        def unhandled_exception(e):
            return self.error_handler(e)

        for cls in HTTPException.__subclasses__():
            app.register_error_handler(cls, self.error_handler)

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

        return Response(js.dumps(error), status=error['code'], mimetype='application/json')

