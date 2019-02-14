# coding: utf-8

from flask import request, Response
from ..server_utils import *
from ething.core.reg import fromJson
from future.utils import iteritems


def install(core, app, auth, **kwargs):

    @app.route('/api/usage', methods=['GET'])
    @auth.required('resource:read')
    def usage():
        return app.jsonify(core.usage())

    resources_args = {
        'q': fields.Str(missing=None, description='Query string for searching resources'),
        'limit': fields.Int(validate=validate.Range(min=0), description='Limits the number of resources returned'),
        'skip': fields.Int(validate=validate.Range(min=0), description='Skips a number of resources'),
        'sort': fields.Str(description='The key on which to do the sorting, by default the sort is made by modifiedDate descending. To make the sort descending, prepend the field name by minus "-". For instance, "-createdDate" will sort by createdDate descending'),
    }

    @app.route('/api/resources', methods=['GET'])
    @use_args(resources_args)
    @auth.required('resource:read resource:write file:read file:write table:read table:write table:append device:read device:write app:read app:write')
    def resources(args):
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
                        if r.isTypeof(t):
                            return True

                if query:
                    query = [typeQuery, query]
                else:
                    query = typeQuery

        return app.jsonify(core.find(query=query, **args))

    resource_delete_args = {
        'children': fields.Bool(missing=False)
    }

    @app.route('/api/resources/<id>', methods=['GET', 'DELETE', 'PATCH'])
    @use_multi_args(DELETE=resource_delete_args)
    @auth.required(GET='resource:read resource:write file:read file:write table:read table:write table:append device:read device:write app:read app:write', DELETE='resource:admin', PATCH='resource:admin')
    def resource(args, id):
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

                    fromJson(r, data)

                    return app.jsonify(r)

            raise Exception('Invalid request')

        elif request.method == 'DELETE':
            r.remove(args['children'])
            return '', 204
