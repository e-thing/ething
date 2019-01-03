# coding: utf-8

from .Action import Action
from ...entity import *


@attr('script', type=String(), description="The Python script.")
class ExecutePyScript(Action):
    def run(self, signal, core):
        script = self.script

        eval(script, {
          'signal': signal
        })
