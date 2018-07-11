# coding: utf-8
import threading
import datetime


class Activities(object):

    def __init__(self, history_size = None, history_duration = None):
        self._lock = threading.Lock()
        self._items = []
        self.history_size = history_size
        self.history_duration = history_duration

    def push(self, type, **attributes):
        now  = datetime.datetime.utcnow()

        activity = {
            'type': type,
            'date': now
        }

        activity.update(attributes)

        with self._lock:
            self._update()
            self._items.insert(0, activity)

    def _update(self):
        if self.history_size and len(self._items) > self.history_size:
            self._items = self._items[:self.history_size]

        if self.history_duration:
            i=0
            now = datetime.datetime.utcnow()
            for item in reversed(self._items):
                diff = now - item['date']
                if diff.total_seconds() < self.history_duration:
                    break
                i += 1

            if i > 0:
                self._items = self._items[:len(self._items) - i]

    def list(self, types = None):
        with self._lock:
            self._update()
            if types:
                return [item for item in self._items if item['type'] in types]
            else:
                return self._items

