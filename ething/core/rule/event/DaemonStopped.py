# coding: utf-8

from . import Signal, Event


__all__ = ["DaemonStopped", "DaemonStoppedEvent"]


class DaemonStopped(Signal):
    pass


class DaemonStoppedEvent(Event):
    signal = DaemonStopped
