# coding: utf-8
from .. import *


@meta(icon='mdi-function', category="function")
@attr('script', type=Text(lang='python'),
      description="The Python script. The message is accessible using the variable 'msg', get the message's payload by 'msg['payload']'. Call the function 'emit({\"payload\":...})' to emit a message from this node. The core instance is available through 'core'.")
class Function(Node):
    """Execute a python script"""

    INPUTS = ['default']
    OUTPUTS = ['default']

    def main(self, **inputs):
        msg = inputs['default']
        context = self.flow.context

        try:
            formatted = []
            for line in self.script.splitlines():
                formatted.append('  ' + line)

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
            resource = None
            if 'resource' in msg:
                resource = self.core.get(msg['resource'])

            exec(formatted, {
                'msg': msg,
                'logger': self.logger,
                'core': self.core,
                'debug': self.debug,
                'emit': self.emit,
                'context': context,
                'resource': resource,
            })

        except Exception as e:
            raise e
