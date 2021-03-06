# coding: utf-8
from flask import request


def install(core, app, auth, **kwargs):


    @app.route('/api/clients')
    @auth.required()
    def list_clients():
        return app.jsonify(app.clients)

    @app.route('/api/clients/<id>')
    @auth.required()
    def get_client(id):
        cl = app.get_client(id)
        if cl:
            return app.jsonify(cl)
        else:
            raise Exception('Not found')

    @app.route('/api/clients/<id>', methods=['DELETE'])
    @auth.required()
    def delete_client(id):
        cl = app.get_client(id)
        if cl:
            cl.remove()
            return '', 204
        else:
            raise Exception('Not found')

    @app.route('/api/clients/<id>/notify', methods=['POST'])
    @auth.required()
    def notify_client(id):
        cl = app.get_client(id)
        if cl:
            data = request.get_json()
            if 'msg' not in data:
                raise Exception('Invalid data')
            cl.notify(data['msg'])
            return '', 204
        else:
            raise Exception('Not found')
