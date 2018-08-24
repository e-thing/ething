# coding: utf-8


from future.utils import string_types
from ething.Device import Device
from ething.reg import *
from .helpers import *
from .Message import Message
from ething.Process import get_process


@abstract
@attr('isMetric', type=Boolean(), default=True, description="Set the unit to Metric(default) instead of Imperial.")
@attr('libVersion', default=None, mode=READ_ONLY, description="The version of the MySensors library used.")
class MySensorsGateway(Device):
    """
    see https://www.mysensors.org
    """

    @property
    def controller(self):
        return get_process('mysensors.%s' % self.id)

    def getNodes(self, filter=None):

        def _filter (r):
            if r.createdBy == self and r.isTypeof('resources/MySensorsNode'):
                if filter:
                    return filter(r)
                return True
            return False

        return self.ething.find(_filter)

    def getNode(self, nodeId):
        return self.ething.findOne(lambda r: r.isTypeof('resources/MySensorsNode') and r.createdBy == self and r.nodeId == nodeId)

    def removeAllNodes(self):
        # remove all the nodes attached to it !
        for node in self.getNodes():
            node.remove()

    def remove(self, removeChildren=False):

        # remove all the nodes attached to it !
        self.removeAllNodes()

        # remove the resource
        super(MySensorsGateway, self).remove(removeChildren)

    @method.arg('nodeId', type=Integer(min=0, max=255), required=True)
    @method.arg('sensorId', type=Integer(min=0, max=255), required=True)
    @method.arg('type', type=Integer(min=0, max=4), required=True)
    @method.arg('subtype', type=Integer(min=0, max=255), required=True)
    @method.arg('payload', type=String(maxLength=25), default="")
    @method.return_type('application/json')
    def send(self, nodeId, sensorId=None, type=None, subtype=None, payload=None, **kwargs):
        """
        send a message.
        """
        message = Message(nodeId, sensorId, type, subtype, value = payload, ack = kwargs.get('ack', True))

        result = self.controller.send(message, **kwargs)

        result.wait()

        if result.error:
            raise Exception(str(result.error))

        return result

    # send a message and wait for the response.
    # note: not all request has a response !

    @method.return_type('string')
    def getVersion(self):
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