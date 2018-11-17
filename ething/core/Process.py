# coding: utf-8

from .utils.StoppableThread import StoppableThread
import logging
import threading
import time

processes_map_lock = threading.Lock()

processes_map = {}

def add_process(process):
    with processes_map_lock:
        if process.name not in processes_map:
            processes_map[process.name] = []
        processes_map[process.name].append(process)

def remove_process(process):
    with processes_map_lock:
        processes_map[process.name].remove(process)

def get_process(name):
    with processes_map_lock:
        if name in processes_map and len(processes_map[name]) > 0:
            return processes_map[name][0]

def get_processes(name):
    with processes_map_lock:
        return processes_map.get(name, [])

def list_processes():
    processes = []
    with processes_map_lock:
        for n in processes_map:
            processes += processes_map[n]
    return processes


class Process(StoppableThread):

    def __init__(self, name, **kwargs):

        self._loop = kwargs.pop('loop', None)

        super(Process, self).__init__(name = name, **kwargs)

        self.daemon = True
        self.log = logging.getLogger("ething.%s" % name)
        self.start_ts = time.time()

        add_process(self)

    def run(self):
        self.log.info('Process "%s" started' % self.name)

        self.setup()

        try:
            self.main()
        except Exception:
            self.log.exception('Exception in process "%s"' % self.name)

        self.end()

        remove_process(self)

        self.log.info('Process "%s" stopped' % self.name)

    def main(self):
        if self._loop is not None:
            try:
                while not self.stopped():
                    if self._loop(*self._args, **self._kwargs) is False:
                        self.stop(timeout=False)
                        break
            finally:
                # Avoid a refcycle if the thread is running a function with
                # an argument that has a member that points to the thread.
                del self._loop, self._args, self._kwargs
        else:
            # run any target
            super(Process, self).run()

    def setup(self):
        pass

    def end(self):
        pass

    def toJson(self):
        return {
            'name': self.name,
            'active': self.is_alive() and not self.stopped(),
            'start_ts': int(self.start_ts)
        }