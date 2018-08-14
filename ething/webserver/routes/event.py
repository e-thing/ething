# coding: utf-8
from flask import Response, request
try:
    import queue
except ImportError:
    import Queue as queue


def install(core, app, auth, server = None, **kwargs):

    # SSE "protocol" is described here: http://mzl.la/UPFyxY
    @app.route('/api/events')
    @auth.required()
    def events():

        remote_addr = request.remote_addr

        core.log.debug('SSE: new listener %s' % remote_addr)

        def gen():

            q = queue.Queue()

            def on_signal(signal):
                q.put(signal)

            core.signalDispatcher.bind('*', on_signal)

            try:
                while server.ready:

                    try:
                        signal = q.get(True, 1)
                    except queue.Empty:
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

        return Response(gen(), mimetype="text/event-stream")
