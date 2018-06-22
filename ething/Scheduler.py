# coding: utf-8

import time
import datetime
import logging

import threading
from ething.utils.weak_ref import weak_ref

class Scheduler(object):

    def __init__(self, **kwargs):
        self.log = logging.getLogger('ething.Scheduler')
        super(Scheduler, self).__init__(**kwargs)
        self.tasks = []
        self.r_lock = threading.RLock()

    def tick(self, callback, args=(), kwargs=None):
        with self.r_lock:
            if kwargs is None:
                kwargs = {}
            if callable(callback):
                self.tasks.append({
                    'type': 'tick',
                    'callback': weak_ref(callback),
                    'args': args,
                    'kwargs': kwargs,
                })
                return True

        return False

    def setInterval(self, interval, callback, startInSec=0, args=(), kwargs=None):
        with self.r_lock:
            if kwargs is None:
                kwargs = {}
            if callable(callback) and interval > 0:
                self.tasks.append({
                    'type': 'interval',
                    'interval': interval,
                    'callback': weak_ref(callback),
                    'startIn': startInSec,
                    't0': time.time(),
                    'running': False,
                    'args': args,
                    'kwargs': kwargs,
                })
                return True

        return False

    def delay(self, delay, callback, args=(), kwargs=None):
        with self.r_lock:
            if kwargs is None:
                kwargs = {}
            if callable(callback) and delay > 0:
                self.tasks.append({
                    'type': 'delay',
                    'delay': delay,
                    'callback': weak_ref(callback),
                    't0': time.time(),
                    'args': args,
                    'kwargs': kwargs,
                })
                return True

        return False

    def at(self, callback, hour='*', min=0, args=(), kwargs=None):
        with self.r_lock:
            if kwargs is None:
                kwargs = {}
            if callable(callback):
                self.tasks.append({
                    'type': 'at',
                    'hour': hour,
                    'min': min,
                    'callback': weak_ref(callback),
                    't0': time.time(),
                    'args': args,
                    'kwargs': kwargs,
                })
                return True

        return False

    def _run(self, task):
        callback = task['callback']()
        if callback is not None:
            task['lastRun'] = time.time()
            if 'executedCount' not in task:
                task['executedCount'] = 0
            task['executedCount'] += 1
            try:
                callback(*task['args'], **task['kwargs'])
            except:
                self.log.exception(
                    '[scheduler] exception in task "%s"' % task['callback'].__name__)
            return True
        else: # lost reference
            pass

    def process(self):
        with self.r_lock:
            i = 0
            while i < len(self.tasks):
                task = self.tasks[i]
                remove = False
                now = time.time()
                type = task['type']

                if type == 'tick':
                    remove = not self._run(task)

                elif type == 'interval':
                    if task['running']:
                        if (now - task['lastRun']) >= task['interval']:
                            remove = not self._run(task)

                    else:
                        if (now - task['t0']) >= task['startIn']:
                            task['running'] = True
                            remove = not self._run(task)

                elif type == 'delay':

                    if (now - task['t0']) >= task['delay']:
                        self._run(task)
                        remove = True

                elif type == 'at':

                    nowd = datetime.datetime.utcnow()

                    if nowd.second < 5 and (task['hour'] == '*' or task['hour'] == nowd.hour) and (task['min'] == '*' or task['min'] == nowd.minute) and (('lastRun' not in task) or (now - task['lastRun']) >= 55):
                        remove = not self._run(task)

                if remove:
                    self.tasks.remove(task)
                    i -= 1

                i += 1
