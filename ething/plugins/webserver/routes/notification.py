# coding: utf-8
from flask import request


def install(core, app, auth, **kwargs):

    @app.route('/api/notifications')
    @auth.required()
    def list_notifications():
        return app.jsonify(core.notification.find())

    @app.route('/api/notifications/<id>', methods=['DELETE'])
    @auth.required()
    def delete_notification(id):
        core.notification.remove(id)
        return '', 204