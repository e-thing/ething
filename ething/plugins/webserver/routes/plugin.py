# coding: utf-8
from flask import send_file
from ..server_utils import *
from ething.reg import update


def install(core, app, auth, **kwargs):

    @app.route('/api/plugins/<name>/index.js')
    @auth.required()
    def plugin_js_index(name):
        p = core.plugins[name]
        if p:
            if p.is_js_index_valid():
                return send_file(p.js_index())
            else:
                raise Exception('no js index defined for this plugin')
        else:
            raise Exception('unknown plugin')

    @app.route('/api/plugins')
    @auth.required()
    def plugins():
        return app.jsonify(list(core.plugins))

    @app.route('/api/plugins/<name>', methods=['GET', 'PATCH'])
    @auth.required()
    def plugin(name):
        """Get a name by its name
        ---
        get:
          tags:
            - plugin
          description: Returns the meta-data of a plugin in JSON.
          responses:
            '200':
              description: plugin object
              schema:
                $ref: '#/definitions/Plugin'
        patch:
          tags:
            - plugin
          description: Update a plugin. Only properties which are not readonly can be modified.
          parameters:
            - name: modification
              in: body
              description: the attributes to modify
              required: true
              schema:
                $ref: '#/definitions/Plugin'
          responses:
            '200':
              description: plugin successfully updated
              schema:
                $ref: '#/definitions/Plugin'
        """

        p = core.plugins[name]
        if not p:
            raise Exception('unknown plugin %s' % name)

        if request.method == 'GET':
            return app.jsonify(p)

        elif request.method == 'PATCH':

            data = request.get_json()

            if isinstance(data, dict):
                with p:
                    update(p, data, data_src='json')
                    return app.jsonify(p)

            raise Exception('Invalid request')

    @app.route('/api/plugins/<name>/call/<operationId>', methods=['GET', 'POST'])
    @auth.required('resource:execute')
    def plugin_api_call(name, operationId):
        """
        ---
        get:
          tags:
            - plugin
          description: Execute an operation identified by operationId. The parameters must be passed in the query string.
          responses:
            '200':
              description: The response of the plugin.
        post:
          tags:
            - plugin
          description: Execute an operation identified by operationId. The parameters can either be passed in the query string or in the body as a JSON object or a x-www-form-urlencoded string.
          parameters:
            - name: operationId
              in: path
              description: id of the operation.
              required: true
              type: string
            - name: data
              in: body
              description: required parameters for this operation.
              required: false
              schema:
                type: object
          responses:
            '200':
              description: The response of the plugin.
        """
        p = core.plugins[name]
        if not p:
            raise Exception('unknown plugin %s' % name)
        return entity_api_call(app, p, operationId)
