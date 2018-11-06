# coding: utf-8


from flask import request, Response
from ..server_utils import *


def install(core, app, auth, **kwargs):

    @app.route('/api/rules', methods=['POST'])
    @auth.required('rule:write resource:write')
    def rules():
        """
        ---
        post:
          tags:
            - rule
          description: |-
            Create a new rule.
          parameters:
            - name: metadata
              in: body
              description: |-

                the metadata of the rule to be created

                example:

                ```json
                {
                   "name" : 'myrule',
                   "script": "ho58-ju",
                   "event": {
                       "type": "CustomEvent",
                       "name": "foobar"
                   }
                }
                ```

              required: true
              schema:
                $ref: '#/definitions/Rule'
          responses:
            '200':
              description: The rule was successfully created
              schema:
                $ref: '#/definitions/Rule'
        """

        attr = request.get_json()

        if attr is not None:
            attr.setdefault('createdBy', g.auth.resource)

            r = core.create('resources/Rule', attr)

            if r:
                response = app.jsonify(r)
                response.status_code = 201
                return response
            else:
                raise Exception('Unable to create the rule')

        raise Exception('Invalid request')

    @app.route('/api/rules/<id>/execute')
    @auth.required('rule:read resource:read')
    def rule_execute(id):
        r = app.getResource(id, ['Rule'])

        if not r.run():
            raise Exception('An error occurs during execution of the rule')

        return '', 204

    @app.route('/api/rules/trigger/<customEventName>')
    @auth.required('rule:trigger')
    def trigger_custom_event(customEventName):
        core.dispatchSignal('Custom', customEventName)
        return '', 204
