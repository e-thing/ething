# coding: utf-8

from .Action import Action
from ething.base import attr, isString


@attr('message', validator=isString(), description="The message of the notification")
@attr('subject', validator=isString(), default='', description="The subject of the notification")
class Notify(Action):
    """ Send a notification """
    def run(self, signal):
        self.ething.notify(subject = self.subject, message = self.message)
