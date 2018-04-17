# coding: utf-8
from flask import Response, request
from ething.Helpers import toJson

def install(core, app, auth, **kwargs):

    # SSE "protocol" is described here: http://mzl.la/UPFyxY
    @app.route('/api/events')
    @auth.required()
    def events():
        
        remote_addr = request.remote_addr
        
        core.log.debug('SSE: new listener %s' % remote_addr)
        
        def gen():
            
            client = core.rpc.subscribe('signal')
            
            try:
                while True:
                    msg = client.get()
                    if msg is None:
                        # rpc server disconnected
                        break
                    signal = msg.message
                    
                    data = toJson(signal)
                    
                    lines = ["data:{value}".format(value=line) for line in data.splitlines()]
                    lines.insert(0, "event:message")
                    
                    yield "\n".join(lines) + "\n\n"
                    
            except GeneratorExit: # Or maybe use flask signals
                client.stop()
                core.log.debug('SSE: stop listener %s' % remote_addr)
        
        return Response(gen(), mimetype="text/event-stream")

