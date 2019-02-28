# coding: utf-8

from flask import request, Response
from ..server_utils import *
import re
from future.utils import string_types, text_type
from ething.core.reg import get_registered_methods


def install(core, app, auth, **kwargs):


    @app.route('/api/devices/<id>/call/<operationId>', methods=['GET', 'POST'])
    @auth.required('device:execute')
    def device_api_call(id, operationId):
        """
        ---
        get:
          tags:
            - device
          description: Execute an operation identified by operationId. The parameters must be passed in the query string.
          responses:
            '200':
              description: The response of the device.
        post:
          tags:
            - device
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
              description: The response of the device.
        """
        r = app.getResource(id, ['Device'])

        method = get_registered_methods(r, operationId)

        args = []
        kwargs = {}

        if request.method == 'GET':

            for arg_name in list(set(list(request.args)).intersection(list(method.get('args', {})))):
                kwargs[arg_name] = request.args[arg_name]

        elif request.method == 'POST':
            try:
                data = request.get_json()
                if isinstance(data, dict):
                    kwargs = data
                elif isinstance(data, list):
                    args = data
                elif data is not None:  # empty content with content-type set to application/json will return None
                    args.append(data)
            except:
                pass

        return_type = method.get('return_type')

        if return_type:

            if isinstance(return_type, string_types) and re.search('^[^/]+/[^/]+$', return_type):
                return Response(method.call(r, *args, **kwargs), mimetype=return_type)
            else:
                return app.jsonify(method.call(r, *args, **kwargs))

        else:
            method.call(r, *args, **kwargs)
            return '', 204

