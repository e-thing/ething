# coding: utf-8
import eventlet
eventlet.monkey_patch()
import pytest
from ething.core.Process import Process, ThreadProcess, GreenThreadProcess
import time


def test_thread_process():

    counter = {
        'index': 0
    }

    def count(counter):
        counter['index'] += 1
        time.sleep(0.1)

    p = ThreadProcess(name='foobar', loop=count, args=(counter,))

    assert not p.is_active()

    p.start()

    assert p.is_active()

    time.sleep(1)

    p.stop()

    assert p.stopped()

    print(counter['index'])

    assert counter['index'] > 5


def test_greenlet_process():

    counter = {
        'index': 0
    }

    def count(counter):
        counter['index'] += 1
        time.sleep(0.1)

    p = GreenThreadProcess(name='foobar', loop=count, args=(counter,))

    assert not p.is_active()

    p.start()

    assert p.is_active()

    time.sleep(1)

    p.stop()

    assert p.stopped()

    print(counter['index'])

    assert counter['index'] > 5
