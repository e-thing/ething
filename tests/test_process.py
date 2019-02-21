# coding: utf-8
from ething.core.green import mode
import pytest
from ething.core.Process import Process, ThreadProcess, Manager
import time


def test_thread_process():

    counter = {
        'index': 0
    }

    def count(counter):
        counter['index'] += 1
        time.sleep(0.1)

    p = ThreadProcess(name='foobar', loop=count, args=(counter,))

    assert not p.is_running

    p.start()

    assert p.is_running

    time.sleep(1)

    p.stop()

    assert not p.is_running

    print(counter['index'])

    assert counter['index'] > 5


if mode != 'threading':
    from ething.core.Process import GreenThreadProcess

    def test_greenlet_process():

        counter = {
            'index': 0
        }

        def count(counter):
            counter['index'] += 1
            time.sleep(0.1)

        p = GreenThreadProcess(name='foobar', loop=count, args=(counter,))

        assert not p.is_running

        p.start()

        assert p.is_running

        time.sleep(1)

        p.stop()

        assert not p.is_running

        print(counter['index'])

        assert counter['index'] > 5


def test_manager():

    manager = Manager()

    def sleep(sec):
        time.sleep(sec)

    p = Process(target=sleep, args=(2, ), name='2sec')

    manager.add(p)

    assert not p.is_running

    manager.start()

    assert p.is_running

    assert len(manager.processes) == 1

    manager.add(Process(target=sleep, args=(1, ), name='1sec'))

    assert len(manager.processes) == 2

    time.sleep(3)

    assert len(manager.processes) == 1

    print(manager.processes)

