# coding: utf-8

import logging
import threading
import time

from .green import mode

processes_map_lock = threading.Lock()

processes_map = {}

def add_process(process):
    with processes_map_lock:
        if process.name not in processes_map:
            processes_map[process.name] = []
        processes_map[process.name].append(process)

def remove_process(process):
    with processes_map_lock:
        processes_map[process.name].remove(process)

def get_process(name):
    with processes_map_lock:
        if name in processes_map and len(processes_map[name]) > 0:
            return processes_map[name][0]

def get_processes(name):
    with processes_map_lock:
        return processes_map.get(name, [])

def list_processes():
    processes = []
    with processes_map_lock:
        for n in processes_map:
            processes += processes_map[n]
    return processes


class BaseProcess(object):

    def __init__(self, name=None, loop=None, target=None, args=(), kwargs=None):
        self._name = name or 'process'

        if kwargs is None:
            kwargs = {}

        self._loop = loop
        self._target = target
        self._args = args
        self._kwargs = kwargs

        self._log = logging.getLogger("ething.%s" % self._name)
        self._start_ts = None
        self._start_evt = threading.Event()
        self._stop_evt = threading.Event()

        add_process(self)

    @property
    def name(self):
        return self._name

    @property
    def log(self):
        return self._log

    @property
    def start_ts(self):
        return self._start_ts

    def is_active(self):
        return self._start_evt.isSet() and not self._stop_evt.isSet()

    def __repr__(self):
        return str(self)

    def __str__(self):
        return '<%s name=%s>' % (type(self).__name__, self.name)

    def start(self):
        self._start_ts = time.time()
        self._start_evt.set()

    def stop(self):
        self._stop_evt.set()

    def stopped(self):
        return self._stop_evt.isSet()

    def run(self):

        self.log.debug('Process "%s" started' % self.name)

        try:
            self.setup()
        except Exception:
            self.log.exception('Exception in process "%s" in setup()' % self.name)

        try:
            self.main()
        except Exception:
            self.log.exception('Exception in process "%s" in main()' % self.name)

        try:
            self.end()
        except Exception:
            self.log.exception('Exception in process "%s" in end()' % self.name)

        self._stop_evt.set()

        remove_process(self)

        self.log.debug('Process "%s" stopped' % self.name)

    def main(self):
        if self._loop is not None:
            try:
                while not self.stopped():
                    if self._loop(*self._args, **self._kwargs) is False:
                        self.stop()
                        break
            finally:
                # Avoid a refcycle if the thread is running a function with
                # an argument that has a member that points to the thread.
                del self._loop, self._target, self._args, self._kwargs
        else:
            # run any target
            try:
                if self._target:
                    self._target(*self._args, **self._kwargs)
            finally:
                # Avoid a refcycle if the thread is running a function with
                # an argument that has a member that points to the thread.
                del self._loop, self._target, self._args, self._kwargs

    def setup(self):
        pass

    def end(self):
        pass

    def toJson(self):
        return {
            'name': self.name,
            'active': self.is_active(),
            'start_ts': int(self.start_ts) if self.start_ts is not None else self.start_ts
        }


class ThreadProcess(BaseProcess):

    def __init__(self, **kwargs):
        super(ThreadProcess, self).__init__(**kwargs)
        self._thread = None

    def start(self):
        if self._thread:
            raise Exception('Process "%s" already running' % self.name)
        # start the thread
        super(ThreadProcess, self).start()
        self._thread = threading.Thread(name=self.name, target=self.run)
        self._thread.daemon = True
        self._thread.start()

    def stop(self, timeout=5):
        super(ThreadProcess, self).stop()
        if self._thread:
            if self._thread is not threading.current_thread():
                self._thread.join(timeout)
            self._thread = None


if mode == 'greenlet':

    import eventlet
    import greenlet

    class GreenThreadProcess(BaseProcess):
        def __init__(self, **kwargs):
            super(GreenThreadProcess, self).__init__(**kwargs)

            self._g = None

        def start(self):
            if self._g:
                raise Exception('Process "%s" already running' % self.name)
            super(GreenThreadProcess, self).start()
            self._g = eventlet.spawn_n(self.run)

        def stop(self):
            super(GreenThreadProcess, self).stop()
            if self._g is not None:
                try:
                    eventlet.greenthread.kill(self._g)
                except greenlet.GreenletExit:
                    pass
                self._g = None


    Process = GreenThreadProcess

elif mode == 'gevent':

    import gevent

    class GreenThreadProcess(BaseProcess):
        def __init__(self, **kwargs):
            super(GreenThreadProcess, self).__init__(**kwargs)

            self._g = None

        def start(self):
            if self._g:
                raise Exception('Process "%s" already running' % self.name)
            super(GreenThreadProcess, self).start()
            self._g = gevent.spawn(self.run)

        def stop(self):
            super(GreenThreadProcess, self).stop()
            if self._g is not None:
                try:
                    gevent.kill(self._g)
                except gevent.GreenletExit:
                    pass
                self._g = None


    Process = GreenThreadProcess

else:
    Process = ThreadProcess


