# coding: utf-8

from .utils import ShortId, getmembers
import inspect
import time
import datetime
import logging

import threading
from .utils.weak_ref import weak_ref, proxy_method


_LOGGER = logging.getLogger('scheduler')


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

        self._id = ShortId.generate()

        self._params = params

        self._target = proxy_method(target)
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
        self._instance = weak_ref(instance) if instance is not None else None
        self._condition = condition
        self._allow_multiple = allow_multiple

        self._last_run = None
        self._executed_count = 0
        self._valid = True
        self._t0 = time.time()

    def __getattr__(self, item):
        if item in self._params:
            return self._params[item]
        else:
            raise AttributeError()

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
        return self._target

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

    def run(self):
        target = self.target
        if target is not None:

            if self._instance is not None:
                instance = self._instance()
                if instance is None:
                    # the instance has been destroyed
                    self._valid = False
                    return
            else:
                instance = None

            self._last_run = time.time()
            self._executed_count += 1

            if self._condition is not None:
                try:
                    if not self._condition(self):
                        return False
                except:
                    return False

            try:
                self._scheduler.execute(self)
            except:
                _LOGGER.exception('exception in task "%s"' % self._name)

            return True
        else:  # lost reference
            self._valid = False

    def is_valid(self):
        return self._valid

    def is_time_to_run(self, t):
        raise NotImplementedError()


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
        super(DelayTask, self).run()
        self._valid = False # run only one time


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


def tick(**kwargs):
    def d(func):
        setattr(func, '_scheduler', ('tick', (), kwargs))
        return func
    return d


def set_interval(interval, start_in_sec=0, **kwargs):
    def d(func):
        kwargs['start_in_sec'] = start_in_sec
        setattr(func, '_scheduler', ('set_interval', (interval,), kwargs))
        return func
    return d


def delay(delay, **kwargs):
    def d(func):
        setattr(func, '_scheduler', ('delay', (delay,), kwargs))
        return func
    return d


def at(hour='*', min=0, **kwargs):
    def d(func):
        kwargs['hour'] = hour
        kwargs['min'] = min
        setattr(func, '_scheduler', ('at', (), kwargs))
        return func
    return d


def _deco(callback, p):
    if callback is None:
        def d(f):
            p(f)
            return f

        return d
    else:
        return p(callback)


class Scheduler(object):
    """

    The scheduler will run registered tasks at certain time or at regular interval.

    """

    def __init__(self):
        super(Scheduler, self).__init__()
        self.tasks = []
        self.r_lock = threading.RLock()
        self.log = _LOGGER

    def tick(self, callback=None, args=(), kwargs=None, **params):
        """
        Run a callable every tick (ie: each time process() is called).

        :param callback: If not provided, act as a decorator.
        :param args: args is the argument tuple for the callback invocation. Defaults to ().
        :param kwargs: kwargs is a dictionary of keyword arguments for the callback invocation. Defaults to {}.
        :param params: More optional parameters. See Task class.
        :return: Task instance
        """
        def p(f):
            with self.r_lock:
                task = TickTask(self, f, args=args, kwargs=kwargs, **params)
                self.tasks.append(task)
                return task

        return _deco(callback, p)

    def set_interval(self, interval, callback=None, start_in_sec=0, args=(), kwargs=None, **params):
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
            with self.r_lock:
                task = IntervalTask(interval, self, f, args=args, kwargs=kwargs, start_in_sec=start_in_sec, **params)
                self.tasks.append(task)
                return task

        return _deco(callback, p)

    def delay(self, delay, callback=None, args=(), kwargs=None, **params):
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
            with self.r_lock:
                task = DelayTask(delay, self, f, args=args, kwargs=kwargs, **params)
                self.tasks.append(task)
                return task

        return _deco(callback, p)

    def at(self, hour='*', min=0, callback=None, args=(), kwargs=None, **params):
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
            with self.r_lock:
                task = AtTask(self, f, hour=hour, min=min, args=args, kwargs=kwargs, **params)
                self.tasks.append(task)
                return task

        return _deco(callback, p)

    def _get(self, task_id):
        for task in self.tasks:
            if task.id == task_id:
                return task

    def bind_instance(self, instance):
        """
        Bind an instance.

        Example::

            from ething.core.scheduler import *

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

            scheduler = Scheduler()
            scheduler.bind_instance(foo)

        :param instance: an instance with some methods decorated with set_interval, at, delay or tick
        """
        for name, func in getmembers(instance, lambda x: hasattr(x, '_scheduler')):
            scheduler_func_name, args, kwargs = getattr(func, '_scheduler')
            kwargs['instance'] = instance
            try:
                getattr(self, scheduler_func_name)(*args, callback=getattr(instance, name), **kwargs)
            except:
                _LOGGER.exception('unable to create instance task')

    def unbind(self, task):
        """
        Unregister a task, callback or instance.

        :param task:
        """
        with self.r_lock:
            if isinstance(task, Task):
                if task in self.tasks:
                    self.tasks.remove(task)
            else:
                to_remove = [t for t in self.tasks if t.target == task or t.instance is task]

                for t in to_remove:
                    self.unbind(t)

    def process(self):
        now = time.time()
        to_run = []

        with self.r_lock:
            for task in self.tasks:
                if task.is_time_to_run(now):
                    to_run.append(task)

        # release the lock before running
        for task in to_run:

            task.run()

            if not task.is_valid():
                self.unbind(task)

    def clear(self):
        """
        Remove all registered tasks.
        """
        with self.r_lock:
            del self.tasks[:]

    def execute(self, task):
        task.target(*task.args, **task.kwargs)