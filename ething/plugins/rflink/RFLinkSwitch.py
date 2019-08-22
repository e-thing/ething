# coding: utf-8


from .RFLinkNode import RFLinkNode
from ething.interfaces import Relay
from ething.reg import *


@attr('switchId', type=Nullable(String(allow_empty=False)), mode = READ_ONLY, default='0', description="The switch id of the node. Only available for switch/door/motion subtypes.")
class RFLinkSwitch(RFLinkNode, Relay):

    def setState(self, state):
        self._send(CMD = 'ON' if state else 'OFF', SWITCH = self.switchId)
        self.state = state


    def _handle_incoming_data(self, protocol, data):
        super(RFLinkSwitch, self)._handle_incoming_data(protocol, data)

        if 'CMD' in data:
            self.state = bool(data['CMD']=='ON')

