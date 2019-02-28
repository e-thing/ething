# coding: utf-8

import logging
import threading
import time
from .utils.weak_ref import proxy_method, LostReferenceException
from queue import Queue, Empty


class SignalDispatcher(object):

    def __init__(self):
        self.log = logging.getLogger('ething.SignalDispatcher')

        self.r_lock = threading.RLock()

        self.handlers = {}

        self._queue = Queue()

    def queue(self, signal):
        self._queue.put(signal)

    def process(self, timeout = 0):
        block = bool(timeout != 0)
        t0 = time.time()
        while timeout >= 0:
            try:
                signal = self._queue.get(block, timeout)
                self.dispatch(signal)
            except Empty:
                break
            else:
                timeout -= time.time() - t0


    def dispatch(self, signal):
        with self.r_lock:
            event_type = type(signal).__name__

            for weakref_handlers in [self.handlers.get('*', []), self.handlers.get(event_type, [])]:
                for weakref_handler_info in weakref_handlers:
                    handler, once, args = weakref_handler_info
                    remove = False
                    try:
                        handler(signal, *args)
                    except LostReferenceException:
                        # lost reference
                        remove = True
                    except Exception as e:
                        self.log.exception("Error calling signal handler with signal: %s handler: %s" % (str(signal), handler))
                    if once or remove:
                        weakref_handlers.remove(weakref_handler_info)

    def bind(self, event_types, handler, once = False, args=()):
        """Adds an event listener for event name"""
        with self.r_lock:
            for event_type in event_types.split(' '):
                if not event_type:
                    continue

                if event_type not in self.handlers:
                    self.handlers[event_type] = []

                self.handlers[event_type].append((proxy_method(handler), once, args))

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
                            for index, handler_info in enumerate(self.handlers[type]):
                                _handler, once, args = handler_info
                                if handler == _handler:
                                    del self.handlers[type][index]
                                    break

    def clear(self):
        with self.r_lock:
            self.handlers.clear()

        while True:
            try:
                signal = self._queue.get(False)
            except Empty:
                break
