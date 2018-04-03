
from flask import Flask, Response
from flask_cors import CORS
from werkzeug.exceptions import HTTPException
from auth import install_auth
from routes import install_routes
import converters
import json as js
import os, sys
import traceback
import logging
from method_override import HTTPMethodOverrideMiddleware

root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

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


def init(core):
    global debug
    
    app = Flask(__name__, static_url_path='', root_path=root_path)
    
    app.wsgi_app = HTTPMethodOverrideMiddleware(app.wsgi_app)
    
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)
    
    core.log.info("web server root path = %s" % root_path)
    
    debug = bool(core.config['debug'])
    
    if debug:
        core.log.info('webserver: debug mode enabled')
    
    
    # register custom converters :
    converters.install(core = core, app = app)

    @app.errorhandler(Exception)
    def unhandled_exception(e):
        return error_handler(e)

    for cls in HTTPException.__subclasses__():
        app.register_error_handler(cls, error_handler)
    
    auth = install_auth(core = core, app = app, debug = debug)
    
    install_routes(core = core, app = app, auth = auth, debug = debug)
    
    return app

def run(core):
    app = init(core)
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
    
    
    #with app.test_client() as c:
    #    response = c.get('/test/monid?a=toto&b=1')
    #    print response.get_data()
    
    run(core)

