# coding: utf-8
from future.utils import string_types

from flask import request, Response
from ..server_utils import *
import csv
from ething.core.ShortId import ShortId


def install(core, app, auth, **kwargs):

    @app.route('/api/tables', methods=['POST'])
    @auth.required('table:write resource:write')
    def tables():
        """
        ---
        post:
          tags:
            - table
          description: |-
            Creates a new table.

            You may want to pass directly the content of the table in the same request. To do so, just pass the data through the key 'content' of the metadata object;

            example:

            ```json
            {
               "name": "foobar.db",
               "content": [
                    {
                        "temperature": 12.5,
                        "pressure": 101325
                    }
               ]
            }
            ```

            #### cURL example

            The next command will create a new table 'mytable.db'.

            ```bash
            curl
                -H 'X-API-KEY: <YOUR_API_KEY>'
                -H "Content-Type: application/json"
                -X POST
                -d '{"name":"mytable.db"}'
                http://localhost:8000/api/tables
            ```

            If the command was successful, a response containing the meta data of the created table will be given back.
            You will find in it the id of that table.
            This id is a unique string identifying this table and is necessary to make any operation on it.

            ```json
            {
              "id":"56_df0f",
              "name":"mytable.db",
              "data":null,
              "description":null,
              "maxLength":null,
              "expireAfter":null,
              "type":"Table",
              "createdBy":null,
              "createdDate":"2016-02-12T14:49:30+00:00",
              "modifiedDate":"2016-02-15T13:03:20+00:00",
              "length":421,
              "keys":{
                 "temp1":421,
                 "temp2":421
              },
              "location":null
            }
            ```
          parameters:
            - name: metadata
              in: body
              description: |-


                The metadata of the table to be created.

                example:

                ```json
                {
                    "name":"mytable.db"
                }
                ```

              required: true
              schema:
                $ref: '#/definitions/Table'
          responses:
            '200':
              description: The table was successfully created
              schema:
                $ref: '#/definitions/Table'
        """
        attr = request.get_json()

        if isinstance(attr, dict):

            content = None

            if 'content' in attr:
                content = attr['content']
                attr.pop('content')

            attr.setdefault('createdBy', g.auth.resource)

            r = core.create('resources/Table', attr)

            if r:

                if content:
                    r.importData(content)

                response = app.jsonify(r)
                response.status_code = 201
                return response
            else:
                raise Exception('Unable to create the table')

        raise Exception('Invalid request')

    table_fmts = ["json", "json_pretty", "csv", "csv_no_header"]
    date_fmts = ['timestamp', 'timestamp_ms', 'rfc3339']
    table_get_args = {
        'start': fields.Int(missing=0, description="Position of the first rows to return. If start is negative, the position will start from the end. (default to 0)"),
        'length': fields.Int(validate=validate.Range(min=0), description="Maximum number of rows to return. If not set, returns until the end"),
        'sort': fields.Str(description='the key on which to do the sorting, by default the sort is made by date ascending. To make the sort descending, prepend the field name by minus "-". For instance, "-date" will sort by date descending'),
        'query': fields.Str(data_key="q", load_from="q", description="Query string for filtering results"),
        'date_format': fields.Str(data_key="datefmt", load_from="datefmt", validate=lambda val: val.lower() in date_fmts, missing='rfc3339', description="the format of the date field (default to RFC3339) : %s" % ','.join(date_fmts)),
        'fmt': fields.Str(validate=validate.OneOf(table_fmts), missing='json', description="the output format (default to JSON) : %s" % ','.join(table_fmts)),
    }

    table_put_args = {
        'invalid_field': fields.Str(validate=validate.OneOf(['rename', 'stop', 'skip', 'none']), missing='rename', description="The behaviour to adopt when an invalid field name appears."),
        'skip_error': fields.Bool(missing=True, description="Whether to skip data on error or not."),
    }

    table_post_args = {
        'invalid_field': fields.Str(validate=validate.OneOf(['rename', 'stop', 'skip', 'none']), missing='rename', description="The behaviour to adopt when an invalid field name appears."),
    }

    @app.route('/api/tables/<id>', methods=['GET', 'PUT', 'POST'])
    @use_multi_args(GET=table_get_args, PUT=(table_put_args, ('query',)), POST=(table_post_args, ('query',)))
    @auth.required(GET='table:read resource:read', PUT='table:write resource:write', POST='table:write table:append resource:write')
    def table(args, id):
        """
        ---
        get:
          tags:
            - table
          description: |-
            Retrieves the content of a table.

            #### cURL examples

            ```bash
            # get all the data of a table :
            curl -H 'X-API-KEY: <YOUR_API_KEY>' http://localhost:8000/api/tables/<TABLE_ID>

            # only the first 20 rows :
            curl -H 'X-API-KEY: <YOUR_API_KEY>' http://localhost:8000/api/tables/<TABLE_ID>?start=0&length=20

            # only the last 20 rows :
            curl -H 'X-API-KEY: <YOUR_API_KEY>' http://localhost:8000/api/tables/<TABLE_ID>?start=-20

            # only the last 10 rows sorted by the field "temperature" in ascending order
            # (put a minus before the name of the field if you want to sort in descending order)
            curl -H 'X-API-KEY: <YOUR_API_KEY>' http://localhost:8000/api/tables/<TABLE_ID>?start=-10&sort=temperature
            ```
          produces:
            - application/json
            - text/plain
          responses:
            '200':
              description: The records of this table
              schema:
                type: array
                items:
                  type: object
                  description: record's object. Every record has at least the 'id' and 'date' keys.
                  properties:
                    id:
                      type: string
                      description: an unique id to identify a record
                    date:
                      type: string
                      format: date-time
                      description: the create date of this record
        put:
          tags:
            - table
          description: Set the content of a table. The new data will erase the previous one.
          consumes:
            - application/json
          parameters:
            - name: content
              in: body
              description: |-
                The content to be inserted as an array of object.

                The data must be sent in a JSON formatted object :

                ```json
                [{
                    "<KEY>":<VALUE>
                }]
                ```

                example:

                ```json
                [
                    {
                      "date": "2016-02-06T15:03:07+01:00",
                      "temperature": 12.5,
                      "pressure": 101325
                    },
                    {
                      "date": "2016-02-06T16:03:07+01:00",
                      "temperature": 13.5,
                      "pressure": 101212
                    }
                ]
                ```

                If the 'date' field is not present, the current date will be set automatically.
                If an 'id' field is present, it will be automatically be resetted to a new value.


              required: true
              schema:
                type: array
                items:
                  type: object
          responses:
            '200':
              description: The content was successfully set. The table metadata is returned.
              schema:
                $ref: '#/definitions/Table'
        post:
          tags:
            - table
          description: Insert a new record in a table
          parameters:
            - name: record
              in: body
              description: |-
                The record to be inserted.

                The data must be sent in a JSON formatted object :

                ```json
                {
                    "<KEY>":<VALUE>
                }
                ```

                cURL example :

                ```bash
                curl
                    -H 'X-API-KEY: <YOUR_API_KEY>'
                    -H "Content-Type: application/json"
                    -X POST
                    -d '{"temperature":15.2, "comment":"outdoor"}'
                    http://localhost:8000/api/tables/<TABLE_ID>
                ```



              required: true
              schema:
                type: object
          responses:
            '200':
              description: The record was successfully inserted. The table metadata is returned.
              schema:
                $ref: '#/definitions/Table'
        """

        r = app.getResource(id, ['Table'])

        if request.method == 'GET':

            fmt = args.pop('fmt').lower()

            if fmt == "json":
                return app.jsonify(r.select(**args))
            elif fmt == "json_pretty":
                return app.jsonify(r.select(**args), indent=4)
            elif fmt == "csv" or fmt == "csv_no_header":
                args['show_header'] = (fmt == "csv")

                fields = request.args.get('fields')
                if fields is not None:
                    fields = fields.replace(' ', ',').replace(
                        ';', ',').replace('|', ',').split(',')
                    args['fields'] = fields

                return Response(r.writeCSV(**args), mimetype='text/csv')

            raise Exception('Invalid request')

        elif request.method == 'PUT':

            data = request.get_json()

            if data:
                r.importData(data, args['invalid_field'], args['skip_error'])
                return app.jsonify(r)
            else:
                raise Exception('No data.')

        elif request.method == 'POST':

            data = request.get_json()

            if data:
                r.insert(data, args['invalid_field'])
                return app.jsonify(r)
            else:
                raise Exception('No data.')

    table_action_remove_args = {
        'ids': fields.DelimitedList(fields.Str(), missing=[], description="The records id to be removed as a comma separated list."),
    }

    @app.route('/api/tables/<id>/remove', methods=['POST'])
    @use_args(table_action_remove_args, locations=('query', 'form'))
    @auth.required('table:write resource:write')
    def table_delete_rows(args, id):
        """
        ---
        post:
          tags:
            - table
          description: Remove one or more records in a table
          responses:
            '200':
              description: The records was successfully deleted
              schema:
                $ref: '#/definitions/Table'
        """
        r = app.getResource(id, ['Table'])
        ids = args['ids'] or []

        if request.json:
            more_ids = request.json

            if isinstance(more_ids, string_types):
                more_ids = [more_ids]

            if not isinstance(more_ids, list):
                raise Exception('The key ids must be an array of record id.')

            ids = ids + more_ids

        if len(ids) > 0:
            for id in ids:
                if not ShortId.validate(id):
                    raise Exception('Must be an array of record id.')

            nb = r.remove_rows(ids)

            if nb == len(ids):
                # all the specified documents/rows were removed
                return app.jsonify(r)
            else:
                # all or only certain documents/rows could not have been removed
                raise Exception(
                    'Some or all documents could not have been removed.')

    table_action_replace_args = {
        'q': fields.Str(required=True, description="A query that select the rows to update"),
        'invalid_field': fields.Str(validate=validate.OneOf(['rename', 'stop', 'skip', 'none']), missing='rename', description="The behaviour to adopt when an invalid field name appears."),
        'upsert': fields.Bool(missing=False, description="If true and no records was found, the data will be added to the table as a new record."),
    }

    @app.route('/api/tables/<id>/replace', methods=['POST'])
    @use_args(table_action_replace_args, locations=('query',))
    @auth.required('table:write resource:write')
    def table_replace_rows(args, id):
        """
        ---
        post:
          tags:
            - table
          description: Update records in a table
          responses:
            '200':
              description: The records was successfully updated
              schema:
                $ref: '#/definitions/Table'
        """

        r = app.getResource(id, ['Table'])
        data = request.get_json()

        if data:

            r.replaceRow(args['q'], data, args['invalid_field'],
                         args['upsert'])
            return app.jsonify(r)
        else:
            raise Exception('No data.')

    table_statistics_args = {
        'q': fields.Str(description="A query string to select the rows used for the statistics computation", missing=None),
        'key': fields.Str(required=True, description="the name of the key. Statistics can only be computed for a single key."),
    }

    @app.route('/api/tables/<id>/statistics')
    @auth.required('table:read resource:read')
    @use_args(table_statistics_args)
    def table_statistics(args, id):
        """
        ---
        get:
          tags:
            - table
          description: Compute statistics of a column (=key)
          responses:
            '200':
              description: The records was successfully updated
              schema:
                type: object
                description: The statistics object.
        """
        r = app.getResource(id, ['Table'])
        return app.jsonify(r.computeStatistics(args['key'], args['q']))

    table_cell_id_patch_args = {
        'invalid_field': fields.Str(validate=validate.OneOf(['rename', 'stop', 'skip', 'none']), missing='rename'),
    }

    @app.route('/api/tables/<id>/id/<doc_id>', methods=['GET', 'DELETE', 'PATCH'])
    @use_multi_args(PATCH=(table_cell_id_patch_args, ('query',)))
    @auth.required(GET='table:read resource:read', DELETE='table:write resource:write', PATCH='table:write resource:write')
    def table_cell_id(args, id, doc_id):

        r = app.getResource(id, ['Table'])

        if request.method == 'GET':

            doc = r.getRow(doc_id)

            if doc is None:
                raise Exception(
                    'The document with id=%s does not exist.' % doc_id)

            return app.jsonify(doc)

        elif request.method == 'DELETE':
            r.remove_row(doc_id)
            return '', 204

        elif request.method == 'PATCH':

            data = request.get_json()

            if data:
                doc = r.replaceRowById(doc_id, data, args['invalid_field'])
                if doc:
                    return app.jsonify(doc)
                else:
                    raise Exception(
                        'The document with id=%s does not exist.' % doc_id)
            else:
                raise Exception('No data')
