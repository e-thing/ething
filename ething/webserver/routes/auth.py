# coding: utf-8
from flask import redirect,request,url_for, make_response, send_from_directory
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
        
        password = request.values.get('password')
        redirect_uri = request.values.get('redirect_uri') or url_for('root_client')
        
        if len(password) > 0:
            resp = make_response(redirect(redirect_uri))
            if auth.session.authenticate(password, request, resp):
                return resp
            
        
        raise Exception('invalid authentication credentials !')



    @app.route('/auth/logout')
    def auth_logout():
        
        redirect_uri = request.values.get('redirect_uri') or ''
        
        resp = make_response(redirect(url_for('auth_login', redirect_uri = redirect_uri)))
        
        auth.session.unauthenticate(request, resp)
        
        return resp
        

    @app.route('/auth/login')
    def auth_login():
        
        redirect_uri = request.values.get('redirect_uri') or url_for('root_client')
        
        if auth.session.isAuthenticated(request):
            
            return redirect(redirect_uri)
        
        else:
            core.log.info(dir_html)
            return send_from_directory(dir_html, 'login.html')

