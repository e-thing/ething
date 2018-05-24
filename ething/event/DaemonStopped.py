# coding: utf-8

from .Signal import Signal
from .Event import Event


class DaemonStopped(Signal):
    pass


class DaemonStoppedEvent(Event):
    signal = DaemonStopped
