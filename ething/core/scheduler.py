# coding: utf-8

from .ShortId import ShortId
from .Process import Process, BaseProcess
import inspect
import time
import datetime
import logging

import threading
from .utils.weak_ref import weak_ref


_LOGGER = logging.getLogger('ething.scheduler')

class Task(object):

    def __init__(self, target, args=(), kwargs=None, name=None, thread=True, instance=None, condition=None, allow_multiple=False):

        if not callable(target):
            raise Exception('target must be callable')

        self._id = ShortId.generate()
        self._target = weak_ref(target)
        if instance is None and getattr(target, '__self__', None) is not None:
            instance = target.__self__
        self._args = args
        self._kwargs = kwargs or {}
        self._name = name
        if not self._name:
            if instance is not None:
                self._name = "%s.%s" % (type(instance).__name__, target.__name__)
            else:
                self._name = target.__name__
        self._thread = thread
        self._instance = weak_ref(instance) if instance is not None else None
        self._condition = condition
        self._allow_multiple = allow_multiple

        self._last_run = None
        self._executed_count = 0
        self._valid = True
        self._t0 = time.time()

        self._p = None # last process ran

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
        return self._target()

    @property
    def instance(self):
        return self._instance() if self._instance is not None else None

    def run(self):
        target = self._target()
        if target is not None:

            self._last_run = time.time()
            self._executed_count += 1

            if self._condition is not None:
                try:
                    if not self._condition(self):
                        return False
                except:
                    return False

            if self._thread:

                if self._p and not self._p.stopped() and not self._allow_multiple:
                    _LOGGER.debug('task "%s" already running: skipped' % self._name)
                    return

                processCls = self._thread if inspect.isclass(self._thread) else Process
                self._p = processCls(name=self._name, target=target, args=self._args, kwargs=self._kwargs)
                self._p.start()
            else:
                try:
                    target(*self._args, **self._kwargs)
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


def setInterval(interval, start_in_sec=0, **kwargs):
    def d(func):
        kwargs['start_in_sec'] = start_in_sec
        setattr(func, '_scheduler', ('setInterval', (interval,), kwargs))
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


class Scheduler(object):

    def __init__(self):
        super(Scheduler, self).__init__()
        self.tasks = []
        self.r_lock = threading.RLock()

    def tick(self, callback, args=(), kwargs=None, **params):
        with self.r_lock:
            task = TickTask(callback, args=args, kwargs=kwargs, **params)
            self.tasks.append(task)
            return task

    def setInterval(self, interval, callback, start_in_sec=0, args=(), kwargs=None, **params):
        with self.r_lock:
            task = IntervalTask(interval, callback, args=args, kwargs=kwargs, start_in_sec=start_in_sec, **params)
            self.tasks.append(task)
            return task

    def delay(self, delay, callback, args=(), kwargs=None, **params):
        with self.r_lock:
            task = DelayTask(delay, callback, args=args, kwargs=kwargs, **params)
            self.tasks.append(task)
            return task

    def at(self, callback, hour='*', min=0, args=(), kwargs=None, **params):
        with self.r_lock:
            task = AtTask(callback, hour=hour, min=min, args=args, kwargs=kwargs, **params)
            self.tasks.append(task)
            return task

    def _get(self, task_id):
        for task in self.tasks:
            if task.id == task_id:
                return task

    def bind_instance(self, instance):
        for name, func in inspect.getmembers(instance, inspect.ismethod):
            if hasattr(func, '_scheduler'):
                scheduler_func_name, args, kwargs = getattr(func, '_scheduler')
                kwargs['instance'] = instance
                try:
                    getattr(self, scheduler_func_name)(*args, callback=getattr(instance, name), **kwargs)
                except:
                    _LOGGER.exception('unable to create instance task')

    def unbind(self, task):
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
        with self.r_lock:
            self.tasks.clear()
