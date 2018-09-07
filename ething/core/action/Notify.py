# coding: utf-8

from .Action import Action
from ..reg import *


@attr('message', type=String(), description="The message of the notification")
@attr('subject', type=String(), default='', description="The subject of the notification")
class Notify(Action):
    """ Send a notification """
    def run(self, signal):
        self.ething.notify(subject = self.subject, message = self.message)

