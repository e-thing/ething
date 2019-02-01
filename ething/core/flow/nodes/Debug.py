# coding: utf-8
from .. import *


@meta(icon='mdi-android-debug-bridge', category="output")
@attr('print_log', label='print to log', type=Boolean(), default=False, description='print the debug information in the log')
@attr('print_debug_window', label='print to debug window', type=Boolean(), default=True, description='print the debug information in the debug window')
@attr('output', type=Descriptor(('fullmsg', 'msg')), default={'type':'msg','value':'payload'}, description='Select the message property to display.')
class DebugNode(Node):
    """
    print some debug information
    """

    INPUTS = ['default']

    def main(self, **inputs):
        _msg = inputs.get('default')
        _data = self.output.get(msg=_msg, flow=self.flow)
        if self.print_debug_window:
            self.debug(_data)
        if self.print_log:
            self.log.info(str(_data))
