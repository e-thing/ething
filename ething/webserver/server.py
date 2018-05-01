# coding: utf-8

from flask import Flask, Response
from flask_cors import CORS
from werkzeug.exceptions import HTTPException
from .auth import install_auth
from .routes import install_routes
import json as js
import traceback
import logging
from .method_override import HTTPMethodOverrideMiddleware
from .server_utils import ServerException, tb_extract_info, root_path



debug = False

def error_handler(e):
    
    error = {
        'message' : str(e),
        'code': 400
    }
    
    if isinstance(e, HTTPException):
        error['code'] = e.get_response().status_code
    elif isinstance(e, ServerException):
        error['code'] = e.status_code
    
    if debug :
        file, line = tb_extract_info()
        error['stack'] = traceback.format_exc()
        error['file'] = file
        error['line'] = line
        
    
    return Response(js.dumps(error), status=error['code'], mimetype='application/json')


def create(core):
    global debug
    
    app = Flask(__name__, static_url_path='', root_path=root_path)
    
    app.wsgi_app = HTTPMethodOverrideMiddleware(app.wsgi_app)
    
    cors_opt = {"origins": "*", "supports_credentials": True}
    
    CORS(app, resources={
        r"/api/*": cors_opt,
        r"/auth/*": cors_opt
    })

    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)
    
    core.log.info("web server root path = %s" % root_path)
    
    debug = bool(core.config['debug'])
    
    if debug:
        core.log.info('webserver: debug mode enabled')

    @app.errorhandler(Exception)
    def unhandled_exception(e):
        return error_handler(e)

    for cls in HTTPException.__subclasses__():
        app.register_error_handler(cls, error_handler)
    
    auth = install_auth(core = core, app = app, debug = debug)
    
    install_routes(core = core, app = app, auth = auth, debug = debug)
    
    return app


def toto():
    return 2

def run(core):
    app = create(core)
    app.run(host='0.0.0.0', port=core.config['webserver']['port'], threaded=True)
    return app


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
        },
        'debug': True
    })
    
    
    run(core)


