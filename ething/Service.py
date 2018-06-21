
from .StoppableThread import StoppableThread
import logging

class Service(StoppableThread):

    def __init__(self, name, *args, **kwargs):
        super(Service, self).__init__(name = name, *args, **kwargs)
        self.daemon = True
        self.log = logging.getLogger(name)


    def run(self):
        self.log.info('Start service %s' % self.name)

        try:
            self.main()
        except Exception:
            self.log.exception('Exception in service %s' % self.name)

        self.log.info('Stop service %s' % self.name)

    def main(self):
        pass