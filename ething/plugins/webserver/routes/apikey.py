# coding: utf-8


from flask import request, Response
from ..server_utils import *
from ..apikey import *


def install(core, app, auth, **kwargs):

    @app.route('/api/apikey', methods=['GET', 'POST'])
    @auth.required()
    def apikeys():
        if request.method == 'GET':
            return app.jsonify(core.db.os.find(Apikey))

        elif request.method == 'POST':
            attr = request.get_json()

            if attr is not None:

                apikey = fromJson(Apikey, attr, {
                    'core': core
                })

                if apikey:
                    core.db.os.save(apikey)
                    response = app.jsonify(apikey)
                    response.status_code = 201
                    return response
                else:
                    raise Exception('Unable to create the apikey')

        raise Exception('Invalid request')

    @app.route('/api/apikey/<id>', methods=['GET', 'DELETE', 'PATCH'])
    @auth.required()
    def apikey(id):
        apikey = core.db.os.get(Apikey, id)

        if not apikey:
            raise Exception('API key not found')

        if request.method == 'GET':
            return app.jsonify(apikey)

        elif request.method == 'PATCH':

            data = request.get_json()

            if isinstance(data, dict):
                with apikey:
                    fromJson(apikey, data)
                    return app.jsonify(apikey)

            raise Exception('Invalid request')

        elif request.method == 'DELETE':
            core.db.os.remove(apikey)
            return '', 204
