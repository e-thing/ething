# coding: utf-8

from . import Signal, Event


__all__ = ["DaemonStarted", "DaemonStartedEvent"]


class DaemonStarted(Signal):
    pass


class DaemonStartedEvent(Event):
    signal = DaemonStarted
