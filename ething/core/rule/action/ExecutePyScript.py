# coding: utf-8

from .Action import Action
from ...entity import *


class PythonScript(String):
    def __init__(self, **attributes):
        super(PythonScript, self).__init__(**attributes)

    def toSchema(self, context = None):
        schema = super(PythonScript, self).toSchema(context)
        schema['format'] = 'text/x-python'
        return schema


@meta(label='Execute Script')
@attr('script', type=PythonScript(), description="The Python script.")
class ExecutePyScript(Action):
    def run(self, signal, core):
        script = self.script

        eval(script, {
          'signal': signal,
          'logger': self.log,
          'ething': core,
          'debug': self._context.get('debugger', self._debug)
        })

    def _debug(self, obj):
        self.log.debug(obj)