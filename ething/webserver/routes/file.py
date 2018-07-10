# coding: utf-8


from flask import request, Response
from ..server_utils import *
import base64
from werkzeug.http import parse_options_header
import json
from ething.ScriptEngine import ScriptEngine


def install(core, app, auth, **kwargs):

    @app.route('/api/files', methods=['POST'])
    @auth.required('file:write resource:write')
    def files():
        """
        ---
        post:
          tags:
            - file
          description: |-
            Creates a new file.

            There are 2 ways to pass directly the content of the file on the same request :

             - pass the content as a base-64 encoded ASCII string through the key 'content' of the metadata object.

             example:

            ```json
            {
               "name": "myfile.txt",
               "content": "SGVsbG8gd29ybGQgIQ==" // 'Hello world !' in base-64
            }
            ```

             - multipart/related request: transfers the content along with metadata that describes it. *The metadata part must come first*.

             example:

            ```
            POST /ething/api/files HTTP/1.1
            Host: <YOUR_HOST>
            Content-Type: multipart/related; boundary=foo_bar_baz

            --foo_bar_baz
            Content-Type: application/json; charset=UTF-8

            {
              "name": "image.jpg"
            }

            --foo_bar_baz
            Content-Type: image/jpeg

            <JPEG DATA>
            --foo_bar_baz--
            ```

            #### cURL example

            The next command will create a new file 'myfile.txt'.

            ```bash
            curl
                -H 'X-API-KEY: <YOUR_API_KEY>'
                -H "Content-Type: application/json"
                -X POST
                -d '{"name":"myfile.txt"}'
                http://localhost:8000/api/files
            ```

            If the command was successful, a response containing the meta data of the created file will be given back.
            You will find in it the id of that file.
            This id is a unique string identifying this file and is necessary to make any operation on it.

            ```json
            {
              "id":"73c66-4",
              "name":"myfile.txt",
              "data":null,
              "description":null,
              "expireAfter":null,
              "type":"File",
              "createdBy":{
               "id":"56a7B-5",
               "type":"Device"
              },
              "createdDate":"2016-01-27T07:46:43+00:00",
              "modifiedDate":"2016-02-13T10:34:31+00:00",
              "mime":"text/plain",
              "size":0,
              "location":null,
              "hasThumbnail":false,
              "isText": true
            }
            ```
          parameters:
            - name: metadata
              in: body
              description: |-

                the metadata of the file to be created

                example:

                ```json
                {
                   "name": "myfile.txt",
                   "description": "an optional description"
                }
                ```

              required: true
              schema:
                $ref: '#/definitions/File'
          responses:
            '200':
              description: The file was successfully created
              schema:
                $ref: '#/definitions/File'
        """

        attr = None
        content = None

        if request.mimetype == 'multipart/related':

            parts = list(parse_multipart_data(request.stream,
                                              request.mimetype_params['boundary']))

            for headers, body in parts:
                mimetype, params = parse_options_header(
                    headers['Content-Type'])

                if mimetype == 'application/json':
                    attr = json.loads(body.decode())
                else:
                    content = body

        else:
            attr = request.get_json()

            if isinstance(attr, dict):

                if 'content' in attr:
                    content = base64.b64decode(attr['content'])
                    attr.pop('content')

        if attr is not None:
            attr.setdefault('createdBy', g.auth.resource)

            r = core.create('File', attr)

            if r:

                if content:
                    r.write(content)

                response = app.jsonify(r)
                response.status_code = 201
                return response
            else:
                raise Exception('Unable to create the file')

        raise Exception('Invalid request')

    file_put_args = {
        'append': fields.Bool(missing=False, description="If true, the content will be appended."),
    }

    @app.route('/api/files/<id>', methods=['GET', 'PUT'])
    @use_multi_args(PUT=(file_put_args, ('query',)))
    @auth.required(GET='file:read resource:read', PUT='file:write resource:write')
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
            return Response(r.read(), mimetype=r.mime)

        elif request.method == 'PUT':

            content = request.data

            if args['append']:
                r.append(content)
            else:
                r.write(content)

            return app.jsonify(r)

    @app.route('/api/files/<id>/thumbnail')
    @auth.required('file:read resource:read')
    def file_thumb(id):
        r = app.getResource(id, ['File'])
        thumb = r.readThumbnail()

        if not thumb:
            raise Exception('No thumbnail available')

        return Response(thumb, mimetype='image/png')

    file_action_execute_args = {
        'args': fields.Str(missing=None, description="A string representing the arguments to be passed to the script.")
    }

    @app.route('/api/files/<id>/execute')
    @use_args(file_action_execute_args)
    @auth.required('file:read resource:read')
    def file_execute(args, id):
        r = app.getResource(id, ['File'])

        if r.mime == 'application/javascript':

            res = ScriptEngine.runFromFile(r, args['args'])

            if not res:
                raise Exception('Unable to execute')

            return app.jsonify(res)

        else:
            raise Exception('Not executable')
