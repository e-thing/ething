# coding: utf-8

from ething.plugin import Plugin
from ething.Process import Process


class WebServer(Plugin):

    def load(self):
        self.process = WebServerProcess(self.core)
        self.process.start()

    def unload(self):
        if self.process:
            self.process.stop()


class WebServerProcess(Process):

    def __init__(self, core):
        super(WebServerProcess, self).__init__('webserver')
        self.core = core

    def main(self):

        from ething.webserver.server import run

        run(self.core)

