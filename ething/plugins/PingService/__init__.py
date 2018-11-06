# coding: utf-8

from ething.core.plugin import Plugin
from ething.core.Process import Process
from ething.core.scheduler import Scheduler
import threading
import time
import datetime


class PingPlugin(Plugin):
    def start(self):
        super(PingPlugin, self).load()
        self.service = PingService(self.core)
        self.service.start()

    def stop(self):
        super(PingPlugin, self).unload()
        if hasattr(self, 'service'):
            self.service.stop()
            del self.service


class PingService(Process):
    def __init__(self, core):
        super(PingService, self).__init__('ping_service')
        self.core = core
        self.scheduler = Scheduler()
        self.scheduler.setInterval(60, self._ping_all)

    def main(self):
        while not self.stopped():
            self.scheduler.process()
            time.sleep(0.5)

    def _ping_all(self):
        """
        ping all devices to see if there are still connected !
        """

        devices = self.core.find(lambda r: r.isTypeof("resources/Device") and hasattr(r, 'ping_host'))

        for device in devices:
            if (device.lastSeenDate is None) or (
                device.lastSeenDate < datetime.datetime.utcnow() - datetime.timedelta(seconds=45)):
                threading.Thread(target=self._ping, args=(device,), name="ping").start()

    def _ping(self, device):
        try:
            connected = device.ping_host(timeout=5)
        except:
            self.log.exception('unable to ping device %s' % device)
        else:
            self.log.debug('ping device %s : %s' % (device, 'connected' if connected else 'not connected'))
