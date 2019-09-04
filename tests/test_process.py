# coding: utf-8
import pytest
from ething.processes import Process, ProcessCollection, process, processes
import time


def test_process_start_stop():

    counter = {
        'index': 0
    }

    def count(counter):
        while True:
            counter['index'] += 1
            time.sleep(0.1)

    p = Process(count, args=(counter,))

    assert not p.is_running

    p.start()

    assert p.is_running

    time.sleep(0.5)

    p.stop()

    _count = counter['index']

    assert not p.is_running

    time.sleep(0.3)

    assert _count == counter['index']

    p.restart()

    assert p.is_running

    time.sleep(0.5)

    assert _count < counter['index']

    p.stop()

    assert not p.is_running


def test_process_wait():

    def sleep(sec):
        time.sleep(sec)

    p = Process(sleep, args=(2, ))
    p.start()
    p.join(timeout=3)

    assert not p.is_running


def test_process_collection():

    class T(object):
        pass

    parent = T()

    col = ProcessCollection(parent=parent)

    def sleep(sec):
        time.sleep(sec)

    p = col.add(sleep, args=(2, ), id='2sec')

    assert p.is_running
    assert p.parent is parent

    assert '2sec' in col
    assert p.id in col
    assert p in col
    assert len(col) == 1
    assert col['2sec'] is p

    del col['2sec']

    assert not p.is_running


def test_process_decorator():
    counter = {
        'index': 0
    }

    @process(id='foobar')
    def count():
        while True:
            counter['index'] += 1
            time.sleep(0.1)

    p = processes['foobar']

    assert p
    assert p.is_running

    time.sleep(0.5)

    assert counter['index'] > 3

    del processes['foobar']

    assert not p.is_running
