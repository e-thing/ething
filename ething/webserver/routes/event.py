from flask import Response
from ething.Helpers import toJson

def install(core, app, auth, **kwargs):

    # SSE "protocol" is described here: http://mzl.la/UPFyxY
    @app.route('/api/events')
    @auth.required()
    def events():
        
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
        
        return Response(gen(), mimetype="text/event-stream")

