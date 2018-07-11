# coding: utf-8

from flask import request
from ..server_utils import *


def install(core, app, auth, **kwargs):

    @app.route('/api/settings', methods=['GET', 'PATCH'])
    @auth.required(GET='settings:read', PATCH='settings:write')
    def settings():
        """
        ---
        get:
          tags:
            - settings
          description: Returns the settings
          responses:
            '200':
              description: The settings
              schema:
                type: object
        patch:
          tags:
            - settings
          description: update your settings.
          parameters:
            - name: data
              in: body
              description: the attributes to modify
              required: true
              schema:
                type: object
          responses:
            '200':
              description: settings successfully updated
              schema:
                type: object
        """
        if request.method == 'PATCH':
            core.config.set(request.get_json())

        return app.jsonify(core.config())
