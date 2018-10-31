# coding: utf-8

from .utils.StoppableThread import StoppableThread
import logging
import threading

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


class Process(StoppableThread):

    def __init__(self, name, **kwargs):

        super(Process, self).__init__(name = name, **kwargs)

        self.daemon = True
        self.log = logging.getLogger("ething.%s" % name)

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
        # run any target
        super(Process, self).run()

    def setup(self):
        pass

    def end(self):
        pass