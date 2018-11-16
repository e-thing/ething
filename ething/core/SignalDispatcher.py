# coding: utf-8

import logging
import threading
import time
from .utils.weak_ref import weak_ref
try:
    import queue
except ImportError:
    import Queue as queue


class SignalDispatcher(object):

    def __init__(self):
        self.log = logging.getLogger('ething.SignalDispatcher')

        self.r_lock = threading.RLock()

        self.handlers = {}

        self._queue = queue.Queue()

    def queue(self, signal):
        self._queue.put(signal)

    def process(self, timeout = 0):
        block = bool(timeout != 0)
        t0 = time.time()
        while timeout >= 0:
            try:
                signal = self._queue.get(block, timeout)
                self.dispatch(signal)
            except queue.Empty:
                break
            else:
                timeout -= time.time() - t0


    def dispatch(self, signal):
        with self.r_lock:
            event_type = type(signal).__name__

            for weakref_handlers in [self.handlers.get('*', []), self.handlers.get(event_type, [])]:
                for weakref_handler_info in weakref_handlers:
                    weakref_handler, once, args = weakref_handler_info
                    handler = weakref_handler()
                    if handler is not None:
                        try:
                            handler(signal, *args)
                        except Exception as e:
                            self.log.exception("Error calling signal handler with signal: %s handler: %s" % (str(signal), handler))
                        if once:
                            weakref_handlers.remove(weakref_handler_info)
                    else: # lost reference
                        weakref_handlers.remove(weakref_handler_info)

    def bind(self, event_types, handler, once = False, args=()):
        """Adds an event listener for event name"""
        with self.r_lock:
            for event_type in event_types.split(' '):
                if not event_type:
                    continue

                if event_type not in self.handlers:
                    self.handlers[event_type] = []

                self.handlers[event_type].append((weak_ref(handler), once, args))

    def unbind(self, event_types, handler = None):
        """removes previously added event listener"""
        with self.r_lock:
            for event_type in event_types.split(' '):
                if not event_type:
                    continue

                for type in list(self.handlers.keys()):
                    if event_type == '*' or event_type == type:
                        if handler is None:
                            del self.handlers[type]
                        else:
                            for index, weakref_handler_info in enumerate(self.handlers[type]):
                                weakref_handler, once, args = weakref_handler_info
                                if handler == weakref_handler():
                                    del self.handlers[type][index]
                                    break