# coding: utf-8

from ething.Device import Device
from ething.reg import *
from .helpers import *
from collections import MutableSequence


@abstract
@attr('sensorId', type=Integer(min=0, max=254), description="The id of the sensor.")
@attr('sensorType', mode = READ_ONLY, description="The type of the sensor.")
@attr('createdBy', required=True)
class MySensorsSensor (Device):
    """
    MySensorsSensor Device resource representation. This device is normally automatically created by a MySensorsNode instance.
    """

    @property
    def node(self):
        return self.createdBy

    @property
    def nodeId(self):
        return self.node.nodeId

    @property
    def gateway(self):
        return self.node.gateway

    @property
    def controller(self):
        return self.gateway.controller

    @method.arg('type', type=Integer(min=0, max=4))
    @method.arg('subtype', type=Integer(min=0, max=255))
    @method.arg('payload', type=String(maxLength=25))
    @method.return_type('application/json')
    def send(self, type, subtype, payload=''):
        """
        send a message.
        """
        return self.node.send(self.sensorId, type, subtype, payload)

    def _set(self, datatype, value):
        name = valueTypeToName(datatype)

        if isinstance(value, MutableSequence):
            value = ','.join(value)

        self.data[name] = value

