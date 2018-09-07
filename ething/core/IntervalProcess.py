# coding: utf-8

from .Process import Process
from .Scheduler import Scheduler
import time


class IntervalProcess(Process):
    def __init__(self, name, interval):
        super(IntervalProcess, self).__init__(name)
        self.scheduler = Scheduler()
        self.scheduler.setInterval(interval, self.process)

    def main(self):
        self.begin()

        while not self.stopped():
            self.scheduler.process()
            time.sleep(0.5)

        self.end()

    def begin(self):
      pass

    def process(self):
      pass

    def end(self):
      pass
