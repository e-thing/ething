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
        self._run_t = None
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
        self._run_t = None
        self._stop_t = 0
        self._cnt += 1
        self._stop_evt.clear()
        self._running_evt.set()

        # clear result
        self._process.result = None
        self._process.exception = None

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
        self._run_t = time.time()

    def _end(self):
        if self._process is not None:
            self._running_evt.clear()
            self._stop_t = time.time()
            duration = -1.
            if self._run_t is not None:
                duration = self._stop_t - self._run_t
            self.log.debug('Process "%s" stopped after %f sec' % (self._process, duration))

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

        if process.id not in self:

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

    def p_start(self, process, block=False, timeout=None):
        try:
            p = self._get(process)
        except IndexError:
            self.attach(process, auto_start=False)
            p = self._get(process)

        if p.is_running:
            raise Exception('Process "%s" already running' % p)

        if self._started:
            p.start()

        if block:
            p.wait(timeout)

        return process

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
    """

    Process is similar to Thread: it represents an activity that is run in a separate thread of control.


    Example::

        def long_running_process():
            while True:
                process_something()

        # create a new process :
        proc = Process(target=long_running_process)

        # the process will automatically be launched by the manager :
        core.process_manager.attach(proc)

        # to stop the process, simply do:
        proc.stop()

        # iterative process:
        def loop_process():
            process_something()

        # loop_process will be called every seconds
        proc = Process(loop=loop_process, loop_interval=1)


    .. note:: you may override the setup()/main()/end() methods instead of using the target or loop arguments.

    """
    def __init__(self, name=None, loop=None, loop_interval=None, target=None, args=(), kwargs=None, terminate=None, parent=None, manager=None, log=None, id=None):
        """

        :param name: The name of the process.
        :param loop: loop is the callable object to be invoked indefinitely by the run() method. Use either target or loop but not both.
        :param loop_interval: the number of seconds to wait between 2 successive loop call. Default to None (no wait).
        :param target: target is the callable object to be invoked by the run() method. Use either target or loop but not both.
        :param args: args is the argument tuple for the target or loop invocation. Defaults to ().
        :param kwargs: kwargs is a dictionary of keyword arguments for the target or loop invocation. Defaults to {}.
        :param terminate: a callable that is invoked on stop()
        :param parent: if a process is provided, all child processes will be automatically killed when the parent process stop.
        :param manager: a manager to bind this process to. If not provided, this process must be attach manually to a manager.
        :param log: a specific logger
        :param id: a specific id. Must be id. If not provided, an id will be auto generated.
        """
        self._id = id or ShortId.generate()
        self._name = name or ('process_%s' % self._id)

        self.parent = parent

        if kwargs is None:
            kwargs = {}

        self._loop = proxy_method(loop)
        self._loop_interval = loop_interval
        self._target = proxy_method(target)
        self._args = args
        self._kwargs = kwargs
        self._terminate = proxy_method(terminate)

        self.result = None
        self.exception = None

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
        """
        Start the process. Normally, this method should not be used. The manager will do it for you.

        """
        return self._manager.p_start(self)

    def stop(self, *args, **kwargs):
        """
        Stop the process.

        :param block: Wait until the process terminates. Default to True.
        :param timeout: Kill the process after the timeout occurs.
        """
        return self._manager.p_stop(self, *args, **kwargs)

    def wait(self, *args, **kwargs):
        """
        wait until the process has stopped.

        :param timeout: Wait until the timeout occurs. Default wait indefinitely.
        """
        return self._manager.p_wait(self, *args, **kwargs)

    def run(self):
        """
        Do not override this method but main() instead.
        """
        try:
            self.setup()
        except Exception as e:
            self.log.exception('Exception in process "%s" in setup()' % self.name)
            self.exception = e
        else:
            try:
                self.result = self.main()
            except Exception as e:
                self.log.exception('Exception in process "%s" in main()' % self.name)
                self.exception = e

        try:
            self.end()
        except Exception as e:
            self.log.exception('Exception in process "%s" in end()' % self.name)
            if self.exception is None:
                self.exception = e

    def terminate(self):
        """
        is called on stop().
        """
        if self._terminate is not None:
            self._terminate()

    def main(self):
        """
        Invoke the target or loop callable. To be override if necessary.
        """
        if self._loop is not None:
            while self.is_running:
                if self._loop(*self._args, **self._kwargs) is False:
                    self.stop()
                    break
                if self._loop_interval is not None:
                    time.sleep(self._loop_interval)
        else:
            if self._target:
                return self._target(*self._args, **self._kwargs)

    def setup(self):
        """
        To be override if necessary.
        """
        pass

    def end(self):
        """
        To be override if necessary.
        """
        pass

    def restart(self, timeout=None):
        """
        restart the process.

        :param timeout: the timeout when stopping the process before killing it !
        """
        self.stop(timeout=timeout)
        self.start()

    def destroy(self, timeout=None):
        """
        stop this process if it was started and free up memory

        :param timeout: the timeout when stopping the process before killing it !
        """
        try:
            self._manager.detach(self, timeout=timeout)
        finally:
            self.__dict__.clear()