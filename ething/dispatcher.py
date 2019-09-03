# coding: utf-8

import logging
import threading
import time
import re
from .utils.weak_ref import proxy_method, LostReferenceException
from queue import Queue, Empty


__all__ = ['emit', 'bind', 'unbind', 'SignalEmitter']


LOGGER = logging.getLogger(__name__)


ANY = '*'


class Signal(object):
    pass


class SignalDispatcher(object):

    def __init__(self, auto_start=True):
        self.r_lock = threading.RLock()
        self.handlers = list()
        self._queue = Queue()
        self._running = False
        if auto_start:
            self.start()

    def queue(self, signal, sender=None, namespace=None):
        self._queue.put((signal, sender, namespace))

    def process(self, timeout=0):
        block = bool(timeout != 0)
        t0 = time.time()
        while timeout >= 0:
            try:
                arg = self._queue.get(block, timeout)
                self.dispatch(*arg)
            except Empty:
                break
            else:
                timeout -= time.time() - t0

    def run(self):
        self._running = True
        LOGGER.debug('signal dispatcher event loop started')
        while self._running:
            try:
                arg = self._queue.get(True, 1)
                self.dispatch(*arg)
            except Empty:
                pass
        LOGGER.debug('signal dispatcher event loop stopped')

    def start(self):
        t = threading.Thread(name='signaldispatcher', target=self.run, daemon=True)
        t.start()
        setattr(self, '_t', t)

    def stop(self):
        self._running = False
        t = getattr(self, '_t', None)
        if t is not None:
            t.join()
            delattr(self, '_t')

    def dispatch(self, signal, sender=None, namespace=None):
        with self.r_lock:
            # LOGGER.debug("dispatch signal: %s" % (str(signal), ))
            for weakref_handler_info in list(self.handlers):
                _signal, handler, once, _sender, _, _ns_re, args = weakref_handler_info
                if _signal == ANY or isinstance(signal, _signal):
                    if _sender is None or _sender == sender:
                        if _ns_re is None or (namespace and _ns_re.match(namespace)):
                            remove = False
                            try:
                                handler(signal, *args)
                            except LostReferenceException:
                                # lost reference
                                remove = True
                            except Exception as e:
                                LOGGER.exception("Error calling signal handler with signal: %s handler: %s" % (str(signal), handler))
                            if once or remove:
                                self.handlers.remove(weakref_handler_info)

    def bind(self, signal, handler, once = False, sender=None, args=(), namespace=None):
        """Adds an event listener for event name"""
        with self.r_lock:
            ns_re = re.compile(namespace + '(\.|$)') if namespace else None
            self.handlers.append((signal, proxy_method(handler), once, sender, namespace, ns_re, args))

    def unbind(self, signal=ANY, handler = None, sender=None, namespace=None):
        """removes previously added event listener"""
        if namespace is not None:
            namespace = re.compile(namespace + '(\.|$)')
        with self.r_lock:
            for handler_info in list(self.handlers):
                _signal, _handler, once, _sender, _namespace, _, args = handler_info
                if signal == ANY or issubclass(_signal, signal):
                    if handler is None or handler == _handler:
                        if sender is None or sender == _sender:
                            if namespace is None or (_namespace and namespace.match(_namespace)):
                                self.handlers.remove(handler_info)

    def clear(self):
        with self.r_lock:
            self.handlers.clear()

        while True:
            try:
                self._queue.get(False)
            except Empty:
                break


_dispatcher = None


def global_instance():
    global _dispatcher

    if _dispatcher is None:
        # start the global instance
        _dispatcher = SignalDispatcher()

    return _dispatcher


def emit(signal, sender=None, namespace=None):
    """dispatch asynchronously a signal"""
    global_instance().queue(signal, sender, namespace)


def bind(signal, handler, once=False, sender=None, args=(), namespace=None):
    """Adds an event listener for event name"""
    global_instance().bind(signal, handler, once, sender, args, namespace)


def unbind(signal, handler=None, sender=None, namespace=None):
    """removes previously added event listener"""
    global_instance().unbind(signal, handler, sender, namespace)


class SignalEmitter(object):

    @property
    def namespace(self):
        return str(id(self))

    def emit(self, signal):
        """
        Dispatch a signal.

        :param signal: a signal instance
        """

        emit(signal, sender=self, namespace=self.namespace)

    def bind(self, signal, handler, once=False, args=()):
        bind(signal, handler, once, self, args, self.namespace)

    def unbind(self, signal, handler=None):
        unbind(signal, handler, self, self.namespace)