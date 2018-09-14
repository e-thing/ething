# coding: utf-8

from .Signal import Signal
from .Event import Event


__all__ = ["DaemonStopped", "DaemonStoppedEvent"]


class DaemonStopped(Signal):
    pass


class DaemonStoppedEvent(Event):
    signal = DaemonStopped
