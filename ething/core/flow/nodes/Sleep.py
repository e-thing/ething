# coding: utf-8
from .. import *


@meta(icon='mdi-clock')
@attr('duration', type=Integer(min=1), default=1000, description="The waiting duration in milliseconds.")
class Sleep(Node):
    """ Wait a certain amount of time """

    INPUTS = ['default']
    OUTPUTS = ['default']

    def main(self, **inputs):
        time.sleep(self.duration / 1000.)
        self.emit(inputs.get('default'))
