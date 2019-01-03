# coding: utf-8


from flask import request, Response
from ..server_utils import *
from ething.core.Flow import registered_nodes


def install(core, app, auth, **kwargs):

    @app.route('/api/flows', methods=['POST'])
    @auth.required('flow:write resource:write')
    def flows():

        attr = request.get_json()

        if attr is not None:
            attr.setdefault('createdBy', g.auth.resource)

            r = core.create('resources/Flow', attr)

            if r:
                response = app.jsonify(r)
                response.status_code = 201
                return response
            else:
                raise Exception('Unable to create the flow')

        raise Exception('Invalid request')

    @app.route('/api/flows/<id>/deploy')
    @auth.required('flow:read resource:read')
    def flow_deploy(id):
        r = app.getResource(id, ['Flow'])
        r.deploy()
        return '', 204

    @app.route('/api/flows/meta')
    @auth.required()
    def flow_meta():
        nodes = []

        for cls in registered_nodes:
            nodes.append({
                'type': cls.__name__,
                'color': getattr(cls, 'COLOR', None),
                'icon': getattr(cls, 'ICON', None),
                'inputs': cls.INPUTS,
                'outputs': cls.OUTPUTS,
                'schema': {
                    'type': 'object',
                    'properties': cls.PROPS or {}
                }
            })

        return app.jsonify({
            'nodes': nodes
        })
