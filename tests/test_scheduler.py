# coding: utf-8
import pytest
from ething.core.scheduler import Scheduler, tick
import time


def test_scheduler():

    g = {
        'i': 0
    }

    scheduler = Scheduler()

    def increase():
        g['i'] += 1

    scheduler.setInterval(0.5, increase, thread=False)

    tf = time.time() + 3.2
    while time.time() < tf:
        scheduler.process()
        time.sleep(0.2)

    assert g['i'] == 6

    scheduler.unbind(increase)

    tf = time.time() + 1.2
    while time.time() < tf:
        scheduler.process()
        time.sleep(0.2)

    assert g['i'] == 6


def test_class_method():

    class Foo(object):
        def __init__(self):
            self.cnt = 0

        def increase(self):
            self.cnt += 1

    foo = Foo()

    scheduler = Scheduler()

    scheduler.tick(foo.increase, thread=False)

    scheduler.process()
    scheduler.process()
    scheduler.process()

    assert foo.cnt == 3

    scheduler.unbind(foo.increase)

    scheduler.process()

    assert foo.cnt == 3


def test_class_method2():

    class Foo(object):
        def __init__(self):
            self.cnt = 0

        def increase(self):
            self.cnt += 1

    foo = Foo()

    scheduler = Scheduler()

    scheduler.tick(foo.increase, thread=False)

    scheduler.process()
    scheduler.process()
    scheduler.process()

    assert foo.cnt == 3

    scheduler.unbind(foo)

    scheduler.process()

    assert foo.cnt == 3


def test_instance():
    scheduler = Scheduler()

    class Foo(object):

        def __init__(self):
            self.i = 0

        @tick(thread=False)
        def bar(self):
            self.i += 1

    foo = Foo()

    scheduler.bind_instance(foo)

    assert foo.i == 0

    scheduler.process()
    scheduler.process()

    assert foo.i == 2

    scheduler.unbind(foo)

    scheduler.process()

    assert foo.i == 2



