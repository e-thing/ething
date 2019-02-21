# coding: utf-8


from flask import request, Response
from ..server_utils import *
import base64
from werkzeug.http import parse_options_header
import json


def install(core, app, auth, **kwargs):

    file_put_args = {
        'append': fields.Bool(missing=False, description="If true, the content will be appended."),
    }

    @app.route('/api/files/<id>', methods=['GET', 'PUT'])
    @use_multi_args(PUT=(file_put_args, ('query',)))
    @auth.required(GET='file:read', PUT='file:write')
    def file(args, id):
        """
        ---
        get:
          tags:
            - file
          description: |-
            Retrieves the content of a file.

            #### cURL example

            The next command show you how to read the content of a file identified by its id.

            ```bash
            curl -H 'X-API-KEY: <YOUR_API_KEY>' http://localhost:8000/api/files/<FILE_ID>
            ```
          produces:
            - '*/*'
          responses:
            '200':
              description: The content of this file
              schema:
                type: file
        put:
          tags:
            - file
          description: |-
            Upload the content of a file.

            #### cURL example

            The next command show you how to send the content of the local file 'data.txt' into a file.

            ```bash
            curl
                -H 'X-API-KEY: <YOUR_API_KEY>'
                -X PUT
                --data @data.txt
                http://localhost:8000/api/files/<FILE_ID>
            ```
          consumes:
            - '*/*'
          parameters:
            - name: content
              in: body
              description: The new content. Could be of any type.
              required: true
              schema:
                type: string
                format: binary
          responses:
            '200':
              description: The file's metadata
              schema:
                $ref: '#/definitions/File'
        """
        r = app.getResource(id, ['File'])

        if request.method == 'GET':
            etag = str(r.contentModifiedDate)

            if app.etag_match(etag):
                return Response(status=304)

            return app.set_etag(Response(r.read(), mimetype=r.mime), etag)

        elif request.method == 'PUT':

            content = request.data

            if args['append']:
                r.append(content)
            else:
                r.write(content)

            return app.jsonify(r)

    @app.route('/api/files/<id>/thumbnail')
    @auth.required('file:read')
    def file_thumb(id):
        r = app.getResource(id, ['File'])
        thumb = r.readThumbnail()

        if not thumb:
            raise Exception('No thumbnail available')

        return Response(thumb, mimetype='image/png')

