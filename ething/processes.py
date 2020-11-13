# coding: utf-8
import logging
import threading
import gevent
from .utils import generate_id, getmembers
import inspect
import weakref
import time
from collections.abc import Mapping, Sequence


__all__ = [
    'ProcessCollection',
    'Process',
    'run',
    'generate_instance_processes',
    'process',
    'processes'
]


LOGGER = logging.getLogger(__name__)


class ProcessCollection(Mapping):

    def __init__(self, parent=None, weak=False):
        self._processes = dict()
        self._parent = parent
        self._weak = weak

    @property
    def parent(self):
        return self._parent

    def _items(self):
        if self._weak:
            # filter the invalid ref
            ret = list()
            for pid in list(self._processes):
                _i = self._processes[pid]() # check weakref
                if _i is not None:
                    ret.append(_i)
                else:
                    del self._processes[pid]
            return ret
        else:
            return list(self._processes.values())

    def add(self, process=None, start=True, **kwargs):
        parent = self.parent

        if process is None:
            process = Process(**kwargs)
        elif isinstance(process, Process):
            # process instance
            pass
        elif inspect.isclass(process) and issubclass(process, Process):
            # Process subclass
            if parent is not None:
                process = process(parent, **kwargs)
            else:
                process = process(**kwargs)
        elif callable(process):
            # create a process
            process = Process(target=process, **kwargs)
        elif isinstance(process, Sequence):
            for p in process:
                self.add(p, start, **kwargs)
            return
        else:
            raise Exception('not a process')

        if parent is not None:
            process.parent = parent

        self._processes[process.id] = (weakref.ref(process) if self._weak else process)

        if start:
            process.start()

        return process

    def stop(self, obj, timeout=3):
        if not isinstance(obj, Process):
            obj = self[obj]
        elif obj not in self:
            raise KeyError('process not found')
        return obj.stop(timeout)

    def stop_all(self, timeout=3):
        processes = list(self)
        
        for p in processes:
            p.stop_async()
        
        t0 = time.time()
        for p in processes:
            time_left = timeout  - (time.time() - t0)
            if time_left < 0:
                time_left = 0
            p.stop(timeout=time_left)

    def __iter__(self):
        return iter(self._items())

    def __getitem__(self, key):
        """
        the key can either be a process instance or a process id
        """
        for p in self._items():
            if p == key or p.id == key:
                return p
        raise KeyError

    def __len__(self):
        return len(self._items())

    def __delitem__(self, key):
        p = self[key]
        p.stop()
        del self._processes[p.id]


processes = ProcessCollection(weak=True)


class Process(object):
    """

    Process is similar to Thread: it represents an activity that is run in a separate thread of control.


    Example::

        def long_running_process():
            while True:
                process_something() # must not be blocking
                # do not forget to sleep as often as possible for the global event loop to process
                time.sleep(0.1)

        # create a new process :
        process = Process(target=long_running_process)
        process.start()

        # to stop the process, simply do:
        process.stop() # by default, after 3 secondes the process will be killed


        # you may override the run() method instead of using the target argument.

        class MyProcess(Process):

            def run(self):
                while self.is_running:
                    process_something() # must not be blocking
                    # do not forget to sleep as often as possible for the global event loop to process
                    time.sleep(0.1)

        process = MyProcess()
        process.start()

    """
    def __init__(self, target=None, args=(), kwargs=None, terminate=None, parent=None, id=None):
        """

        :param target: target is the callable object to be invoked by the run() method. Use either target or loop but not both.
        :param args: args is the argument tuple for the target or loop invocation. Defaults to ().
        :param kwargs: kwargs is a dictionary of keyword arguments for the target or loop invocation. Defaults to {}.
        :param terminate: a callable that is invoked on stop()
        :param parent: any object. If a process is provided, all child processes will be automatically killed when the parent process stop.
        :param id: The id of the process. It can be useful to easily find a process in a collection. If not provided, the id will be automatically generated.
        """
        self._id = id or generate_id()

        self.parent = parent

        if kwargs is None:
            kwargs = {}

        self._target = weakref.WeakMethod(target) if inspect.ismethod(target) else target
        self._args = args
        self._kwargs = kwargs
        self._terminate = weakref.WeakMethod(terminate) if inspect.ismethod(terminate) else terminate

        self._reset()

        if self._id in processes:
            raise Exception('A process with the same id already exist ! Use Process.restart() method instead.')

        processes.add(self, False)

    @property
    def id(self):
        return self._id

    @property
    def parent(self):
        return self._parent() if self._parent is not None else None

    @parent.setter
    def parent(self, p):
        self._parent = weakref.ref(p) if p is not None else None

    @property
    def is_running(self):
        return not self._ask_stop and self.is_alive()

    def __repr__(self):
        return str(self)

    def __str__(self):
        return '<%s id=%s running=%s>' % (type(self).__name__, self.id, self.is_running)

    def start(self):
        """
        Start the process.
        """
        if self._started.is_set():
            raise Exception('The process has already been started. Use restart() to run it again.')

        self._started.set()
        self._ask_stop = False

        self._g = gevent.spawn(self._run)

    def stop(self, timeout=3):
        """
        Stop the process.

        :param timeout: Kill the process after the timeout occurs. If None, the process is immediately killed.
        """
        if self.is_alive():
            # must be running
            
            if not self._ask_stop:
                self._ask_stop = True # terminate only 1 time
                
                if self._terminate is not None:
                    # must be run anyway for clean exit
                    terminate = self._terminate
                    if isinstance(terminate, weakref.WeakMethod):
                        terminate = terminate()
                    if terminate:
                        try:
                            terminate()
                        except:
                            pass

            if timeout > 0:
                # wait for exit

                if self._stopped.wait(timeout):
                    return
            
            if timeout == -1:
                # async
                return self._stopped

            # kill it !
            try:
                gevent.kill(self._g)
            except gevent.GreenletExit:
                pass

            self._end()
    
    def stop_async(self):
        return self.stop(timeout=-1)

    def join(self, timeout=None):
        """
        wait until the process has stopped.

        :param timeout: Wait until the timeout occurs. If None, wait until the process finished.
        :return: True if the process exited
        """
        return self._stopped.wait(timeout)

    def restart(self):
        self.stop()
        self._reset()
        self.start()

    def _reset(self):
        self.result = None
        self.exception = None

        self._started = threading.Event()
        self._stopped = threading.Event()
        self._ask_stop = False

    def _run(self):
        """
        Do not override this method but run() instead.
        """

        try:
            self.result = self.run()
        except Exception as e:
            LOGGER.exception('Exception in process "%s"', self)
            self.exception = e

        self._end()

    def _end(self):
        self._stopped.set()

        # stop also the children
        for p in processes:
            if p.parent == self:
                p.stop()

        del self._g

        # free up memory (not needed)
        # del self._target
        # del self._args
        # del self._kwargs
        # del self._terminate
        # del self._parent

    def is_alive(self):
        return self._started.is_set() and not self._stopped.is_set()

    def run(self):
        """
        Invoke the target callable. To be override if necessary.
        """
        if self._target:
            target = self._target
            if isinstance(target, weakref.WeakMethod):
                target = target()
                if not target:
                    return
            return target(*self._args, **self._kwargs)
        else:
            raise Exception('empty process')



def run(target, **kwargs):
    sync = kwargs.pop('kwargs', None)
    kwargs['target'] = target
    p = Process(**kwargs)
    p.start()
    if sync:
        p.join()
    return p


# decorator

def _is_method(func):
    """return True if the function is a method"""
    spec = inspect.getfullargspec(func)
    return bool(spec.args and spec.args[0] == 'self')


def process(*args, **kwargs):
    def w(func):
        if _is_method(func):
            # tag it only. then call generate_instance_processes(instance)
            setattr(func, '_process', (args, kwargs))
        else:
            # function decorator
            p = Process(func, *args, **kwargs)
            p.start()
        return func
    return w


def generate_instance_processes(instance):
    # find any @process decorator
    processes = list()
    for name, func in getmembers(instance, lambda x: hasattr(x, '_process')):
        f = getattr(instance, name)
        args, kwargs = getattr(f, '_process')
        processes.append(Process(f, *args, **kwargs))
    return processes


def print_info(no_print=False, printer=None):
    _processes = list(processes)
    _lines = list()

    def _children(p):
        return [_p for _p in _processes if _p.parent == p]

    def _print(p, level=0):
        _processes.remove(p)
        line = ''.rjust(level * 4) + str(p)
        _lines.append(line)
        for _p in _children(p):
            _print(_p, level=level+1)

    # make a tree
    for p in list(_processes):
        if p.parent is None:
            # no parent, print it
            _print(p)

    if _processes:
        # unnested child
        _parents = set([p.parent for p in _processes])
        for p in _parents:
            _print(p)

    if not no_print:
        for l in _lines:
            print(l) if printer is None else printer(l)
    else:
        return '\n'.join(_lines)
