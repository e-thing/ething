# coding: utf-8


from flask import request, Response
from ..server_utils import *
import os
import random
import string
from collections import OrderedDict
from io import open

from ething.core.reg import build_schema_definitions
from ething.core.dbentity import DbEntity, Entity
from ething.core.utils.export import export_data, import_data
from ething.core.plugin import Plugin

from ..Scope import Scope

from ething.core.utils import get_info


_meta = None


def install(core, app, auth, **kwargs):

    @app.route('/api/utils/restart')
    @auth.required()
    def restart():
        core.restart()
        return '', 204

    @app.route('/api/utils/reset')
    @auth.required()
    def reset():
        core.reset()
        return '', 204


    @app.route('/api/utils/serial_ports_list')
    @auth.required()
    def serial_ports_list():
        import serial.tools.list_ports

        ports = list(serial.tools.list_ports.comports())

        info = []

        for port in ports:
            info.append({
                'device': port.device,
                'name': port.name,
                'description': port.description,
                'hwid': port.hwid,
                'vid': port.vid,
                'pid': port.pid,
                'serial_number': port.serial_number,
                'location': port.location,
                'manufacturer': port.manufacturer,
                'product': port.product,
                'interface': port.interface
            })

        return app.jsonify(info, indent=4)

    @app.route('/api/utils/net_list')
    @auth.required()
    def net_list():
        from ething.core.utils.net_scan import scan
        return app.jsonify(scan(), indent=4)

    @app.route('/api/utils/bluetooth_list')
    @auth.required()
    def bluetooth_list():
        from ething.core.utils.bluetooth import list_bluetooth_interfaces
        return app.jsonify(list_bluetooth_interfaces(), indent=4)

    read_log_args = {
        'line': fields.Int(validate=validate.Range(min=0), missing=50),
        'filter': fields.Str(missing=None, description='a filter the log results'),
    }

    @app.route('/api/utils/read_log')
    @use_args(read_log_args)
    @auth.required()
    def read_log(args):
        logfilename = None
        lines = []
        linenb = args['line']
        filter = args['filter'] or None

        for h in core.log.handlers:
            try:
                logfilename = h.baseFilename
                break
            except:
                pass

        if logfilename:
            with open(logfilename, encoding='utf8') as f:
                lines = f.readlines()
                if filter:
                    lines = [l for l in lines if filter in l]
                if linenb:
                    lines = lines[-linenb:]

        return app.jsonify(lines)

    #
    # META
    #

    definitions_etag = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(16))

    @app.route('/api/utils/definitions')
    @auth.required()
    def definitions():
        global _meta

        if _meta is None:
            _meta = {
                "definitions": build_schema_definitions(skip=(DbEntity, Entity)),
                "scopes": Scope.list,
                "info": get_info(core),
                "plugins": OrderedDict(),
                "config": core.config.SCHEMA
            }

            for plugin in core.plugins:
                name = plugin.name
                definition = {
                    'js_index': plugin.is_js_index_valid(),
                    'schema': None
                }

                if isinstance(plugin, Plugin):
                    definition['schema'] = plugin.config.schema

                _meta['plugins'][name] = definition
        else:
            if app.etag_match(definitions_etag):
                return Response(status=304)

        return app.set_etag(app.jsonify(_meta), definitions_etag)

    @app.route('/api/utils/export')
    @auth.required()
    def export_route():
        return app.jsonify(export_data(core))

    @app.route('/api/utils/import', methods=['POST'])
    @auth.required()
    def import_route():

        data = request.get_json()

        if data:
            import_data(core, data)
            return '', 204

        raise Exception('Invalid request')
