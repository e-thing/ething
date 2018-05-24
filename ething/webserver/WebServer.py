# coding: utf-8
import os
import signal

is_thread = os.name == "nt"

if is_thread:
    from threading import Thread
else:
    from multiprocessing import Process


class WebServer(object):

    def __init__(self, core):

        self.core = core
        self.p = None

    @property
    def is_started(self):
        return self.p is not None and self.p.is_alive()

    def __proc(self):

        # remove any signal handlers set by the parents
        if not is_thread:
            signal.signal(signal.SIGINT, signal.SIG_IGN)
            signal.signal(signal.SIGTERM, signal.SIG_DFL)

        self.core.log.info("webserver process started, pid = %d" % os.getpid())

        self.core._init_database()

        try:
            from ething.webserver.server import run

            run(self.core)
        except:
            self.core.log.exception("webserver stopped")

        self.core.log.info("webserver process ended")

    def start(self):
        if self.is_started:
            raise Exception('the webserver is already running !')

        # run webserver in another process
        if is_thread:
            self.p = Thread(target=self.__proc, args=())
        else:
            self.p = Process(target=self.__proc, args=())

        self.p.daemon = True
        self.p.start()

    def stop(self):
        if self.is_started:
            if not is_thread:
                self.core.log.info("stopping webserver")
                self.p.terminate()
                self.p.join()
                self.core.log.info("webserver stopped")
                self.p = None
