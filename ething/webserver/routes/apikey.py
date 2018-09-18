# coding: utf-8


from flask import request, Response
from ..server_utils import *


def install(core, app, auth, **kwargs):

    apikey_manager = app.apikey_manager

    @app.route('/api/apikey', methods=['GET', 'POST'])
    @auth.required()
    def apikeys():
        if request.method == 'GET':
            return app.jsonify(apikey_manager.list())

        elif request.method == 'POST':
            attr = request.get_json()

            if attr is not None:

                apikey = apikey_manager.create(attr)

                if apikey:
                    response = app.jsonify(apikey)
                    response.status_code = 201
                    return response
                else:
                    raise Exception('Unable to create the apikey')

        raise Exception('Invalid request')

    @app.route('/api/apikey/<id>', methods=['GET', 'DELETE', 'PATCH'])
    @auth.required()
    def apikey(id):
        apikey = apikey_manager.get(id)

        if not apikey:
            raise Exception('API key not found')

        if request.method == 'GET':
            return app.jsonify(apikey)

        elif request.method == 'PATCH':

            data = request.get_json()

            if isinstance(data, dict):
                with apikey:
                    apikey.updateFromJson(data)

                    return app.jsonify(apikey)

            raise Exception('Invalid request')

        elif request.method == 'DELETE':
            apikey.remove()
            return '', 204
