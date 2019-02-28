# coding: utf-8

from ..green import get_current, mode
import threading
import sys
#import logging
#import time


#_LOGGER = logging.getLogger('ething.lock')

if sys.version_info >= (3, 0):
    py3 = True
else:
    py3 = False

if py3 and False:
    _Lock = threading.Lock
    _RLock = threading.RLock
else:
    from queue import Queue, Full, Empty

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

        def __exit__(self, type, value, traceback):
            self.release()


class SecureLockBase(object):

    def __init__(self, lock_cls, timeout=30, name='anonym'):
        self._lock = lock_cls()
        self._timeout = timeout
        self._owner = None
        self._name = name
        #self._t1 = None

    def acquire(self, blocking=True, timeout=-1):
        c = get_current()
        #t0 = time.time()
        #_LOGGER.debug('[lock] %s wait acquire by %s' % (self._name, c))
        res = self._lock.acquire(blocking, timeout)
        if res:
            #self._t1 = time.time()
            #_LOGGER.debug('[lock] %s acquired after %f sec by %s' % (self._name, self._t1 - t0, c))
            self._owner = c
        #else:
            #_LOGGER.debug('[lock] %s not acquired by %s' % (self._name, c))
        return res

    def release(self):
        #_LOGGER.debug('[lock] %s release after %f sec by %s' % (self._name, time.time() - self._t1, get_current()))
        return self._lock.release()

    def __enter__(self):
        if not self.acquire(True, self._timeout):
            # print stack trace
            if mode == 'gevent':
                from gevent.util import print_run_info
                print_run_info()
            raise RuntimeError('Lock %s is blocked by %s' % (self._name, self._owner))

    def __exit__(self, type, value, traceback):
        self.release()


class SecureLock(SecureLockBase):
    def __init__(self, *args, **kwargs):
        super(SecureLock, self).__init__(_Lock, *args, **kwargs)


class SecureRLock(SecureLockBase):
    def __init__(self, *args, **kwargs):
        super(SecureRLock, self).__init__(_RLock, *args, **kwargs)


if __name__ == '__main__':
    from gevent import monkey, spawn, joinall, get_hub, lock
    import gevent

    monkey.patch_all()
    import time

    h = get_hub()
    print(h)

    time.sleep(5)

    l = SecureLock(30)

    def acquire_and_wait():
        print('<acquire_and_wait')
        #spawn(get_hub().threadpool.apply, sleep, (5,))
        with l:
            print('acquired')
            time.sleep(5)
        print('release')
        print('acquire_and_wait>')

    def acquire():
        print('<acquire')
        print('try acq')
        with l:
            print('acquired 2')
        print('acquire>')

    def acthre():
        t2 = spawn(sleep)
        t1 = spawn(acquire)
        joinall([t1, t2])

    def sleep(d=30):
        print('<sleep')
        gevent.sleep(d)
        print('sleep>')

    t1 = spawn(acquire_and_wait)
    gevent.sleep(0.5)
    t2 = spawn(sleep, 5)
    gevent.sleep(0.5)
    spawn(h.threadpool.apply(acthre))

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
