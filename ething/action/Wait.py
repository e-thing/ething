# coding: utf-8

from .Action import Action
from ething.base import attr, isInteger
import time


@attr('duration', validator=isInteger(min=1), default=1000, description="The waiting duration in milliseconds.")
class Wait(Action):
    """ Wait a certain amount of time """
    def run(self, signal):
        time.sleep(self.duration / 1000.)
