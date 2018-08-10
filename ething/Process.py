# coding: utf-8

from ething.utils.StoppableThread import StoppableThread
import logging
import threading

processes_map_lock = threading.Lock()

processes_map = {}

def add_process(process):
    with processes_map_lock:
        if process.name not in processes_map:
            processes_map[process.name] = set()

        processes_map[process.name].add(process)

def remove_process(process):
    with processes_map_lock:
        processes_map[process.name].discard(process)

def get_process(name):
    with processes_map_lock:
        if name in processes_map and len(processes_map[name]) > 0:
            return processes_map[name][0]

def get_processes(name):
    with processes_map_lock:
        return list(processes_map.get(name, set()))


class Process(StoppableThread):

    def __init__(self, name, *args, **kwargs):
        super(Process, self).__init__(name = name, *args, **kwargs)
        self.daemon = True
        self.log = logging.getLogger("ething.%s" % name)

        add_process(self)

    def run(self):
        self.log.info('Start process "%s"' % self.name)

        try:
            self.main()
        except Exception:
            self.log.exception('Exception in process "%s"' % self.name)

        remove_process(self)

        self.log.info('Process "%s" stopped' % self.name)

    def main(self):
        pass