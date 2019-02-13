# coding: utf-8
import pytest
from ...server import FlaskApp
from ...routes import install_routes
from ...auth import install_auth
import base64


@pytest.fixture
def webapp(core):
    app = FlaskApp(core, {
        'debug': True
    })

    # add a global context
    ctx = app.app_context()
    ctx.push()

    return app


@pytest.fixture
def webapp_auth_header(core):

    username = core.config(u'auth.username')
    password = core.config(u'auth.password')

    if username and password:

        t = u"{0}:{1}".format(username, password)

        auth_headers = {
            'Authorization': u'Basic {0}'.format(base64.b64encode(t.encode('utf8')).decode('utf8'))
        }
    else:
        auth_headers = {}

    return auth_headers
