# coding: utf-8

from . import Signal, Event
from ...reg import meta


__all__ = ["Notified", "NotifiedEvent"]


class Notified(Signal):
    def __init__(self, message, subject = None):
        super(Notified, self).__init__()
        self.message = message
        self.subject = subject


@meta(label='Notified', icon='mdi-send')
class NotifiedEvent(Event):
    """
    is emitted when a notification has been sent
    """
    signal = Notified
