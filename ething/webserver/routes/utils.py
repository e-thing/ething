# coding: utf-8


from flask import request, Response
from ..server_utils import *
import os
import random
import string
from werkzeug.http import unquote_etag

from ething.meta import resource_classes, interfaces_classes, event_classes, iface
from ething.base import READ_ONLY
from ething.Resource import Resource
from ething.event import Event

from ething.Scope import Scope

from ething.utils import get_info


def attr_helper(schema, name, attribute):

    if attribute.get('mode') == READ_ONLY:
        schema['readOnly'] = True


_meta = None


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

        return jsonify(info, indent=4)

    @app.route('/api/utils/net_list')
    @auth.required()
    def net_list():
        import ething.utils.net_scan
        return jsonify(ething.utils.net_scan.scan(), indent=4)
    
    @app.route('/api/utils/bluetooth_list')
    @auth.required()
    def bluetooth_list():
        from ething.utils.bluetooth import list_bluetooth_interfaces
        return jsonify(list_bluetooth_interfaces(), indent=4)

    read_log_args = {
        'line': fields.Int(validate=validate.Range(min=0), missing=50),
    }

    @app.route('/api/utils/read_log')
    @use_args(read_log_args)
    @auth.required()
    def read_log(args):
        logfilename = None
        lines = []
        linenb = args['line']

        for h in core.log.handlers:
            try:
                logfilename = h.baseFilename
                break
            except:
                pass

        def tail(fname, lines):
            bufsize = 8192
            fsize = os.stat(fname).st_size

            iter = 0
            data = []
            with open(fname) as f:
                if bufsize > fsize:
                    bufsize = fsize-1
                while True:
                    iter += 1
                    f.seek(fsize-bufsize*iter)
                    data.extend(f.readlines())
                    if len(data) >= lines or f.tell() == 0:
                        break

            return [l.strip() for l in data[-lines:]]

        if logfilename:
            lines = tail(logfilename, linenb)

        return jsonify(lines)

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
                "resources": {},
                "interfaces": {},
                "scopes": Scope.list,
                "events": {},
                "info": get_info(core),
                "plugins":{},
                "config": core.config.SCHEMA
            }

            for name in list(resource_classes):
                resource_cls = resource_classes[name]

                schema = resource_cls.schema(flatted=False, helper=attr_helper)

                # static inheritance
                allOf = []
                for b in resource_cls.__bases__:

                    if issubclass(b, Resource):
                        allOf.append({
                            '$ref': '#/resources/%s' % b.__name__
                        })
                    elif issubclass(b, iface):

                        for i in b.get_inherited_interfaces():
                            allOf.append({
                                '$ref': '#/interfaces/%s' % i.__name__
                            })

                if len(allOf) > 0:
                    if schema:
                        allOf.append(schema)

                    schema = {
                        'allOf': allOf
                    }

                if resource_cls.is_abstract():
                    schema['virtual'] = True

                _meta['resources'][name] = schema

            for name in list(interfaces_classes):
                interface_cls = interfaces_classes[name]

                # static inheritance
                allOf = []

                for b in interface_cls.__bases__:
                    if issubclass(b, iface):
                        for i in b.get_inherited_interfaces():
                            allOf.append({
                                '$ref': '#/interfaces/%s' % i.__name__
                            })

                if len(allOf) > 0:
                    schema = {
                        'allOf': allOf
                    }
                else:
                    schema = {
                        'type': 'object'
                    }

                _meta['interfaces'][name] = schema

            for name in list(event_classes):
                event_cls = event_classes[name]

                schema = event_cls.schema(flatted=False, helper=attr_helper)

                # static inheritance
                allOf = []
                for b in event_cls.__bases__:

                    if issubclass(b, Event):
                        allOf.append({
                            '$ref': '#/events/%s' % b.__name__
                        })

                if len(allOf) > 0:
                    if schema:
                        allOf.append(schema)

                    schema = {
                        'allOf': allOf
                    }

                if event_cls.is_abstract():
                    schema['virtual'] = True

                _meta['events'][name] = schema

            for plugin in core.plugins:
                name = plugin.name
                schema = getattr(plugin, 'CONFIG_SCHEMA', None)
                definition = {}

                if schema:
                    definition['schema'] = schema

                _meta['plugins'][name] = definition
        else:
            req_etag = request.headers.get('If-None-Match')
            if req_etag and definitions_etag == unquote_etag(req_etag)[0]:
                return Response(status=304)

        resp = jsonify(_meta)
        resp.set_etag(definitions_etag)
        resp.headers['Cache-Control'] = 'must-revalidate'
        return resp
