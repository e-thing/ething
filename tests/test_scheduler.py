# coding: utf-8
import pytest
from ething.scheduler import set_interval, tick, unbind, Scheduler, bind_instance
import time


def test_scheduler():

    g = {
        'i': 0
    }

    scheduler = Scheduler()

    def increase():
        g['i'] += 1

    set_interval(0.5, increase, scheduler=scheduler)

    tf = time.time() + 3.2
    while time.time() < tf:
        scheduler.process()
        time.sleep(0.2)

    assert g['i'] == 6

    unbind(increase, scheduler=scheduler)

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

    tick(foo.increase, scheduler=scheduler)

    scheduler.process()
    scheduler.process()
    scheduler.process()

    assert foo.cnt == 3

    unbind(foo.increase, scheduler=scheduler)

    scheduler.process()

    assert foo.cnt == 3


def test_instance():
    scheduler = Scheduler()

    class Foo(object):

        def __init__(self):
            self.i = 0

        @tick(scheduler=scheduler)
        def bar(self):
            self.i += 1

    foo = Foo()

    bind_instance(foo)

    assert foo.i == 0

    scheduler.process()
    scheduler.process()

    assert foo.i == 2

    unbind(foo, scheduler=scheduler)

    scheduler.process()

    assert foo.i == 2


def test_instance_delete():
    scheduler = Scheduler()

    ctx = {
        'i': 0
    }

    class Foo(object):

        def __init__(self, ctx):
            self.ctx = ctx

        def bar(self):
            self.ctx['i'] += 1

    foo = Foo(ctx)

    tick(foo.bar, scheduler=scheduler)

    assert ctx['i'] == 0

    scheduler.process()
    scheduler.process()

    assert ctx['i'] == 2

    del foo

    scheduler.process()

    assert ctx['i'] == 2


def test_decorator():
    scheduler = Scheduler()

    ctx = {
        'i': 0
    }

    @tick(scheduler=scheduler)
    def bar():
        ctx['i'] += 1

    assert ctx['i'] == 0

    scheduler.process()
    scheduler.process()

    assert ctx['i'] == 2



