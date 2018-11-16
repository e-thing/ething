# coding: utf-8
from flask import Response, request
from ething.core.rule.event import ResourceSignal
try:
    import queue
except ImportError:
    import Queue as queue


def on_signal_sio(signal, server, app):
    signal_name = type(signal).__name__
    server.socketio.emit(signal_name, app.toJson(signal), namespace="/events")


def install(core, app, auth, server = None, **kwargs):

    if hasattr(server, 'socketio'):
        core.signalDispatcher.bind('*', on_signal_sio, args=(server,app))

    def generate_events_flow(filter = None):

        #if server.stopped():
        #    raise Exception('Server not ready')

        remote_addr = request.remote_addr

        core.log.debug('SSE: new listener %s' % remote_addr)

        def gen():

            q = queue.Queue()

            def on_signal(signal):
                if not filter or filter(signal):
                    q.put(signal)

            core.signalDispatcher.bind('*', on_signal)

            yield "event:init\ndata:\n\n"

            try:
                while not server.stopped():

                    try:
                        signal = q.get(True, 1)
                    except queue.Empty:
                        yield "event:ping\ndata:\n\n"
                        continue

                    data = app.toJson(signal)

                    lines = ["data:{value}".format(
                        value=line) for line in data.splitlines()]
                    lines.insert(0, "event:message")

                    yield "\n".join(lines) + "\n\n"

            except GeneratorExit:  # Or maybe use flask signals
                pass

            core.signalDispatcher.unbind('*', on_signal)

            core.log.debug('SSE: stop listener %s' % remote_addr)

        return gen()

    # SSE "protocol" is described here: http://mzl.la/UPFyxY
    @app.route('/api/events')
    @auth.required()
    def events():
        return Response(generate_events_flow(), mimetype="text/event-stream")

    @app.route('/api/resources/<id>/events')
    @auth.required()
    def resource_events(id):
        r = app.getResource(id)
        return Response(generate_events_flow(lambda signal: isinstance(signal, ResourceSignal) and signal.resource == r), mimetype="text/event-stream")
