
import threading

class StoppableThread(threading.Thread):
    """Thread class with a stop() method. The thread itself has to check
    regularly for the stopped() condition."""

    def __init__(self, **kwargs):
        super(StoppableThread, self).__init__(**kwargs)
        self._stop_evt = threading.Event()

    def stop(self, timeout=5):
        self._stop_evt.set()
        if timeout is not False:
            self.join(timeout)

    def stopped(self):
        return self._stop_evt.isSet()

