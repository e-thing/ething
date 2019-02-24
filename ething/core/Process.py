# coding: utf-8

from future.utils import with_metaclass
import logging
import threading
import time
import gevent
from abc import ABCMeta, abstractmethod
from .utils.weak_ref import weak_ref, proxy_method
from .utils import ShortId


class Runner(with_metaclass(ABCMeta, object)):

    def __init__(self, manager, process):
        self._manager = manager
        self._start_t = None
        self._stop_t = None
        self._cnt = 0
        self._running_evt = threading.Event()
        self._stop_evt = threading.Event()
        self._log = self._manager.log
        self._id = process.id
        self._process = process
        self._weak_ref = weak_ref(process)
        self._exception = None

    @property
    def process(self):
        if self._process is not None:
            return self._process
        return self._weak_ref()

    @property
    def id(self):
        return self._id

    @property
    def manager(self):
        return self._manager

    @property
    def log(self):
        return self._log

    @property
    def is_running(self):
        return self._running_evt.isSet()

    @property
    def start_t(self):
        return self._start_t

    @property
    def stop_t(self):
        return self._stop_t

    def run(self):
        self.log.debug('Process "%s" started' % self._process)

        self._started()

        try:
            self._process.run()
        except Exception as e:
            self._exception = e
            self.log.exception('Exception in process "%s"' % self._process)

        self._end()

    def start(self):
        if self._running_evt.is_set():
            raise Exception('the process already started')

        process = self._weak_ref()
        if process is None:
            raise Exception('the process has been destroyed')

        self._process = process
        self._exception = None
        self._start_t = time.time()
        self._stop_t = 0
        self._cnt += 1
        self._stop_evt.clear()
        self._running_evt.set()
        self.launch()

    def stop(self, block=True, timeout=None):
        if not self._running_evt.is_set():
            # not started !
            return

        self._process.terminate()

        self._running_evt.clear()

        if not block:
            return

        if not self._stop_evt.wait(timeout):
            # kill the process
            try:
                self.kill()
            finally:
                self._end()

    def wait(self, timeout=None):
        """wait until the process is over"""
        return self._stop_evt.wait(timeout)

    @abstractmethod
    def launch(self):
        raise NotImplementedError()

    @abstractmethod
    def kill(self):
        raise NotImplementedError()

    def _started(self):
        pass

    def _end(self):
        if self._process is not None:
            self._running_evt.clear()
            self._stop_t = time.time()
            self.log.debug('Process "%s" stopped after %f sec' % (self._process, self._stop_t - self._start_t))

            # kill any children processes left
            children = self._manager.find(filter=lambda p: p.parent is self._process)
            for p in children:
                p.stop(timeout=0)

            self._process = None
            self._manager._process_evt('end', self)
            self._stop_evt.set()


class GeventRunner(Runner):

    def launch(self):
        self._g = gevent.spawn(self.run)

    def kill(self):
        try:
            gevent.kill(self._g)
        except gevent.GreenletExit:
            pass


class Manager(object):
    RUNNER = GeventRunner

    def __init__(self, runner_cls=None, log=None, start=None):
        self._map = {}
        if start is None:
            start = True
        self._started = start
        self._runner_cls = runner_cls or self.RUNNER
        if self._runner_cls is None:
            raise Exception('no runner class defined')
        self._log = log or logging.getLogger("ething.processes")

    @property
    def log(self):
        return self._log

    def _runners(self):
        r = []
        for id in list(self._map):
            p = self._map[id]
            if p.process is None:
                del self._map[id]
            else:
                r.append(p)
        return r

    @property
    def processes(self):
        return [r.process for r in self._runners()]

    def find(self, filter=None, name=None, parent=None):
        res = []
        for p in self.processes:
            if p is None: continue
            if filter is not None and not filter(p):
                continue
            if name is not None and p.name != name:
                continue
            if parent is not None and p.parent is not parent:
                continue
            res.append(p)
        return res

    def __getitem__(self, item):
        return self._get(item).process

    def get(self, id):
        try:
            return self[id]
        except IndexError:
            pass

    def _get(self, process):
        if isinstance(process, Process):
            id = process.id
        else:
            id = process
        if id in self._map:
            r = self._map[id]
            if r.process is None:
                del self._map[id]
            else:
                return r
        raise IndexError('the process id=%s does not exist' % process)

    def attach(self, process, auto_start=True):
        if not isinstance(process, Process):
            raise Exception('not a process instance')

        if process.id in self:
            # already in the list
            return

        if process.manager is not None and process.manager is not self:
            raise Exception('this process is already attached to a manager')

        process.manager = self

        self._map[process.id] = self._runner_cls(self, process)

        if auto_start:
            # automatically start
            if not process.is_running:
                process.start()

        return process

    def detach(self, process, stop=True, timeout=None):
        r = self._get(process)

        if stop:
            r.stop(timeout=timeout)

        self._map.pop(r.id, None)

        process.manager = None

    def start(self):
        self._started = True
        # start all processes
        for p in self._runners():
            if not p.is_running:
                p.start()

    def stop(self, timeout=None):
        self._started = False
        # stop all processes
        for r in self._runners():
            if r.is_running:
                r.stop(timeout=timeout)

    def clear(self):
        for r in self._runners():
            r.stop()
        self._map.clear()

    def p_start(self, process):
        p = self._get(process)

        if p.is_running:
            raise Exception('Process "%s" already running' % p)

        if not self._started:
            return

        return p.start()

    def p_stop(self, process, *args, **kwargs):
        p = self._get(process)
        return p.stop(*args, **kwargs)

    def p_is_running(self, process):
        p = self._get(process)
        return p.is_running

    def p_wait(self, process, *args, **kwargs):
        p = self._get(process)
        return p.wait(*args, **kwargs)

    def _process_evt(self, evt, runner):
        if evt == 'end':
            if runner.process is None:
                # no more reference to this process, remove it
                self._map.pop(runner.id, None)

    def toJson(self):
        j = []
        for r in self._runners():
            process = r.process

            parent = process.parent
            if isinstance(parent, Process):
                parent = parent.id

            start_ts = None
            stop_ts = None

            if r.start_t is not None:
                start_ts = int(r.start_t)

            if r.stop_t is not None:
                stop_ts = int(r.stop_t)

            rj = {
                'id': process.id,
                'name': process.name,
                'parent': parent,
                'active': r.is_running,
                'start_ts': start_ts,
                'stop_ts': stop_ts
            }

            j.append(rj)

        return j


class Process(object):
    def __init__(self, name=None, loop=None, target=None, args=(), kwargs=None, terminate=None, parent=None, manager=None, log=None, id=None):
        self._id = id or ShortId.generate()
        self._name = name or ('process_%s' % self._id)

        self.parent = parent

        if kwargs is None:
            kwargs = {}

        self._loop = proxy_method(loop)
        self._target = proxy_method(target)
        self._args = args
        self._kwargs = kwargs
        self._terminate = proxy_method(terminate)

        self._log = log or logging.getLogger("ething.%s" % self._name)

        self.manager = manager

        if manager:
            manager.attach(self, auto_start=False)

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

    @parent.setter
    def parent(self, p):
        self._parent = weak_ref(p) if p is not None else None

    @property
    def _manager(self):
        if self.manager is None:
            raise AttributeError('No manager bind to the process %s' % self)
        return self.manager

    @property
    def is_running(self):
        return self._manager.p_is_running(self)

    def __repr__(self):
        return str(self)

    def __str__(self):
        return '<%s id=%s name=%s>' % (type(self).__name__, self.id, self.name)

    def start(self):
        return self._manager.p_start(self)

    def stop(self, *args, **kwargs):
        return self._manager.p_stop(self, *args, **kwargs)

    def wait(self, *args, **kwargs):
        return self._manager.p_wait(self, *args, **kwargs)

    def run(self):

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

    def terminate(self):
        if self._terminate is not None:
            self._terminate()

    def main(self):
        if self._loop is not None:
            while self.is_running:
                if self._loop(*self._args, **self._kwargs) is False:
                    self.stop()
                    break
        else:
            if self._target:
                self._target(*self._args, **self._kwargs)

    def setup(self):
        pass

    def end(self):
        pass

    def restart(self, timeout=None):
        self.stop(timeout=timeout)
        self.start()

    def destroy(self, timeout=None):
        """free memory"""
        try:
            self._manager.detach(self, timeout=timeout)
        finally:
            self.__dict__.clear()