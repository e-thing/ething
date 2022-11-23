# coding: utf-8
import logging
import threading
import asyncio
from .utils import generate_id, getmembers
import inspect
import weakref
import time
from collections.abc import Mapping, Sequence
import sys
import trace

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
                _i = self._processes[pid]()  # check weakref
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

    def stop_all(self):
        processes = list(self)
        for p in processes:
            p.stop()

    async def wait(self, timeout=None, process_ids=None):

        if process_ids is None:
            processes = list(self)
        else:
            processes = list()
            for p in process_ids:
                try:
                    processes.append(self[p])
                except KeyError:
                    pass  # skip unknown process

        t0 = time.time()
        for p in processes:
            # compute timeout
            if timeout is None:
                time_left = None
            else:
                time_left = timeout - (time.time() - t0)
                if time_left < 0:
                    time_left = 0
            await p.wait(timeout=time_left)

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

    Process represents a separate processing that is run in a background.
    Usefull if you want to run long process and/or sync function.
    Accept :
       - async function, will be run in the current event loop
       - sync function, will be run in a thread

    Workflow :
         |    target is executed     |   children cancelled   |
         ^     .is_running==True     ^    .is_running==False  ^
     .start()                     .stop()                 done()==True
                                    or
                                end of target

    Example::

        def long_running_process():
            time.sleep(10)

        # create a new process :
        process = Process(target=long_running_process)
        process.start()

        # to stop the process, simply do:
        process.stop() # by default, after 3 secondes the process will be killed


        # you may override the run() method instead of using the target argument.
        class MyProcess(Process):

            def run(self):
                while self.is_running: # will be False as soon as stop() is called
                    # process something blocking
                    time.sleep(1)

        process = MyProcess()
        process.start()

    """

    TYPE_IO_TASK = 1
    TYPE_THREAD = 2

    def __init__(self, target=None, args=(), kwargs=None, terminate=None, parent=None, id=None, name=None):
        """

        :param target: target is the callable object to be invoked by the run() method.
        :param args: args is the argument tuple for the target or loop invocation. Defaults to ().
        :param kwargs: kwargs is a dictionary of keyword arguments for the target or loop invocation. Defaults to {}.
        :param terminate: a callable that is invoked on stop()
        :param parent: any object. If a process is provided, all child processes will be automatically killed when the parent process stop.
        :param id: The id of the process. It can be useful to easily find a process in a collection. If not provided, the id will be automatically generated.
        """
        self._id = id or generate_id()
        self._name = name

        self.parent = parent  # go through the setter and create a weak ref

        self._g = None
        self._g_type = None
        self._end_evt = asyncio.Event()
        self._ask_stop = False

        self.result = None
        self.exception = None

        self._count = 0
        self._t_start = None
        self._t_end = None

        if target:
            if inspect.ismethod(target):
                self._target = weakref.WeakMethod(target)
                if parent is None:
                    self.parent = target.__self__
            else:
                self._target = target

            self._args = args

            if kwargs is None:
                kwargs = {}

            self._kwargs = kwargs
            self._terminate = weakref.WeakMethod(terminate) if inspect.ismethod(terminate) else terminate

        else:
            self._target = self.run
            self._args = ()
            self._kwargs = {}
            self._terminate = None

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
        """
        Return true when the process is running and before it is stopped.
        """
        return self._g is not None and not self.done() and not self._ask_stop

    @property
    def count(self):
        return self._count

    def done(self):
        """
        Return true when the process is completely finished.
        """
        if self._g is not None:
            return not self._end_evt.is_set()
        return False

    def __repr__(self):
        return str(self)

    def __str__(self):
        return '<%s id=%s name=%s running=%s>' % (type(self).__name__, self.id, self._name, self.is_running)

    def running_time(self):
        if self._t_start is not None:
            if self._t_end is not None:
                # finished
                return self._t_end - self._t_start
            else:
                # still running
                return time.time() - self._t_start
        else:
            # not started
            return None

    def start(self):
        """
        Start the process.
        """
        # check if not already running
        if not self.done():
            raise Exception("Process '%s' already running" % self)

        # reset everything
        self.result = None
        self.exception = None
        self._ask_stop = False
        self._end_evt.clear()
        self._g = None
        self._g_type = None
        self._t_start = None
        self._t_end = None

        # last check
        target = self._target
        if isinstance(target, weakref.WeakMethod):
            target = target()
            if not target:
                # todo: raise an exception ?
                return  # target function no more available !

        # really start from here
        self._t_start = time.time()
        self._count += 1

        if inspect.iscoroutinefunction(target):

            async def _coroutine_wrapper():
                try:
                    self.result = await target(*self._args, **self._kwargs)
                except asyncio.CancelledError as e:
                    LOGGER.debug('process "%s" cancelled', self)
                    self.exception = e
                except Exception as e:
                    LOGGER.exception('Exception in process "%s"', self)
                    self.exception = e
                finally:
                    await self._stop_children()
                    self._end()

            # print('run coroutine')
            self._g = asyncio.create_task(_coroutine_wrapper(), name=self._name)
            self._g_type = Process.TYPE_IO_TASK
        else:
            # run in thread
            main_event_loop = asyncio.get_running_loop()

            def _end(future):
                # print('end "%s"' % self, flush=True)
                self._end()

            def _stop_children():
                task = main_event_loop.create_task(self._stop_children())
                task.add_done_callback(_end)

            def _thread_wrapper():
                try:
                    self.result = target(*self._args, **self._kwargs)
                except Exception as e:
                    LOGGER.exception('Exception in process "%s"', self)
                    self.exception = e
                finally:
                    # print('finally "%s"' % self, flush=True)
                    main_event_loop.call_soon_threadsafe(_stop_children)

            # print('run thread')
            # thread = threading.Thread(target=_thread_wrapper, daemon=False)
            thread = thread_with_trace(target=_thread_wrapper, daemon=False, name=self._name)  # this thread can be killed
            thread.start()
            self._g = thread
            self._g_type = Process.TYPE_THREAD

    def run(self):
        """
        Invoke the target callable. To be override if necessary.
        May be async or not
        """
        raise Exception('empty process')

    async def wait(self, timeout=None):
        """
        timeout can either be None or a float or int number of seconds to wait for. If timeout is None, block until the future completes.
        """
        if not self.done():
            try:
                await asyncio.wait_for(self._end_evt.wait(), timeout=timeout)
            except asyncio.TimeoutError:
                pass

            # if self._g_type == Process.TYPE_IO_TASK:
            #    try:
            #        await asyncio.wait_for(self._g, timeout=timeout)
            #    except asyncio.TimeoutError:
            #        pass
            # elif self._g_type == Process.TYPE_THREAD:
            #    try:
            #        await asyncio.wait_for(self._end_evt.wait(), timeout=timeout)
            #    except asyncio.TimeoutError:
            #        pass

    def stop(self):
        if self.is_running:
            self._ask_stop = True  # terminate only 1 time

            if self._terminate is not None:
                # must be run anyway for clean exit
                terminate = self._terminate
                if isinstance(terminate, weakref.WeakMethod):
                    terminate = terminate()
                if terminate:
                    try:
                        terminate()
                        return  # terminate was executed successfully
                    except:
                        pass

            # no terminate function (or raise an exception), must kill the thread/io_task
            if self._g_type == Process.TYPE_IO_TASK:
                self._g.cancel()
            elif self._g_type == Process.TYPE_THREAD:
                # no good way to stop a thread
                # from https://www.geeksforgeeks.org/python-different-ways-to-kill-a-thread/
                self._g.kill()

    async def _stop_children(self):
        # stop also the children
        for p in processes:
            if p.parent == self:
                p.stop()
                await p.wait()

    def _end(self):
        # is called internally at the very end
        self._end_evt.set()
        self._t_end = time.time()


def run(target, **kwargs):
    kwargs['target'] = target
    p = Process(**kwargs)
    p.start()
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
            _print(_p, level=level + 1)

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


# a usefull class to create a thread that can be killed
# cf. https://www.geeksforgeeks.org/python-different-ways-to-kill-a-thread/
class thread_with_trace(threading.Thread):
    def __init__(self, *args, **keywords):
        threading.Thread.__init__(self, *args, **keywords)
        self.killed = False

    def start(self):
        self.__run_backup = self.run
        self.run = self.__run
        threading.Thread.start(self)

    def __run(self):
        sys.settrace(self.globaltrace)
        self.__run_backup()
        self.run = self.__run_backup

    def globaltrace(self, frame, event, arg):
        if event == 'call':
            return self.localtrace
        else:
            return None

    def localtrace(self, frame, event, arg):
        if self.killed:
            if event == 'line':
                raise SystemExit()
        return self.localtrace

    def kill(self):
        self.killed = True


"""
# usefull function

import concurrent
import contextlib

# see https://stackoverflow.com/questions/63420413/how-to-use-threading-lock-in-async-function-while-object-can-be-accessed-from-mu

_pool = concurrent.futures.ThreadPoolExecutor()

#
# # lock is a threading.Lock shared between threads
# async with async_lock(lock):
#     ... access the object with the lock held ...

@contextlib.asynccontextmanager
async def async_lock(lock):
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(_pool, lock.acquire)
    try:
        yield  # the lock is held
    finally:
        lock.release()

"""
