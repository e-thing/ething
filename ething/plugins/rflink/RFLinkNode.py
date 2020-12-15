# coding: utf-8

from ething.Device import Device, ResourceSignal
from ething.reg import *
from .helpers import *


class RFLinkMsgReceived(ResourceSignal):
    """
    is emitted each time the RFLink controller received a message from a device
    """
    def __init__(self, resource, data):
        super(RFLinkMsgReceived, self).__init__(resource, **data)


@abstract
@attr('nodeId', type=String(allow_empty=False), mode = READ_ONLY, description="The hardware id of the node.")
@attr('protocol', type=String(allow_empty=False), mode = READ_ONLY, description="The protocol name of the node.")
@attr('createdBy', required=True)
@attr('debug', type=Boolean(), default=False,
      description='enable debugging, if set, all incoming messages are saved into a table.')
class RFLinkNode(Device):
    ACTIVITY_TIMEOUT = 1800

    @property
    def controller(self):
        return self.plugin.controller

    @property
    def plugin(self):
        return self.core.plugins['rflink']

    def _send(self, **data):
        return self.controller.send(format_transmitted_data(self.protocol, ID = self.id, **data))

    def _handle_incoming_data(self, protocol, data):

        if 'BAT' in data:
            bat_value = data['BAT']
            if bat_value == 'OK':
                self.battery = 90
            elif bat_value == 'LOW':
                self.battery = 10
