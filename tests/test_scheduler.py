# coding: utf-8
import pytest
from ething.core.scheduler import Scheduler, setInterval
import time


def test_taskmanager():

    g = {
        'i': 0
    }

    scheduler = Scheduler()

    def increase():
        g['i'] += 1

    scheduler.setInterval(0.5, increase)

    tf = time.time() + 3.2
    while time.time() < tf:
        scheduler.process()
        time.sleep(0.2)

    assert g['i'] == 6


def test_instance():
    scheduler = Scheduler()

    class Foo(object):

        def __init__(self):
            self.i = 0

        @setInterval(0.5)
        def bar(self):
            self.i += 1

    foo = Foo()

    scheduler.bind_instance(foo)

    assert foo.i == 0

    tf = time.time() + 1.2
    while time.time() < tf:
        scheduler.process()
        time.sleep(0.2)

    assert foo.i == 2

    scheduler.unbind(foo)

    tf = time.time() + 1.2
    while time.time() < tf:
        scheduler.process()
        time.sleep(0.2)

    assert foo.i == 2



