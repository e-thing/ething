# coding: utf-8


from flask import request, Response
from ..server_utils import *
from ething.core.Flow import registered_nodes, Debugger
import time
import json


class SocketIoDebugger (Debugger):
    def __init__(self, app, client_id, flowResource):
        self.app = app
        self.client_id = client_id
        self.flowResource = flowResource
        self.flowResourceId = flowResource.id

        flowResource.attach_debugger(self)

    def debug(self, obj, node=None):

        data = {
            'node': node.id if node is not None else None,
            'flow_id': self.flowResourceId,
            'ts': time.time()
        }

        if isinstance(obj, Exception):
            obj = {
                'type': type(obj).__name__,
                'message': str(obj),
                'traceback': traceback.format_exc()
            }
            data['exception'] = True

        data['data'] = self.app.toJson(obj)

        self.app.socketio.emit('dbg_data', data, namespace='/flow', room=self.client_id)

    def info(self, node, info):

        data = {
            'node': node.id,
            'flow_id': self.flowResourceId,
            'ts': time.time()
        }

        data['data'] = self.app.toJson(info)

        self.app.socketio.emit('dbg_info', data, namespace='/flow', room=self.client_id)

    def destroy(self):
        self.flowResource.dettach_debugger(self)


def install(core, app, auth, **kwargs):

    _debuggers = []

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

            schema = getattr(cls, 'SCHEMA', None)

            if schema is None:
                props = cls.PROPS or {}
                schema = {
                    'type': 'object',
                    'properties': props,
                    'required': cls.PROPS_REQUIRED if cls.PROPS_REQUIRED is not None else list(props.keys())
                }

            nodes.append({
                'type': getattr(cls, 'NAME', cls.__name__),
                'color': getattr(cls, 'COLOR', None),
                'icon': getattr(cls, 'ICON', None),
                'inputs': cls.INPUTS,
                'outputs': cls.OUTPUTS,
                'schema': schema
            })

        return app.jsonify({
            'nodes': nodes
        })

    @app.socketio.on('connect', namespace='/flow')
    def client_connect():
        app.log.debug('[flow] Client connected %s' % request.sid)

    @app.socketio.on('disconnect', namespace='/flow')
    def client_disconnect():
        client_id = request.sid

        # remove all debuggers for this client !
        to_remove = set()
        for d in _debuggers:
            if d.client_id == client_id:
                to_remove.add(d)
        for d in to_remove:
            d.destroy()
            _debuggers.remove(d)

        app.log.debug('[flow] Client disconnected %s' % request.sid)

    @app.socketio.on('dbg_open', namespace='/flow')
    def open_debugger(data):
        flow_id = data.get('flow_id')
        client_id = request.sid

        flowResource = app.getResource(flow_id, ['Flow'])

        debugger = SocketIoDebugger(app, client_id, flowResource)
        _debuggers.append(debugger)

    @app.socketio.on('dbg_close', namespace='/flow')
    def close_debugger(data):
        flow_id = data.get('flow_id')
        client_id = request.sid

        flowResource = app.getResource(flow_id, ['Flow'])

        # find the according debugger
        debugger = None
        for d in _debuggers:
            if d.client_id == client_id and d.flowResource == flowResource:
                debugger = d
                break

        if debugger:
            debugger.destroy()
            _debuggers.remove(debugger)

