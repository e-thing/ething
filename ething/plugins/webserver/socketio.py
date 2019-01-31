# coding: utf-8
from flask_socketio import SocketIO


def patch_socketio():
    """this patch allow multiple handles on events connect and disconnect"""

    native_on_method = getattr(SocketIO, 'on')

    handlers = {}

    def patched_on(self,  message, namespace=None):

        if namespace is None and (message == 'connect' or message == 'disconnect'):

            def decorator(handler):

                if message not in handlers:
                    handlers[message] = []
                handlers[message].append(handler)

                def _handler(*args):
                    for h in handlers[message]:
                        try:
                            h(*args)
                        except Exception as e:
                            print(e)

                native_on_method(self, message, namespace)(_handler)

                return handler

            return decorator

        else:
            return native_on_method(self, message, namespace)

    setattr(SocketIO, 'on', patched_on)


patch_socketio()
