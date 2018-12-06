# coding: utf-8

from ..green import get_current
import threading
import sys


if sys.version_info >= (3, 0):
    py3 = True
else:
    py3 = False

if py3:
    _Lock = threading.Lock
    _RLock = threading.RLock
else:

    from Queue import Queue, Full, Empty

    class _Lock(object):
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

            th = threading.current_thread()
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
            th = threading.current_thread()
            if self._mutex and th != self._owner:
                raise threading.ThreadError('This lock isn\'t owned by this thread.')

            self._owner = None
            try:
                self._queue.get(False)
                return True
            except Empty:
                raise threading.ThreadError('This lock was released already.')

        def __enter__(self):
            self.acquire()
            return self

        def __exit__(self, type, value, traceback):
            self.release()


    class _RLock(object):

        def __init__(self):
            self._lock = threading.RLock()

        def acquire(self, blocking=True, timeout=-1):
            return self._lock.acquire(blocking)

        def release(self):
            return self._lock.release()

        def __enter__(self):
            self.acquire()
            return self

        def __exit__(self, type, value, traceback):
            self.release()


class SecureLockBase(object):

    def __init__(self, lock_cls, timeout=30):
        self._lock = lock_cls()
        self._timeout = timeout
        self._owner = None

    def acquire(self, blocking=True, timeout=-1):
        res = self._lock.acquire(blocking, timeout)
        if res:
            self._owner = get_current()
        return res

    def release(self):
        return self._lock.release()

    def __enter__(self):
        if not self.acquire(timeout = self._timeout):
            raise RuntimeError('Lock is blocked by %s' % self._owner)
        return self

    def __exit__(self, type, value, traceback):
        self.release()


class SecureLock(SecureLockBase):
    def __init__(self, timeout=30):
        super(SecureLock, self).__init__(_Lock, timeout)


class SecureRLock(SecureLockBase):
    def __init__(self, timeout=30):
        super(SecureRLock, self).__init__(_RLock, timeout)


if __name__ == '__main__':
    from gevent import monkey, spawn, joinall

    monkey.patch_all()
    import time

    l = SecureLock(3)

    def acquire_and_wait():
        with l:
            print('acquired')
            time.sleep(60)

    def acquire():
        with l:
            print('acquired 2')


    t1 = spawn(acquire_and_wait)
    time.sleep(1)
    t2 = spawn(acquire)

    joinall([t1, t2])


    #t1 = threading.Thread(target=acquire_and_wait)
    #t1.start()
#
    #time.sleep(1)
#
    #t2 = threading.Thread(target=acquire)
    #t2.start()
#
    #t2.join()
