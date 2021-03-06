# coding: utf-8


from flask import request, Response
from ..server_utils import *
import os
import random
import string
from collections import OrderedDict

from ething.core.reg import build_schema_definitions, Entity, build_schema

from ..Scope import list as scope_list

from ething.core.utils import get_info


def install(core, app, auth, **kwargs):

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

    #
    # META
    #

    # load it only one time, definitions should not change during runtime
    definitions_etag = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(16))

    @app.route('/api/utils/definitions')
    @auth.required()
    def definitions():
        if app.etag_match(definitions_etag):
            return Response(status=304)

        meta = build_schema_definitions(skip=(Entity, ), core=core)

        return app.set_etag(app.jsonify(meta), definitions_etag)

    @app.route('/api/utils/info')
    @auth.required()
    def info():

        resp = {
            "scopes": scope_list,
            "info": get_info(core),
            "plugins": OrderedDict(),
        }

        for plugin in core.plugins:
            resp['plugins'][plugin.name] = {
                'js_index': plugin.is_js_index_valid(),
                'package': plugin.PACKAGE,
                'schema': build_schema(plugin)
            }

        return app.jsonify(resp)
