# coding: utf-8
from flask import request
from ething.notification import list_persistent_notifications, remove_persistent_notification


def install(core, app, auth, **kwargs):

    @app.route('/api/notifications')
    @auth.required()
    def list_notifications():
        return app.jsonify(list_persistent_notifications(core))

    @app.route('/api/notifications/<id>', methods=['DELETE'])
    @auth.required()
    def delete_notification(id):
        remove_persistent_notification(core, id)
        return '', 204