# coding: utf-8

from .MySensorsNode import MySensorsNode
from .MySensorsSensor import MySensorsSensor
from .protocol import MySensorsProtocol
from .helpers import *
from .Message import Message
from ething import Plugin
from ething.reg import *
from ething.TransportProcess import TransportProcess, NetTransport, SerialTransport
import logging

LOGGER = logging.getLogger(__name__)


@attr('isMetric', type=Boolean(), default=True, description="Set the unit to Metric(default) instead of Imperial.")
@attr('libVersion', default=None, mode=READ_ONLY, description="The version of the MySensors library used.")
@attr('connected', type=Boolean(), default=False, mode=READ_ONLY,
      description="Set to true when connected to the MySensors gateway.")
class MySensorsPlugin(Plugin):

    def setup(self):
        self.controller = None

        eth_enable = self.options.get('eth_enable', 'no').lower()
        if eth_enable in ('1', 'y', 'yes', 'true'):
            # ethernet
            if not self.options.get('host'):
                self.logger.warning("no host set in the configuration file")
                self.notification.warning('no host set in the configuration file', title='MySensors',
                                          id='mysensors.check')
            else:
                self.controller = MySensorsEthernetController(self)
        else:
            # serial
            if not self.options.get('serial_port'):
                self.logger.warning("no serial_port set in the configuration file")
                self.notification.warning('no serial_port set in the configuration file', title='MySensors',
                                          id='mysensors.check')
            else:
                self.controller = MySensorsSerialController(self)

        if self.controller is not None:
            self.notification.remove('mysensors.check')
            self.processes.add(self.controller)
        else:
            self.connected = False

    def getNodes(self, filter=None):

        def _filter(r):
            if r.typeof('resources/MySensorsNode'):
                if filter:
                    return filter(r)
                return True
            return False

        return self.core.find(_filter)

    def getNode(self, nodeId):
        return self.core.find_one(lambda r: r.typeof('resources/MySensorsNode') and r.nodeId == nodeId)

    def send(self, nodeId, sensorId, type, subtype, payload=None, value=None, ack=None, smartSleep=None, done=None,
             err=None, response=None):
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
        result = self.send(GATEWAY_ADDRESS, INTERNAL_CHILD, INTERNAL, I_VERSION, response={'subType': I_VERSION})
        return result.data.value

    @method
    def reboot(self):
        """
        Request gateway to reboot.
        """
        self.send(GATEWAY_ADDRESS, INTERNAL_CHILD, INTERNAL, I_REBOOT)

    def ping(self):
        result = self.send(GATEWAY_ADDRESS, INTERNAL_CHILD, INTERNAL, I_PING, response={'subType': I_PONG})
        return

    @method.return_type('object')
    def heartbeat(self):
        result = self.send(GATEWAY_ADDRESS, INTERNAL_CHILD, INTERNAL, I_HEARTBEAT_REQUEST,
                           response={'subType': I_HEARTBEAT_RESPONSE})
        return result.data.value

    @method
    def include(self):
        self.send(GATEWAY_ADDRESS, INTERNAL_CHILD, INTERNAL, I_INCLUSION_MODE, '1')


class MySensorsController(TransportProcess):

    def __init__(self, plugin, transport):
        super(MySensorsController, self).__init__(
            transport=transport,
            protocol=MySensorsProtocol(plugin),
            logger=plugin.logger
        )
        self.plugin = plugin

    def on_open_state_changed(self):
        self.plugin.connected = self.is_open

    def send(self, *args, **kwargs):
        return self.protocol.send(*args, **kwargs)


class MySensorsEthernetController(MySensorsController):
    def __init__(self, plugin):
        host = plugin.options.get('host')
        eth_port = int(plugin.options.get('eth_port', DEFAULT_ETH_PORT))

        super(MySensorsEthernetController, self).__init__(plugin, NetTransport(
            host=host,
            port=eth_port
        ))


class MySensorsSerialController(MySensorsController):
    def __init__(self, plugin):
        port = plugin.options.get('serial_port')
        baudrate = int(plugin.options.get('baudrate', 57600))

        super(MySensorsSerialController, self).__init__(plugin, SerialTransport(
            port=port,
            baudrate=baudrate
        ))
