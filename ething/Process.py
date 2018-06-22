# coding: utf-8

from ething.utils.StoppableThread import StoppableThread
import logging


class Process(StoppableThread):

    def __init__(self, name, *args, **kwargs):
        super(Process, self).__init__(name = name, *args, **kwargs)
        self.daemon = True
        self.log = logging.getLogger("ething.%s" % name)

    def run(self):
        self.log.info('Start process "%s"' % self.name)

        try:
            self.main()
        except Exception:
            self.log.exception('Exception in process "%s"' % self.name)

        self.log.info('Stop process "%s"' % self.name)

    def main(self):
        pass