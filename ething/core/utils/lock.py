# coding: utf-8

import threading
import sys


if sys.version_info >= (3, 0):
    py3 = True
else:
    py3 = False

if py3:
    Lock = threading.Lock
else:

    from threading import ThreadError, current_thread
    from Queue import Queue, Full, Empty

    class Lock(object):
        """
        Thread-safe lock mechanism with timeout support.
        """

        def __init__(self, mutex=True):
            """
            Constructor.
            Mutex parameter specifies if the lock should behave like a Mutex, and
            thus use the concept of thread ownership.
            """
            self._queue = Queue(maxsize=1)
            self._owner = None
            self._mutex = mutex

        def acquire(self, blocking=True, timeout=-1):
            """
            Acquire the lock.
            Returns True if the lock was succesfully acquired, False otherwise.

            Timeout:
            - < 0 : Wait forever.
            -   0 : No wait.
            - > 0 : Wait x seconds.
            """

            th = current_thread()
            try:
                self._queue.put(
                    th, block=blocking,
                    timeout=(None if timeout < 0 else timeout)
                )
            except Full:
                return False

            self._owner = th
            return True

        def release(self):
            """
            Release the lock.
            If the lock is configured as a Mutex, only the owner thread can release
            the lock. If another thread attempts to release the lock a
            ThreadException is raised.
            """
            th = current_thread()
            if self._mutex and th != self._owner:
                raise ThreadError('This lock isn\'t owned by this thread.')

            self._owner = None
            try:
                self._queue.get(False)
                return True
            except Empty:
                raise ThreadError('This lock was released already.')

        def __enter__(self):
            self.acquire()
            return self

        def __exit__(self, type, value, traceback):
            self.release()



class DbgLock(object):

    def __init__(self, timeout=5):
        self._lock = Lock()
        self._timeout = timeout

    def acquire(self, blocking=True, timeout=-1):
        return self._lock.acquire(blocking, timeout)

    def release(self):
        return self._lock.release()

    def __enter__(self):
        if not self.acquire(timeout = self._timeout):
            raise RuntimeError('Lock is blocked')
        return self

    def __exit__(self, type, value, traceback):
        self.release()


if __name__ == '__main__':
    import time

    l = DbgLock()

    def acquire_and_wait():
        with l:
            print('acquired')
            time.sleep(60)

    def acquire():
        with l:
            print('acquired 2')

    t1 = threading.Thread(target=acquire_and_wait)
    t1.start()

    time.sleep(1)

    t2 = threading.Thread(target=acquire)
    t2.start()

    t2.join()
