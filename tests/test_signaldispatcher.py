# coding: utf-8
import pytest
from ething.core.SignalDispatcher import SignalDispatcher
from ething.core.Signal import Signal


class Foo(Signal):
    pass


def test_signaldispatcher():
    signaldispatcher = SignalDispatcher()

    cnt = 0

    def inc():
        global cnt
        cnt += 1

    foo = Foo()

    signaldispatcher.bind('Foo', inc)

    signaldispatcher.dispatch(foo)
    signaldispatcher.dispatch(foo)

    assert cnt == 2

    signaldispatcher.bind('*', inc)

    signaldispatcher.dispatch(foo)

    assert cnt == 4

    signaldispatcher.unbind('*', inc)

    signaldispatcher.dispatch(foo)

    assert cnt == 4


def test_signaldispatcher_once():
    signaldispatcher = SignalDispatcher()

    cnt = 0

    def inc():
        global cnt
        cnt += 1

    foo = Foo()

    signaldispatcher.bind('Foo', inc, once=True)

    signaldispatcher.dispatch(foo)

    assert cnt == 1

    signaldispatcher.dispatch(foo)

    assert cnt == 1
