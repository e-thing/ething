# coding: utf-8

from .ShortId import ShortId
from .Process import Process
import time
import datetime
import logging

import threading
from .utils.weak_ref import weak_ref


class Task(object):

    def __init__(self, target, args=(), kwargs=None, name = None, thread = False):

        if not callable(target):
            raise Exception('target must be callable')

        self._id = ShortId.generate()
        self._target = weak_ref(target)
        self._args = args
        self._kwargs = kwargs or {}
        self._name = name or target.__name__
        self._thread = thread

        self._last_run = None
        self._executed_count = 0
        self._log = logging.getLogger('ething.Scheduler.%s' % self._name)
        self._valid = True
        self._t0 = time.time()

    @property
    def id(self):
        return self._id

    @property
    def executed_count(self):
        return self._executed_count

    def run(self):
        target = self._target()
        if target is not None:

            self._last_run = time.time()
            self._executed_count += 1

            if self._thread:
                p = Process(self._name, target=target, args=self._args, kwargs=self._kwargs)
                p.start()
            else:
                try:
                    target(*self._args, **self._kwargs)
                except:
                    self._log.exception('exception in task')

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
    def __init__(self, interval, *args, start_in_sec=0, **kwargs):
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
        super(DelayTask, self).run(self)
        self._valid = False # run only one time


class AtTask(Task):
    def __init__(self, *args, hour='*', min=0, **kwargs):
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
            self._next = self._compute_next_time(self._t0)
            return True


class Scheduler(object):

    def __init__(self):
        self.log = logging.getLogger('ething.Scheduler')
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

    def unbind(self, task):
        with self.r_lock:
            if task in self.tasks:
                self.tasks.remove(task)

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


