# coding: utf-8
from .. import *



@meta(icon='mdi-function', category="function")
@attr('script', type=Text(lang='python'), description="The Python script.")
class Function(Node):
    """Execute a python script"""

    INPUTS = ['default']
    OUTPUTS = ['default']

    def main(self, **inputs):
        msg = inputs['default']
        context = self.flow.context

        try:
            formatted = []
            for l in self.script.splitlines():
                formatted.append('  ' + l)

            formatted = '\n'.join(formatted)

            formatted = """
import collections

def __main():
""" + formatted + """

res = __main()
if res is not None:
  if isinstance(res, collections.abc.Sequence):
    for r in res:
      emit(r)
  else:
    emit(res)

"""
            exec(formatted, {
                'msg': msg,
                'logger': self.logger,
                'core': self.core,
                'debug': self.debug,
                'emit': self.emit,
                'context': context
            })

        except Exception as e:
            raise e
            pass
