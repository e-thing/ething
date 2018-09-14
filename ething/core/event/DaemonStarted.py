# coding: utf-8

from .Signal import Signal
from .Event import Event


__all__ = ["DaemonStarted", "DaemonStartedEvent"]


class DaemonStarted(Signal):
    pass


class DaemonStartedEvent(Event):
    signal = DaemonStarted
