# coding: utf-8
from ..server_utils import *
from ething.reg import update


def install(core, app, auth, **kwargs):

    resources_args = {
        'q': fields.Str(missing=None, description='Query string for searching resources'),
        'limit': fields.Int(validate=validate.Range(min=0), description='Limits the number of resources returned'),
        'skip': fields.Int(validate=validate.Range(min=0), description='Skips a number of resources'),
        'sort': fields.Str(description='The key on which to do the sorting, by default the sort is made by modifiedDate descending. To make the sort descending, prepend the field name by minus "-". For instance, "-createdDate" will sort by createdDate descending'),
    }

    @app.route('/api/resources', methods=['GET'])
    @use_args(resources_args, location="querystring")
    @auth.required('resource:read')
    def resources_get(args):
        """list the resources
        ---
        get:
            tags:
              - resource
            description: |-
                Lists the resources.

                #### cURL example

                ```bash
                curl -H 'X-API-KEY: <YOUR_API_KEY>' http://localhost:8000/api/resources
                ```
            responses:
                200:
                    description: A list of resources
                    schema:
                        type: array
                        items:
                            $ref: '#/definitions/Resource'
        """

        query = args.pop('q')

        auth = g.auth

        if auth.scope is not None:

            scopes = [s for s in auth.scope.split(" ") if s]

            allowed_types = []
            for scope in scopes:
                type = scope.split(':')[0].capitalize()
                if type not in allowed_types:
                    allowed_types.append(type)

            if 'resource' not in allowed_types:
                # restrict the search to the allowed_types

                def typeQuery (r):
                    for t in allowed_types:
                        if r.typeof(t):
                            return True

                if query:
                    query = [typeQuery, query]
                else:
                    query = typeQuery

        return app.jsonify(core.find(query=query, **args))

    @app.route('/api/resources', methods=['POST'])
    @auth.required('resource:write')
    def resources_post():
        """
        ---
        post:
          tags:
            - resource
          description: Creates a new resource.
          parameters:
            - name: metadata
              in: body
              description: |

                The metadata of the resource to be created.

                example:

                ```json
                {
                   "type": "resources/SSH",
                   "name": "mydevice",
                   "location": "room 1",
                   "host": "192.168.1.25"
                }
                ```
              required: true
              schema:
                $ref: '#/definitions/Resource'
          responses:
            '200':
              description: The resource was successfully created
              schema:
                allOf:
                  - type: object
                    required:
                      - type
                    properties:
                      type:
                        type: string
                        description: 'The type of the device to create (eg: "MySensorsEthernetGateway").'
                  - $ref: '#/definitions/Device'
        """
        attr = request.get_json()

        if isinstance(attr, dict):

            type = attr.pop('type', None)

            if not isinstance(type, string_types) or len(type) == 0:
                raise Exception(
                    'the "type" attribute is mandatory and must be a non empty string')

            attr.setdefault('createdBy', g.auth.resource)

            r = core.create(type, attr)

            if r:
                response = app.jsonify(r)
                response.status_code = 201
                return response
            else:
                raise Exception(
                    'Unable to create the resource (type = %s)' % type)

        raise Exception('Invalid request')


    @app.route('/api/resources/<id>', methods=['GET', 'DELETE', 'PATCH'])
    @auth.required(GET='resource:read', DELETE='resource:write', PATCH='resource:write')
    def resource(id):
        """Get a resource by its id
        ---
        get:
          tags:
            - resource
          description: Returns the meta-data of a resource in JSON.
          responses:
            '200':
              description: resource object
              schema:
                $ref: '#/definitions/Resource'
        delete:
          tags:
            - resource
          description: deletes a resource
          responses:
            '200':
              description: the resource has been deleted successfully
        patch:
          tags:
            - resource
          description: |-
            update a resource. Only properties which are not readonly can be modified.

            Rename a resource :

            ```json
            {
               "name":"myFileRenamed.txt"
            }
            ```

            Clear a description :

            ```json
            {
               "description":null
            }
            ```
          parameters:
            - name: modification
              in: body
              description: the attributes to modify
              required: true
              schema:
                $ref: '#/definitions/Resource'
          responses:
            '200':
              description: resource successfully updated
              schema:
                $ref: '#/definitions/Resource'
        """

        r = app.getResource(id)

        if request.method == 'GET':
            return app.jsonify(r)

        elif request.method == 'PATCH':

            data = request.get_json()

            if isinstance(data, dict):
                
                with r:
                    update(r, data, data_src='json')
                    return app.jsonify(r)

            raise Exception('Invalid request')

        elif request.method == 'DELETE':
            r.remove()
            return '', 204

    @app.route('/api/resources/<id>/call/<operationId>', methods=['GET', 'POST'])
    @auth.required('resource:execute')
    def resource_api_call(id, operationId):
        """
        ---
        get:
          tags:
            - resource
          description: Execute an operation identified by operationId. The parameters must be passed in the query string.
          responses:
            '200':
              description: The response of the resource.
        post:
          tags:
            - resource
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
              description: The response of the resource.
        """
        r = app.getResource(id)
        return entity_api_call(app, r, operationId)
