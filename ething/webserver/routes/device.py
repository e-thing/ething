# coding: utf-8


from flask import request, Response
from ..server_utils import *
import re
import base64

def install(core, app, auth, **kwargs):



    devices_args = {
        'fields': fields.DelimitedList(fields.Str()),
    }

    @app.route('/api/devices', methods=['POST'])
    @auth.required('device:write resource:write')
    @use_args(devices_args)
    def devices(args):
        """
        ---
        post:
          tags:
            - device
          description: Creates a new device.
          parameters:
            - name: metadata
              in: body
              description: |

                The metadata of the device to be created.

                example:

                ```json
                {
                   "name": "mydevice.txt",
                   "location": "room 1",
                   "scope": "resource:read notification",
                }
                ```
              required: true
              schema:
                $ref: '#/definitions/Device'
          responses:
            '200':
              description: The device was successfully created
              schema:
                allOf:
                  - type: object
                    required:
                      - type
                    properties:
                      type:
                        type: string
                        description: 'The type of the device to create (eg: "Http" or "MySensorsEthernetGateway").'
                  - $ref: '#/definitions/Device'
        """
        attr = request.get_json()
        
        if isinstance(attr, dict):
            
            if 'type' not in attr:
                raise Exception('the "type" attribute is mandatory')
            
            type = attr.pop('type')
            content = None
            
            if type == 'Http':
                content = attr.pop('content', None)
            elif type == 'MQTT':
                content = attr.pop('subscription', None)
            
            attr.setdefault('createdBy', g.auth.resource)
            
            r = core.create(type, attr)
            
            if r:
                
                if content:
                    if r.type == 'Http':
                        r.setSpecification(base64.b64decode(content))
                    elif r.type == 'MQTT':
                        r.setSubscription(content)
                
                response = jsonEncodeFilterByFields(r, args['fields'])
                response.status_code = 201
                return response
            else:
                raise Exception('Unable to create the device (type = %s)' % type);
        
        raise Exception('Invalid request')



    @app.route('/api/devices/<Device:r>/api')
    @auth.required('device:read resource:read')
    def device_apis(r):
        """
        ---
        get:
          tags:
            - device
          description: Retrieves an object describing the operations available for this device.
          responses:
            '200':
              description: object describing the operations available for this device.
        """
        return jsonify(r.interface)


    @app.route('/api/devices/<Device:r>/api/<operationId>')
    @auth.required('device:read resource:read')
    def device_api(r, operationId):
        """
        ---
        get:
          tags:
            - device
          description: Retrieves an object describing the operation identified by operationId.
          parameters:
            - name: operationId
              in: path
              description: id of the operation.
              required: true
              type: string
          responses:
            '200':
              description: object describing the operation.
        """
        return jsonify(r.interface.get_method(operationId))


    @app.route('/api/devices/<Device:r>/call/<operationId>', methods=['GET', 'POST'])
    @auth.required('device:write resource:write')
    def device_api_call(r, operationId):
        """
        ---
        get:
          tags:
            - device
          description: Execute an operation identified by operationId. The parameters must be passed in the query string.
          parameters:
            - name: operationId
              in: path
              description: id of the operation.
              required: true
              type: string
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
        
        method = r.interface.get_method(operationId)
        
        args = []
        kwargs = {}
        
        if request.method == 'GET':
            
            for arg_name in list(set(list(request.args)).intersection(list(method.args))):
                kwargs[arg_name] = method.args[arg_name]
            
        elif request.method == 'POST':
            try:
                data = request.get_json()
                if isinstance(data, dict):
                    kwargs = data
                elif isinstance(data, list):
                    args = data
                else:
                    args.append(data)
            except:
                pass
        
        return_type = method.return_type
        
        if return_type:
            
            if re.search('^[^/]+/[^/]+$', return_type):
                return Response(method.call(*args, **kwargs), mimetype=return_type)
            else:
                return jsonify(method.call(*args, **kwargs))
            
        else:
            method.call(*args, **kwargs)
            return ('', 204)


    @app.route('/api/devices/<Device:r>/specification')
    @auth.required('device:read resource:read')
    def device_http_specification(r):
        if not r.isTypeof('Http'):
            raise Exception('Not a Http device')
        return jsonify(r.getSpecification())


    @app.route('/api/devices/<Device:r>/subscription')
    @auth.required('device:read resource:read')
    def device_mqtt_subscription(r):
        if not r.isTypeof('MQTT'):
            raise Exception('Not a MQTT device')
        return jsonify(r.getSubscription())
