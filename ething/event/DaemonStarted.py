# coding: utf-8

from .Signal import Signal
from .Event import Event


class DaemonStarted(Signal):
    pass


class DaemonStartedEvent(Event):
    signal = DaemonStarted
