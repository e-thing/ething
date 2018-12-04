# coding: utf-8
from ething.core.green import mode
import pytest
from ething.core.Process import Process, ThreadProcess
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

        assert not p.is_active()

        p.start()

        assert p.is_active()

        time.sleep(1)

        p.stop()

        assert p.stopped()

        print(counter['index'])

        assert counter['index'] > 5
