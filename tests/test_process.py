# coding: utf-8
from ething.core.green import mode
import pytest
from ething.core.Process import Process, Manager
import time


def test_process():
    manager = Manager()

    counter = {
        'index': 0
    }

    def count(counter):
        counter['index'] += 1
        time.sleep(0.1)

    p = Process(name='foobar', loop=count, args=(counter,), manager=manager)

    assert not p.is_running

    p.start()

    assert p.is_running

    time.sleep(1)

    p.stop()

    assert not p.is_running

    print(counter['index'])

    assert counter['index'] > 5


def test_manager():

    manager = Manager(start=False)

    def sleep(sec):
        time.sleep(sec)

    p = Process(target=sleep, args=(2, ), name='2sec')

    manager.attach(p)

    assert not p.is_running

    manager.start()

    assert p.is_running

    assert len(manager.processes) == 1

    manager.attach(Process(target=sleep, args=(1, ), name='1sec'))

    assert len(manager.processes) == 2

    p.wait()

    assert len(manager.processes) == 1

    print(manager.processes)

