

from flask import request, Response
from ..server_utils import *
import os


def install(core, app, auth, **kwargs):

    @app.route('/utils/serial_ports_list')
    @auth.required()
    def serial_ports_list():
        import serial.tools.list_ports

        ports = list(serial.tools.list_ports.comports())

        info = [];

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


    @app.route('/utils/net_list')
    @auth.required()
    def net_list():
        import ething.utils.net_scan
        return jsonify(ething.utils.net_scan.scan(), indent=4)


    read_log_args = {
        'line': fields.Int(validate=validate.Range(min=0), missing=50),
    }

    @app.route('/utils/read_log')
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
                    iter +=1
                    f.seek(fsize-bufsize*iter)
                    data.extend(f.readlines())
                    if len(data) >= lines or f.tell() == 0:
                        break
            
            return [ l.strip() for l in data[-lines:]]

        if logfilename:
            lines = tail(logfilename, linenb)
        
        return jsonify(lines)



