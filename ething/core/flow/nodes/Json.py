# coding: utf-8
from .. import *
import json


@meta(icon='mdi-json')
class JSON(Node):
    """convert to/from JSON"""

    INPUTS = ['default']
    OUTPUTS = ['default']

    def main(self, **inputs):
        data = inputs['default'].get('payload')

        if isinstance(data, string_types):
            self.emit({'payload': json.loads(data)})
        else:
            self.emit({'payload': json.dumps(data)})
