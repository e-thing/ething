# coding: utf-8

from .Signal import Signal
from .Event import Event


class Notified(Signal):
    def __init__(self, message, subject = None):
        super(Notified, self).__init__()
        self.message = message
        self.subject = subject

class NotifiedEvent(Event):
    signal = Notified
