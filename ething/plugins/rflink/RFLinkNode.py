# coding: utf-8

from ething.core.Device import Device
from ething.core.reg import *
from .helpers import *


@attr('nodeId', type=String(allow_empty=False), mode = READ_ONLY, description="The hardware id of the node.")
@attr('protocol', type=String(allow_empty=False), mode = READ_ONLY, description="The protocol name of the node.")
@attr('createdBy', required=True)
class RFLinkNode(Device):
    ACTIVITY_TIMEOUT = 1800

    @property
    def controller(self):
        return self.gateway.controller

    @property
    def gateway(self):
        return self.createdBy

    def _send(self, **data):
        return self.controller.send(format_transmitted_data(self.protocol, ID = self.id, **data))

    def _handle_incoming_data(self, protocol, data):

        if 'BAT' in data:
            bat_value = data['BAT']
            if bat_value == 'OK':
                self.battery = 90
            elif bat_value == 'LOW':
                self.battery = 10
