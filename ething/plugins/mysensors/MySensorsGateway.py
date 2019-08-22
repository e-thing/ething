# coding: utf-8

from future.utils import string_types
from ething.Device import Device
from ething.reg import *
from .helpers import *
from .Message import Message
from .protocol import MySensorsProtocol
from ething.TransportProcess import TransportProcess


class MySensorsController(TransportProcess):
    RESET_ATTR = list()

    def __init__(self, gateway, transport):

        super(MySensorsController, self).__init__(
            'mysensors.%s' % gateway.id,
            transport=transport,
            protocol=MySensorsProtocol(gateway)
        )
        self.gateway = gateway

    def on_open_state_changed(self):
        self.gateway.refresh_connect_state(self.is_open)

    def send(self, *args, **kwargs):
        return self.protocol.send(*args, **kwargs)


@abstract
@attr('isMetric', type=Boolean(), default=True, description="Set the unit to Metric(default) instead of Imperial.")
@attr('libVersion', default=None, mode=READ_ONLY, description="The version of the MySensors library used.")
class MySensorsGateway(Device):
    """
    see https://www.mysensors.org
    """

    def __process__(self):
        self.controller = self.__controller__(self)
        return self.controller

    def on_update(self, dirty_keys):
        for attr in self.controller.RESET_ATTR:
            if attr in dirty_keys:
                self.controller.restart()
                break

    def getNodes(self, filter=None):

        def _filter (r):
            if r.createdBy == self and r.typeof('resources/MySensorsNode'):
                if filter:
                    return filter(r)
                return True
            return False

        return self.core.find(_filter)

    def getNode(self, nodeId):
        return self.core.find_one(lambda r: r.typeof('resources/MySensorsNode') and r.createdBy == self and r.nodeId == nodeId)

    def send(self, nodeId, sensorId, type, subtype, payload=None, value=None, ack=None, smartSleep=None, done=None, err=None, response=None):
        """
        send a message and wait for the response.
        note: not all request has a response !

        :param nodeId: node id
        :param sensorId: sensor id
        :param type: message type
        :param subtype: message subtype
        :param payload: raw payload (string or binary)
        :param value: value. (It will be converted into a raw payload according to the message type and subtype)
        :param ack: whether ack is enabled (default) or not
        :param smartSleep: whether smartSleep is enabled or not.
        :param done: callback when the transaction is completed.
        :param err: callback when the transaction has failed.
        :param response: whether the transaction await for a response or not.
        :return:
        """

        if ack is None:
            ack = False if nodeId == GATEWAY_ADDRESS else True

        message = Message(nodeId, sensorId, type, subtype, value=value, payload=payload, ack=ack)

        result = self.controller.send(message, smartSleep=smartSleep, done=done, err=err, response=response)

        result.wait()

        if result.error:
            raise Exception(str(result.error))

        return result


    @method.arg('nodeId', type=Integer(min=0, max=255), required=True)
    @method.arg('sensorId', type=Integer(min=0, max=255), required=True)
    @method.arg('type', type=Integer(min=0, max=4), required=True)
    @method.arg('subtype', type=Integer(min=0, max=255), required=True)
    @method.arg('payload', type=String(maxLength=25), default="")
    @method.return_type('application/json')
    def send_raw(self, nodeId, sensorId, type, subtype, payload=None):
        """
        send a message.
        """
        return self.send(nodeId, sensorId, type, subtype, payload)

    @method.return_type('string')
    def get_version(self):
        """
        request gateway version.
        """
        result = self.send(GATEWAY_ADDRESS, INTERNAL_CHILD, INTERNAL, I_VERSION, response = {'subType': I_VERSION})
        return result.data.value

    @method
    def reboot(self):
        """
        Request gateway to reboot.
        """
        self.send(GATEWAY_ADDRESS, INTERNAL_CHILD, INTERNAL, I_REBOOT)

    def ping(self):
        result = self.send(GATEWAY_ADDRESS, INTERNAL_CHILD, INTERNAL, I_PING, response = {'subType': I_PONG})
        return

    @method
    def heartbeat(self):
        result = self.send(GATEWAY_ADDRESS, INTERNAL_CHILD, INTERNAL, I_HEARTBEAT_REQUEST, response = {'subType': I_HEARTBEAT_RESPONSE})
        return result.data.value