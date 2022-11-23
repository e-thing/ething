# coding: utf-8

from .utils import generate_id, getmembers
import time
import datetime
import logging
import inspect
import threading
import weakref
import asyncio


__all__ = [
    'bind_instance',
    'unbind',
    'tick',
    'set_interval',
    'delay',
    'at',
    'global_instance'
]


LOGGER = logging.getLogger(__name__)

TICK_INTERVAL = 1 # one sec


class Task(object):

    """
    Represent a Task.
    """

    def __init__(self, scheduler, target, args=(), kwargs=None, name=None, instance=None, condition=None, allow_multiple=False, **params):
        """
        Task should not be instantiated manually but through a Scheduler.

        :param scheduler: the scheduler this task is bind to.
        :param target: target is the callable object to be invoked.
        :param args: args is the argument tuple for the target invocation. Defaults to ().
        :param kwargs: kwargs is a dictionary of keyword arguments for the target invocation. Defaults to {}.
        :param name: the task name.
        :param instance: the instance this task is bind to. Default is None.
        :param condition: an optional callable to test if the task can be executed or not.
        :param allow_multiple: If True, this task can be executed multiple time simultaneously. Default to False: if the previous invocation is not terminated, the current invocation is skipped.
        """
        if not callable(target):
            raise Exception('target must be callable')

        self._scheduler = scheduler

        self._id = generate_id()

        self._params = params

        self._target = weakref.WeakMethod(target) if inspect.ismethod(target) else target
        if instance is None and hasattr(target, '__self__'):
            instance = target.__self__

        self._args = args
        self._kwargs = kwargs or {}
        self._name = name
        if not self._name:
            if instance is not None:
                self._name = "%s.%s" % (type(instance).__name__, target.__name__)
            else:
                self._name = target.__name__
        self._instance = weakref.ref(instance) if instance is not None else None
        self._condition = condition
        self._allow_multiple = allow_multiple

        self._last_run = None
        self._executed_count = 0
        self._valid = True
        self._t0 = time.time()

        self._aio_tasks = list()

        scheduler.add(self)

    def __getattr__(self, item):
        if item in self._params:
            return self._params[item]
        else:
            raise AttributeError()

    def __repr__(self):
        return str(self)

    def __str__(self):
        return '<scheduler.task %s>' % (self._name, )

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name

    @property
    def executed_count(self):
        return self._executed_count

    @property
    def target(self):
        return self._target() if isinstance(self._target, weakref.WeakMethod) else self._target

    @property
    def args(self):
        return self._args

    @property
    def kwargs(self):
        return self._kwargs

    @property
    def instance(self):
        return self._instance() if self._instance is not None else None

    @property
    def allow_multiple(self):
        return self._allow_multiple

    def is_running(self):
        self._clean_aio_tasks()
        return len(self._aio_tasks) != 0

    def _clean_aio_tasks(self):
        # remove asyncio tasks that are done
        self._aio_tasks[:] = [t for t in self._aio_tasks if not t.done()]

    def run(self):

        if not self.is_valid():
            return False

        if not self._allow_multiple:
            # check if already being executed and not yet finished
            if self.is_running():
                return False

        target = self.target
        if target is not None:

            if self._instance is not None:
                instance = self._instance()
                if instance is None:
                    # the instance has been destroyed
                    self._valid = False
                    return False
            else:
                instance = None

            if self._condition is not None:
                try:
                    if not self._condition(self):
                        return False
                except:
                    return False

            async def _wrapper():
                LOGGER.debug("running task '%s'" % self._name)
                self._last_run = time.time()
                self._executed_count += 1

                try:
                    await target(*self.args, **self.kwargs)
                except asyncio.CancelledError:
                    LOGGER.exception("task '%s' cancelled" % self._name)
                except:
                    LOGGER.exception("exception in task '%s'" % self._name)

            self._aio_tasks.append(asyncio.create_task(_wrapper(), name=str(self)))

            return True
        else:  # lost reference
            self._valid = False

        return False

    def is_valid(self):
        return self._valid

    def is_time_to_run(self, t):
        raise NotImplementedError()

    async def cancel(self):
        # cancel all running asyncio tasks
        for t in self._aio_tasks:
            if not t.done():
                t.cancel()
                try:
                    await t
                except asyncio.CancelledError:
                    pass # handled in "async def _wrapper()"
        self._clean_aio_tasks()



class TickTask(Task):
    def is_time_to_run(self, t):
        return True


class IntervalTask(Task):
    def __init__(self, interval, *args, **kwargs):
        start_in_sec = kwargs.pop('start_in_sec', 0)
        super(IntervalTask, self).__init__(*args, **kwargs)
        self._interval = interval
        self._start_in_sec = start_in_sec

    def is_time_to_run(self, t):
        if self._last_run is None:
            return (t - self._t0) >= self._start_in_sec
        else:
            return (t - self._last_run) >= self._interval


class DelayTask(Task):
    def __init__(self, delay, *args, **kwargs):
        super(DelayTask, self).__init__(*args, **kwargs)
        self._delay = delay

    def is_time_to_run(self, t):
        if self._last_run is None: # run only one time
            return (t - self._t0) >= self._delay

    def run(self):
        r = super(DelayTask, self).run()
        self._valid = False # run only one time
        return r


class AtTask(Task):
    def __init__(self, *args, **kwargs):
        hour = kwargs.pop('hour', '*')
        min = kwargs.pop('min', 0)
        super(AtTask, self).__init__(*args, **kwargs)
        self._hour = hour
        self._min = min

        self._next = self._compute_next_time(self._t0)

    def _compute_next_time(self, t):
        dt = datetime.datetime.fromtimestamp(t)

        dt_next = dt.replace(second=0, microsecond=0)

        if self._hour == '*':
            if self._min == '*':
                if dt_next < dt:
                    dt_next = dt_next + datetime.timedelta(minutes=1)
            else:
                dt_next = dt_next.replace(minute=self._min)
                if dt_next < dt:
                    dt_next = dt_next + datetime.timedelta(hours=1)
        else:
            dt_next = dt.replace(hour=self._hour, minute=self._min)

            if dt_next < dt:
                dt_next = dt_next + datetime.timedelta(days=1)

        return time.mktime(dt_next.timetuple())

    def is_time_to_run(self, t):
        if t > self._next:
            self._next = self._compute_next_time(t)
            return True


class Scheduler(object):
    """

    The scheduler will run registered tasks at certain time or at regular interval.

    """

    def __init__(self):
        super(Scheduler, self).__init__()
        self.tasks = []
        self.r_lock = threading.RLock()
        self._running = False

    @property
    def is_running(self):
        return self._running

    def add(self, task):
        with self.r_lock:
            self.tasks.append(task)

    def remove(self, task):
        with self.r_lock:
            if task in self.tasks:
                self.tasks.remove(task)

    def process(self):
        now = time.time()
        to_run = []

        with self.r_lock:
            for task in self.tasks[:]:
                if task.is_valid():
                    if task.is_time_to_run(now):
                        to_run.append(task)
                else:
                    # not valid anymore
                    self.tasks.remove(task)

        # release the lock before running
        for task in to_run:
            task.run()

    async def run(self):
        if self._running:
            raise Exception('Scheduler already running')

        self._running = True

        LOGGER.info("scheduler started")

        # loop
        while self._running:
            self.process()
            await asyncio.sleep(TICK_INTERVAL)

        LOGGER.info("scheduler stopping ... cancelling running tasks")

        # cancel any running tasks
        for task in self.tasks:
            await task.cancel()

        LOGGER.info("scheduler stopped")

    def start(self):
        """
        start the scheduler in the current event loop
        """

        if self._running:
            raise Exception('Scheduler already running')

        asyncio.create_task(self.run(), name="Scheduler")

    def stop(self):
        self._running = False



_scheduler = None


def global_instance():
    global _scheduler

    if _scheduler is None:
        # start the global instance
        _scheduler = Scheduler()

    return _scheduler


def bind_instance(instance):
    """
    Bind an instance.

    Example::

        from ething.scheduler import *

        class Foo:

            @set_interval(interval=30)
            def task1(self):
                # this method will be invoked every 30 seconds
                pass

            @at(12, 30)
            def task2(self):
                # this method will be invoked every day at 12h30.
                pass


        foo = Foo()

        bind_instance(foo) # task1 and task2 will be automatically registered

    :param instance: an instance with some methods decorated with set_interval, at, delay or tick
    """

    # find any scheduler decorators (@set_interval @at ...)
    tasks = list()
    for name, func in getmembers(instance, lambda x: hasattr(x, '_scheduler')):
        f = getattr(instance, name)
        installer = getattr(f, '_scheduler')
        t = installer(f)
        tasks.append(t)
    return tasks


def unbind(obj, scheduler=None):
    """
    Unregister a task, callback or instance.

    :param obj: either a task, a callback or an instance
    """
    scheduler = scheduler or global_instance()
    if isinstance(obj, Task):
        scheduler.remove(obj)
    else:
        to_remove = [t for t in scheduler.tasks if t.target == obj or t.instance is obj]

        for t in to_remove:
            scheduler.remove(t)


# decorators

def _is_method(func):
    """return True if the function is a method"""
    spec = inspect.getfullargspec(func)
    return bool(spec.args and spec.args[0] == 'self')


def _deco(callback, p):
    if callback is None:
        # create a decorator
        def d(func):
            if _is_method(func):
                # tag it only. then call bind_instance(instance)
                setattr(func, '_scheduler', p)
            else:
                # function decorator
                p(func)
            return func

        return d
    else:
        return p(callback)


def tick(callback=None, args=(), kwargs=None, scheduler=None, **params):
    """
    Run a callable every tick (ie: each time process() is called).

    :param callback: If not provided, act as a decorator.
    :param args: args is the argument tuple for the callback invocation. Defaults to ().
    :param kwargs: kwargs is a dictionary of keyword arguments for the callback invocation. Defaults to {}.
    :param params: More optional parameters. See Task class.
    :return: Task instance
    """

    def p(f):
        return TickTask(scheduler or global_instance(), f, args=args, kwargs=kwargs, **params)

    return _deco(callback, p)


def set_interval(interval, callback=None, start_in_sec=0, args=(), kwargs=None, scheduler=None, **params):
    """
    Run a callable at regular interval.

    :param interval: The amount of seconds between 2 successive calls.
    :param callback: If not provided, act as a decorator.
    :param start_in_sec: Delay the first call. Default to 0.
    :param args: args is the argument tuple for the callback invocation. Defaults to ().
    :param kwargs: kwargs is a dictionary of keyword arguments for the callback invocation. Defaults to {}.
    :param params: More optional parameters. See Task class.
    :return: Task instance
    """
    def p(f):
        return IntervalTask(interval, scheduler or global_instance(), f, args=args, kwargs=kwargs, start_in_sec=start_in_sec, **params)

    return _deco(callback, p)


def delay(delay, callback=None, args=(), kwargs=None, scheduler=None, **params):
    """
    Run a callable once after a certain delay.

    :param delay: The delay in seconds
    :param callback: If not provided, act as a decorator.
    :param args: args is the argument tuple for the callback invocation. Defaults to ().
    :param kwargs: kwargs is a dictionary of keyword arguments for the callback invocation. Defaults to {}.
    :param params: More optional parameters. See Task class.
    :return: Task instance
    """
    def p(f):
        return DelayTask(delay, scheduler or global_instance(), f, args=args, kwargs=kwargs, **params)

    return _deco(callback, p)


def at(hour='*', min=0, callback=None, args=(), kwargs=None, scheduler=None, **params):
    """
    Run a callable at a certain time of a the day.

    :param hour: The hour or '*' for every hour. Default to '*'.
    :param min: The minute or '*' for every minute. Default to 0.
    :param callback: If not provided, act as a decorator.
    :param args: args is the argument tuple for the callback invocation. Defaults to ().
    :param kwargs: kwargs is a dictionary of keyword arguments for the callback invocation. Defaults to {}.
    :param params: More optional parameters. See Task class.
    :return: Task instance
    """
    def p(f):
        return AtTask(scheduler or global_instance(), f, hour=hour, min=min, args=args, kwargs=kwargs, **params)

    return _deco(callback, p)
