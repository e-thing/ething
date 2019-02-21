# coding: utf-8

from future.utils import string_types
import logging
import threading
import time

from .green import mode
from .utils.weak_ref import weak_ref
from .utils import ShortId


_processes_list = []


def add_process(process):
    if process not in _processes_list:
        _processes_list.append(process)


def remove_process(process):
    if process in _processes_list:
        _processes_list.remove(process)


def get_process(*args, **kwargs):
    pp = get_processes(*args, **kwargs)
    return pp[0] if len(pp)>0 else None


def get_processes(name=None, parent=None):
    pp = []
    for p in _processes_list:
        if name is not None and p.name != name:
            continue
        if parent is not None and p.parent is not parent:
            continue
        pp.append(p)
    return pp


class BaseProcess(object):

    def __init__(self, name=None, loop=None, target=None, args=(), kwargs=None, parent=None, manager=None):
        self._name = name or 'process'

        self._id = ShortId.generate()

        self.set_parent(parent)

        if kwargs is None:
            kwargs = {}
        
        self._loop = loop
        self._target = target
        self._args = args
        self._kwargs = kwargs

        self._log = logging.getLogger("ething.%s" % self._name)
        self._start_ts = None
        self._stop_evt = threading.Event()
        self._running_evt = threading.Event()
        self._cnt = 0
        self._handlers = {}

        if manager:
            manager.add(self, auto_start=False)

    @property
    def name(self):
        return self._name

    @property
    def id(self):
        return self._id

    @property
    def log(self):
        return self._log

    @property
    def parent(self):
        return self._parent() if self._parent is not None else None

    @property
    def children(self):
        return [p for p in get_processes(parent=self)]

    @property
    def start_ts(self):
        return self._start_ts

    def set_parent(self, parent):
        self._parent = weak_ref(parent) if parent is not None else None

    @property
    def is_running(self):
        return self._running_evt.isSet()

    def add_handler(self, evt_name, handler):
        if evt_name not in self._handlers:
            self._handlers[evt_name] = []
        self._handlers[evt_name].append(handler)

    def remove_handler(self, evt_name, handler):
        if evt_name in self._handlers:
            try:
                self._handlers[evt_name].remove(handler)
            except ValueError:
                pass

    def _trigger(self, evt_name):
        if evt_name in self._handlers:
            for h in self._handlers[evt_name]:
                try:
                    h(self)
                except:
                    pass

    def __repr__(self):
        return str(self)

    def __str__(self):
        return '<%s name=%s>' % (type(self).__name__, self.name)

    def start(self):
        self._start_ts = time.time()
        self._cnt += 1
        self._stop_evt.clear()
        self._running_evt.set()
        self._trigger('start')

    def stop(self, timeout=None):
        if not self._running_evt.is_set():
            # not started !
            return

        # stop the children process
        for p in self.children:
            p.stop(timeout=timeout)

        self._running_evt.clear()

        if timeout is not None:
            if not self._stop_evt.wait(timeout):
                # kill the process
                self.kill()

    def kill(self):
        pass # to be implemented if possible

    def run(self):

        self.log.debug('Process "%s" started' % self.name)

        try:
            self.setup()
        except Exception:
            self.log.exception('Exception in process "%s" in setup()' % self.name)
        else:
            try:
                self.main()
            except Exception:
                self.log.exception('Exception in process "%s" in main()' % self.name)

        try:
            self.end()
        except Exception:
            self.log.exception('Exception in process "%s" in end()' % self.name)

        self._stop_evt.set()

        self.log.debug('Process "%s" stopped after %f sec' % (self.name, time.time() - self._start_ts))

        self._trigger('end')

    def main(self):
        if self._loop is not None:
            try:
                while self.is_running:
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
        parent = self.parent
        if isinstance(parent, BaseProcess):
            parent = parent.id
        return {
            'id': self.id,
            'name': self.name,
            'parent': parent,
            'active': self.is_running,
            'start_ts': int(self.start_ts) if self.start_ts is not None else self.start_ts
        }

    def restart(self, timeout=None):
        if self.is_running:
            self.stop(timeout=timeout)
            self.start()


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

    def run(self):
        t = self._thread
        super(ThreadProcess, self).run()
        if self._thread is t:
            self._thread = None

    def kill(self):
        if self._thread is not None:
            # unable to kill a thread ! just leave the reference
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

        def run(self):
            g = self._g
            super(GreenThreadProcess, self).run()
            if self._g is g:
                self._g = None

        def kill(self):
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

        def run(self):
            g = self._g
            super(GreenThreadProcess, self).run()
            if self._g is g:
                self._g = None

        def kill(self):
            if self._g is not None:
                try:
                    gevent.kill(self._g)
                except gevent.GreenletExit:
                    pass
                self._g = None


    Process = GreenThreadProcess

else:
    Process = ThreadProcess


#
# Process Manager
#

class ManagerItem(object):

    def __init__(self, process, manager):
        self._manager = manager
        self.ref(process)

    def _get_weak_ref(self):
        wrp = self._weak_ref()
        if wrp is None:
            self._destroy()
        return wrp

    def _destroy(self):
        try:
            self._manager._processes.remove(self)
        except ValueError:
            pass

    @property
    def process(self):
        if self._process is not None:
            return self._process
        return self._get_weak_ref()

    def ref(self, process):
        self._process = process
        self._weak_ref = weak_ref(process)

    def make_weak(self):
        self._process = None
        self._get_weak_ref()


class Manager(object):

    def __init__(self):
        self._processes = []
        self._started = False

    def find(self, filter=None, name=None, parent=None):
        res = []
        for p_ in list(self._processes):
            p = p_.process
            if p is None: continue
            if filter is not None and not filter(p):
                continue
            if name is not None and p.name != name:
                continue
            if parent is not None and p.parent is not parent:
                continue
            res.append(p)
        return res

    @property
    def processes(self):
        return self.find()

    def __getitem__(self, item):
        p = self.get(id)
        if p is None:
            raise KeyError('no process %s' % item)
        return p

    def get(self, id):
        return self.find_one(filter=lambda p: p.id == id)

    def find_one(self, *args, **kwargs):
        pp = self.find(*args, **kwargs)
        return pp[0] if len(pp) > 0 else None

    def add(self, process, auto_start=True):
        if not isinstance(process, BaseProcess):
            raise Exception('not a process instance')

        if process.id in self:
            # already in the list
            return

        process.add_handler('start', self._process_start_handler)
        process.add_handler('end', self._process_end_handler)

        self._processes.append(ManagerItem(process, self))

        if self._started and auto_start:
            # automatically start
            if not process.is_running:
                process.start()

        return process

    def remove(self, process, stop=True, timeout=None):
        if isinstance(process, string_types):
            process = self.get(process)
            if process is None: return
        p_ = self._get_p_item(process)
        if p_ is not None:
            self._processes.remove(p_)

            process.remove_handler('start', self._process_start_handler)
            process.remove_handler('end', self._process_end_handler)

            if stop and process.is_running:
                process.stop(timeout=timeout)

    def _get_p_item(self, process):
        for p_ in list(self._processes):
            if p_.process is process:
                return p_

    def _process_start_handler(self, process):
        p_ = self._get_p_item(process)
        if p_ is not None:
            p_.ref(process)

    def _process_end_handler(self, process):
        p_ = self._get_p_item(process)
        if p_ is not None:
            p_.make_weak()

    def start(self):
        self._started = True
        # start all processes
        for p in self.processes:
            if not p.is_running:
                p.start()

    def stop(self, timeout=None):
        self._started = False
        # stop all processes
        for p in self.processes:
            if p.is_running:
                p.stop(timeout=timeout)

    def clear(self):
        for p in self.processes:
            self.remove(p)

    def toJson(self):
        return self.processes