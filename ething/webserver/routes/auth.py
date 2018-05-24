# coding: utf-8
from flask import redirect, request, url_for, make_response
from ..server_utils import *
import os

dir_html = os.path.abspath(os.path.dirname(__file__))


def install(core, app, auth, **kwargs):

    @app.route('/api/auth', methods=['GET'])
    @auth.required()
    def api_auth():
        """
        get:
          description: Returns information about the current authentication. The properties "device" and "app" are only available with API key authentication.
          responses:
            '200':
              description: authentication information
              schema:
                type: object
                properties:
                  scope:
                    type: string
                    description: 'The space-delimited set of permissions. If the field is missing, it means "full permissions".'
                  resource:
                    $ref: '#/definitions/Resource'
                  type:
                    type: string
                    description: 'the type of authentication: session, apikey, basic ...'
          summary: Returns information about the current authentication.
        """
        auth = g.auth

        d = {
            'type': auth.type
        }

        if auth.resource:
            d['resource'] = auth.resource

        if auth.scope is not None:
            d['scope'] = auth.scope

        return jsonify(d)

    @app.route('/auth/password', methods=['POST'])
    def auth_password():

        login = request.values.get('login')
        password = request.values.get('password')
        redirect_uri = request.values.get('redirect_uri')

        if redirect_uri is not None and not redirect_uri:
            redirect_uri = url_for('root_client')

        if len(login) > 0 and len(password) > 0:
            resp = make_response(redirect(redirect_uri)
                                 if redirect_uri is not None else ('', 204))
            if auth.session.authenticate(login, password, request, resp):
                return resp

        raise ServerException('invalid authentication credentials !', 401)

    @app.route('/auth/refresh', methods=['POST'])
    @auth.required()
    def auth_refresh():

        if g.auth.type == 'session':
            resp = make_response(('', 204))
            if auth.session.refresh(request, resp):
                return resp

        raise ServerException('not authorized', 403)

    @app.route('/auth/logout')
    def auth_logout():

        redirect_uri = request.values.get('redirect_uri')

        if redirect_uri is not None and not redirect_uri:
            redirect_uri = url_for('auth_login')

        resp = make_response(redirect(redirect_uri)
                             if redirect_uri is not None else ('', 204))

        auth.session.unauthenticate(request, resp)

        return resp
