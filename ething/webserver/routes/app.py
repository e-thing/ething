# coding: utf-8



from flask import request, Response
from ..server_utils import *
import base64
from werkzeug.http import parse_options_header
import json

def install(core, app, auth, **kwargs):


    apps_args = {
        'fields': fields.DelimitedList(fields.Str())
    }

    @app.route('/api/apps', methods=['POST'])
    @auth.required('app:write resource:write')
    @use_args(apps_args)
    def apps(args):
        """
        ---
        post:
          tags:
            - app
          description: |-
            Creates a new application.

            An application consists of a single HTML page. Use the Javascript SDK to easily build an application.

             example:
             
            ```html
            <!DOCTYPE html>
            <html>

              <head>

                <!-- CORE -->
                <script src="__JS_URL__"></script>

              </head>

              <body>

                <!-- your content goes here -->

                <!-- APP -->
                <script type="text/javascript">
                  var main = function() {
                    var app = EThing.auth.getApp();

                    var textnode = document.createTextNode('application : ' + app.name());
                    document.body.appendChild(textnode);

                  };

                  EThing.initialize({
                    serverUrl: '__SERVER_URL__',
                    apiKey: '__API_KEY__'
                  }, main || null, function(error) {
                    // on error
                    alert(error.message);
                  });
                  
                </script>

              </body>
            </html>
            ```

            #### Preprocessor definitions


            The following string are automatically replaced in the HTML code :

            | Definition     | Value                                                                |
            |----------------|----------------------------------------------------------------------|
            | __API_KEY__    | the API key of this application                                      |
            | __ID__         | the ID of this application                                           |
            | __NAME__       | the name of this application                                         |
            | __SERVER_URL__ | the url of the server                                                |
            | __JS_URL__     | the url of Javascript API                                            |



            There are 2 ways to pass directly the code and the icon data of the application on the same request :

             - pass the code or/and the icon data as a base-64 encoded ASCII string through the key 'content' and 'icon' respectively of the metadata object.
             
             example:

            ```json
            {
               "name": "myapp",
               "content": "SGVsb...GQgIQ==", // your code in base-64
               "icon": "bXkga...biBkYXRh" // your icon data in base-64
            }
            ```

             - multipart/related request: transfers the code and/or the icon binary data along with metadata. The order of the different part does not matter. The code part must have the Content-Type header set to 'text/html' or 'text/plain'.
               The icon part must have the Content-Type header set to a compatible image MIME type.
             
             example:
             
            ```
            POST /ething/api/apps HTTP/1.1
            Host: <YOUR_HOST>
            Content-Type: multipart/related; boundary=foo_bar_baz

            --foo_bar_baz
            Content-Type: application/json; charset=UTF-8

            {
              "name": "myapp"
            }

            --foo_bar_baz
            Content-Type: image/jpeg

            <JPEG DATA>

            --foo_bar_baz
            Content-Type: text/html

            <!doctype html>
            <html lang="en">
            <head>
              <meta charset="utf-8">
              <title>myapp</title>
            </head>
            <body>
              Hello World !
            </body>
            </html>
            --foo_bar_baz--
            ```
          parameters:
            - name: metadata
              in: body
              description: The metadata of the application to be created.
              required: true
              schema:
                $ref: '#/definitions/App'
          responses:
            '200':
              description: The application was successfully created
              schema:
                $ref: '#/definitions/App'
        """
        
        attr = None
        content = None
        icon = None
        
        if request.mimetype == 'multipart/related':
            
            parts = list(parse_multipart_data(request.stream, request.mimetype_params['boundary']))
            
            for headers, body in parts:
                mimetype, params = parse_options_header(headers['Content-Type'])
                
                if mimetype == 'application/json':
                    attr = json.loads(body.decode())
                elif mimetype == 'text/html' or mimetype == 'text/plain':
                    content = body
                elif re.match('image', mimetype):
                    icon = body
        
        else:
            attr = request.get_json()
            
            if isinstance(attr, dict):
                
                if 'content' in attr:
                    content = base64.b64decode(attr['content'])
                    attr.pop('content')
                
                if 'icon' in attr:
                    icon = base64.b64decode(attr['icon'])
                    attr.pop('icon')
                
        if attr is not None:
            
            attr.setdefault('createdBy', g.auth.resource)
            
            r = core.create('App', attr)
            
            if r:
                
                if content:
                    r.setScript(content)
                
                if icon:
                    r.setIcon(content)
                
                response = jsonEncodeFilterByFields(r, args['fields'])
                response.status_code = 201
                return response
            else:
                raise Exception('Unable to create the app');
        
        raise Exception('Invalid request');


    app_get_args = {
        'exec': fields.Bool(missing=False, description="Set this parameter to '1' to get the HTML code ready to be executed in a browser (i.e. content-type set to 'text/html' and the preprocessor definitions set).")
    }

    app_put_args = {
        'fields': fields.DelimitedList(fields.Str())
    }

    @app.route('/api/apps/<App:r>', methods=['GET', 'PUT'])
    @use_multi_args(GET = app_get_args, PUT = (app_put_args, ('query',)))
    @auth.required(GET = 'app:read resource:read', PUT = 'app:write resource:write')
    def rapp(args, r):
        """
        ---
        get:
          tags:
            - app
          description: Retrieves the script of an application.
          produces:
            - text/html
          responses:
            '200':
              description: The source code
              schema:
                type: file
        put:
          tags:
            - app
          description: Set the script for this application. The script must be a single HTML page.
          parameters:
            - name: script
              in: body
              description: The script as a HTML page.
              required: true
              schema:
                type: string
                format: binary
          consumes:
            - text/plain
            - text/html
          responses:
            '200':
              description: The script was set successfully. It returns back the meta data of this application.
              schema:
                $ref: '#/definitions/App'
        """
        
        if request.method == 'GET':
            
            content = r.readScript()
            
            if args['exec']:
                
                # replace some SUPER GLOBALS
                
                content = content.replace("__SERVER_URL__", request.url_root )
                content = content.replace("__JS_URL__", request.url_root + "client/node_modules/ething-js/dist/ething.js")
                content = content.replace("__API_URL__", request.url_root + "api")
                content = content.replace("__API_KEY__", r.apikey)
                content = content.replace("__ID__", r.id)
                content = content.replace("__NAME__", r.name)
                
                return Response(content, mimetype = 'text/html')
                
            # for security reason, will not be executed in browsers
            return Response(content, mimetype = 'text/plain')
        
        elif request.method == 'PUT':
            
            r.setScript(request.data)
            
            return jsonEncodeFilterByFields(r, args['fields'])



    app_icon_put_args = {
        'fields': fields.DelimitedList(fields.Str())
    }

    @app.route('/api/files/<App:r>/icon', methods=['GET', 'PUT'])
    @use_multi_args(PUT = (app_icon_put_args, ('query',)))
    @auth.required(GET = 'app:read resource:read', PUT = 'resource:admin')
    def app_icon(args, r):
        """
        ---
        get:
          tags:
            - app
          description: Retrieves the icon of an application if there is one defined.
          produces:
            - image/jpeg
            - image/png
          responses:
            '200':
              description: The icon of this application.
              schema:
                type: file
        """
        
        if request.method == 'GET':
            icon = r.readIcon()
            
            if not icon:
                raise Exception('No icon available')
            
            return Response(icon, mimetype='image/png')
        
        elif request.method == 'PUT':
            
            r.setIcon(request.data)
            
            return jsonEncodeFilterByFields(r, args['fields'])

