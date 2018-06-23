# coding: utf-8
from future.utils import bord, iteritems
from .MySensorsGateway import MySensorsGateway, Device
from .MySensorsSerialGateway import MySensorsSerialGateway
from .MySensorsEthernetGateway import MySensorsEthernetGateway
from .MySensorsNode import MySensorsNode
from .MySensorsSensor import MySensorsSensor
from .helpers import *
from .Message import Message
from ething.Helpers import dict_recursive_update
from ething.utils import NullContextManager
from ething.plugin import Plugin
from ething.TransportProcess import LineReader, TransportProcess, SerialTransport, NetTransport
from ething.Scheduler import Scheduler
import time
import re
import random
import math
import binascii
try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse



class MySensors(Plugin):

    def load(self):

        self.controllers = {}

        gateways = self.core.find({
            'type': {'$regex': '^MySensors.*Gateway$'}
        })

        for gateway in gateways:
            try:
                self._start_controller(gateway)
            except Exception as e:
                self.log.exception('unable to start the controller for the gateway %s' % gateway)

        self.core.signalDispatcher.bind('ResourceCreated', self._on_resource_created)
        self.core.signalDispatcher.bind('ResourceDeleted', self._on_resource_deleted)
        self.core.signalDispatcher.bind('ResourceMetaUpdated', self._on_resource_updated)

    def unload(self):
        self.core.signalDispatcher.unbind('ResourceCreated', self._on_resource_created)
        self.core.signalDispatcher.unbind('ResourceDeleted', self._on_resource_deleted)
        self.core.signalDispatcher.unbind('ResourceMetaUpdated', self._on_resource_updated)

        self.stop_all_controllers()

    def _on_resource_created(self, signal):
        device = self.core.get(signal['resource'])
        if isinstance(device, MySensorsGateway):
            self._start_controller(device)

    def _on_resource_deleted(self, signal):
        device = self.core.get(signal['resource'])
        if isinstance(device, MySensorsGateway):
            self._stop_controller(device.id)

    def _on_resource_updated(self, signal):
        id = signal['resource']
        if id in self.controllers:
            controller = self.controllers[id]
            gateway = controller.gateway
            if signal['rModifiedDate'] > gateway.modifiedDate:
                gateway.refresh()

            for attr in signal['attributes']:
                if attr in controller.RESET_ATTR:
                    self._stop_controller(id)
                    self._start_controller(gateway)
                    break

    def _start_controller(self, device):
        if isinstance(device, MySensorsGateway):
            controller = MySensorsController(device)
            self.controllers[device.id] = controller
            controller.start()

            self.core.rpc.register('process.%s.send' % device.id, controller.send, callback_name='callback')
            self.core.rpc.register('process.%s.updateFirmware' % device.id, controller.updateFirmware, callback_name='callback')
        else:
            raise Exception('Unknown gateway type "%s"' % type(device).__name__)

    def _stop_controller(self, id):

        if id in self.controllers:
            controller = self.controllers[id]
            controller.stop()
            del self.controllers[id]
            self.core.rpc.unregister('process.%s.send' % id)
            self.core.rpc.unregister('process.%s.updateFirmware' % id)

    def stop_all_controllers(self):
        if hasattr(self, 'controllers'):
            for id in list(self.controllers):
                self._stop_controller(id)



def unpack(data, length=None):

    out = []

    if not isinstance(data, bytearray):
        data = bytearray(data, 'utf-8')

    l = length if length is not None else int(len(data)/2)

    for i in range(0, l):

        first = data[2*i]
        second = data[2*i+1]

        value = (first << 8) | second

        out.append(value)

    return out


def pack(*args):

    o = []

    for v in args:

        first = (v & 0xFF00) >> 8
        second = (v & 0x00FF)

        o.append(first)
        o.append(second)

    return bytearray(o).decode("utf-8")

class MySensorsProtocol(LineReader):
    ACK_TIMEOUT = 5  # seconds (maybe float number)
    PENDING_MESSAGE_TIMEOUT = 120  # seconds (maybe float number)
    FIRMWARE_BLOCK_SIZE = 16  # in bytes
    # in seconds, let the time for the node to restart and install the new firmware
    FIRMWARE_UPDATE_TIMEOUT = 40
    RESPONSE_TIMEOUT = 10
    STREAM_TIMEOUT = 10  # in seconds, max allowed time between 2 blocks of data

    def __init__(self, gateway):
        super(MySensorsProtocol, self).__init__(terminator = b'\n')
        self.gateway = gateway
        self.scheduler = Scheduler()

        self.gatewayReady = False
        self.gatewayLibVersion = False

        # ack management
        self._ackWaitingMessages = []

        # used for smartSleep
        self._pendingMessages = []

        # firmware
        self._pendingFirmware = {}

        # streams
        self._pendingStreams = {}

        # response management
        self._responseListeners = []

        self.scheduler.setInterval(0.5, self.check_timeout)

    def connection_made(self):
        super(MySensorsProtocol, self).connection_made()
        self._responseListeners = []
        self._ackWaitingMessages = []
        self._pendingMessages = []
        self._pendingFirmware = {}
        self._pendingStreams = {}
        self.gateway.setConnectState(True)
    
    def loop(self):
        self.scheduler.process()

    def createNode(self, nodeId):
        gateway = self.gateway

        node = self.gateway.core.create('MySensorsNode', {
            'nodeId': nodeId,
            'name': '%s/node-%d' % (gateway.name, nodeId),
            'createdBy': gateway
        })

        if not node:
            raise Exception("fail to create the node nodeId=%d" % nodeId)

        self.log.info("MySensors: new node nodeId=%d" % nodeId)

        return node

    def createSensor(self, node, sensorId, sensorType=S_UNK):

        sensor = self.gateway.core.create('MySensorsSensor', {
            'name': ('%s/sensor-%d' % (node.name, sensorId)) if sensorType == S_UNK else sensorTypeToName(sensorType),
            'sensorId': sensorId,
            'sensorType': sensorType,
            'createdBy': node
        })

        if not sensor:
            raise Exception("fail to create the sensor nodeId=%d sensorId=%d sensorType=%s" % (
                node.nodeId, sensorId, sensorType))

        self.log.info("MySensors: new sensor nodeId=%d sensorId=%d sensorType=%s" % (
            node.nodeId, sensorId, sensorType))
        return sensor

    def handle_line(self, line):
        self.log.debug('read: %s' % line)

        message = Message.parse(line)

        r = True

        with self.gateway as gateway:

            gateway.setConnectState(True)

            nodeId = message.nodeId
            sensorId = message.childSensorId
            node = None
            sensor = None

            # automatically create unknown node and sensor
            if nodeId > 0 and nodeId != BROADCAST_ADDRESS:
                node = gateway.getNode(nodeId)
                if not node:
                    node = self.createNode(nodeId)

            if node and sensorId >= 0 and sensorId != INTERNAL_CHILD:
                sensor = node.getSensor(sensorId)
                if not sensor:
                    sensor = self.createSensor(
                        node, sensorId, message.subType if message.messageType == PRESENTATION else S_UNK)

            if not node:
                node = NullContextManager()
            if not sensor:
                sensor = NullContextManager()

            with node, sensor:

                if node:
                    node.setConnectState(True)
                if sensor:
                    sensor.setConnectState(True)

                # is ack ?
                if message.ack == NO_ACK:

                    try:

                        if message.messageType == PRESENTATION:
                            sensorType = message.subType

                            # get sensor
                            if sensor:
                                sensor.sensorType = sensorType  # update type
                                sensor.description = message.getValue()

                            elif node:
                                # node internal sensor (id=0xFF)
                                # library version (node device)
                                node._libVersion = message.getValue()

                        elif message.messageType == SET:

                            if sensor:

                                self.log.debug("MySensors: set value nodeId=%d sensorId=%d valueType=%d value=%s" % (
                                    nodeId, sensorId, message.subType, message.payload))

                                datatype = valueTypeStr(message.subType)

                                if datatype:

                                    # save the raw data payload. used internally for REQ response (see below)
                                    sensor.setData(datatype, message.payload)

                                    sensor.storeData(
                                        datatype, message.getValue())

                                else:
                                    self.log.warn(
                                        "MySensors: unknown value subtype %d" % message.subType)

                        elif message.messageType == REQ:

                            if sensor:

                                datatype = valueTypeStr(message.subType)

                                if datatype:
                                    value = sensor.getData(datatype)
                                    if value is not None:
                                        response = Message(
                                            nodeId, sensorId, SET, NO_ACK, message.subType, payload=value)
                                        self.send(response)
                                    else:
                                        # no value stored ! No response
                                        pass

                                else:
                                    self.log.warn(
                                        "MySensors: unknown value subtype %d" % message.subType)

                        elif message.messageType == INTERNAL:

                            if message.subType == I_GATEWAY_READY:
                                self.gatewayReady = True
                                self.log.info("info: gateway ready")

                            elif message.subType == I_VERSION:
                                self.gatewayLibVersion = message.getValue()
                                gateway._libVersion = message.getValue()
                                self.log.info(
                                    "MySensors: gateway version = %s" % self.gatewayLibVersion)

                            elif message.subType == I_TIME:
                                # return current time
                                response = Message(
                                    message.nodeId, message.childSensorId, INTERNAL, NO_ACK, I_TIME, int(time.time()))
                                self.send(response)

                            elif message.subType == I_CONFIG:
                                # return M (metric) or I (Imperial)
                                response = Message(
                                    message.nodeId, message.childSensorId, INTERNAL, NO_ACK, I_CONFIG,
                                    'M' if gateway.isMetric else 'I')
                                self.send(response)

                            elif message.subType == I_ID_REQUEST:
                                # get a free node id

                                f = None
                                for i in range(1, 255):
                                    if not gateway.getNode(i):
                                        f = i
                                        break

                                if f is not None:
                                    response = Message(
                                        BROADCAST_ADDRESS, INTERNAL_CHILD, INTERNAL, NO_ACK, I_ID_RESPONSE, f)
                                    self.send(response)
                                else:
                                    raise Exception('No free id available')

                            elif message.subType == I_SKETCH_NAME:
                                if node:
                                    sketchName = message.getValue() or ''
                                    node._sketchName = sketchName
                                    # if the default name has not been changed by the user, overwrite it with the sketch name
                                    if re.search('^.+/node-[0-9]+$', node.name) and sketchName:
                                        node.name = sketchName

                            elif message.subType == I_SKETCH_VERSION:
                                if node:
                                    node._sketchVersion = message.getValue()

                            elif message.subType == I_BATTERY_LEVEL:
                                if node:
                                    batteryLevel = int(message.payload)
                                    if batteryLevel < 0:
                                        batteryLevel = 0
                                    if batteryLevel > 100:
                                        batteryLevel = 100
                                    node.battery = batteryLevel

                            elif message.subType == I_HEARTBEAT_RESPONSE:

                                # check if there are some pending messages in queue (smartSleep)
                                i = 0
                                while i < len(self._pendingMessages):
                                    pendingMessage = self._pendingMessages[i]

                                    originalMessage = pendingMessage['message']

                                    if originalMessage.nodeId == message.nodeId:
                                        # remove this item
                                        self._pendingMessages.pop(i)
                                        i -= 1

                                        self.send(
                                            originalMessage, smartSleep=False, callback=pendingMessage['callback'])

                                    i += 1

                            elif message.subType == I_LOG_MESSAGE:
                                self.log.info("MySensors: nodeId=%d sensorId=%d %s" % (
                                    message.nodeId, message.childSensorId, message.getValue()))

                            else:
                                self.log.warn(
                                    "MySensors: message not processed : %s" % str(message))

                        elif message.messageType == STREAM:

                            if message.subType == ST_FIRMWARE_CONFIG_REQUEST:
                                """
                                the payload contains the folowing (encoded in hexadecimal):
                                    uint16_t type;                                //!< Type of config
                                    uint16_t version;                            //!< Version of config
                                    uint16_t blocks;                            //!< Number of blocks
                                    uint16_t crc;                                //!< CRC of block data
                                    uint16_t BLVersion;                            //!< Bootloader version
                                """

                                parts = unpack(message.payload)
                                if len(parts) >= 4:
                                    type, version, nbBlocks, crc = parts

                                    bootloaderVersion = parts[4] if len(
                                        parts) > 4 else 0

                                    self.log.info(
                                        "MySensors: FW CONFIG : nodeId=%d type=%04X version=%04X blocks=%d crc=%04X BLVersion=%04X" % (
                                            nodeId, type, version, nbBlocks, crc, bootloaderVersion))

                                    if node:
                                        node._firmware = {
                                            'type': type,
                                            'version': version,
                                            'blocks': nbBlocks,
                                            'crc': crc,
                                            'BLVersion': bootloaderVersion
                                        }

                                    if nodeId in self._pendingFirmware:
                                        # a firware has been updated
                                        # this message is received after reboot

                                        # check if the installed firmware was the one updated
                                        firmwareInfo = self._pendingFirmware[nodeId]
                                        ok = firmwareInfo['type'] == type and firmwareInfo['version'] == version and \
                                             firmwareInfo[
                                                 'blocks'] == nbBlocks and firmwareInfo['crc'] == crc

                                        if ok:
                                            self.log.info(
                                                "MySensors: FW updated successfully : nodeId=%d type=%04X version=%04X blocks=%d crc=%04X" % (
                                                    nodeId, type, version, nbBlocks, crc))
                                        else:
                                            self.log.warn(
                                                "MySensors: FW update ERROR : nodeId=%d" % nodeId)

                                        if callable(firmwareInfo['callback']):
                                            firmwareInfo['callback'](
                                                False if ok else 'error in firmware update')

                                        del self._pendingFirmware[nodeId]

                            elif message.subType == ST_FIRMWARE_CONFIG_RESPONSE:
                                pass
                            elif message.subType == ST_FIRMWARE_REQUEST:
                                """
                                return a peace of the FIRMWARE

                                receive :
                                uint16_t type;        //!< Type of config
                                uint16_t version;    //!< Version of config
                                uint16_t block;        //!< Block index

                                send:
                                uint16_t type;                        //!< Type of config
                                uint16_t version;                    //!< Version of config
                                uint16_t block;                        //!< Block index
                                uint8_t data[FIRMWARE_BLOCK_SIZE];    //!< Block data
                                """

                                if len(message.payload) >= 6:

                                    type, version, iBlock = unpack(
                                        message.payload, 3)

                                    self.log.warn("MySensors: FW GET : nodeId=%d type=%04X version=%04X block=%d" % (
                                        nodeId, type, version, iBlock))

                                    if nodeId in self._pendingFirmware:

                                        chunk = self._pendingFirmware[nodeId]['firmware'][
                                                iBlock * self.FIRMWARE_BLOCK_SIZE:(
                                                                                                iBlock + 1) * self.FIRMWARE_BLOCK_SIZE]
                                        response = Message(message.nodeId, INTERNAL_CHILD, STREAM, NO_ACK,
                                                           ST_FIRMWARE_CONFIG_RESPONSE, pack(
                                                type, version, iBlock) + chunk)

                                        if self._pendingFirmware[nodeId]['lastBlockSent'] != iBlock:
                                            self._pendingFirmware[nodeId]['blockSent'] += 1
                                            self._pendingFirmware[nodeId]['lastBlockSent'] = iBlock

                                        self._pendingFirmware[nodeId]['ts'] = time.time(
                                        )

                                        self.send(response)

                                    else:
                                        self.log.warn(
                                            "MySensors: FW GET : no firmware found")

                            elif message.subType == ST_FIRMWARE_RESPONSE:
                                pass

                            elif message.subType == ST_SOUND or message.subType == ST_IMAGE:

                                """
                                the payload contains a piece of an image or sound

                                payload :

                                | 1byte | next bytes |
                                |-------|------------|
                                | index | data       |

                                """
                                payload = binascii.unhexlify(message.payload)
                                if payload:
                                    index = bord(payload[0])

                                    if nodeId not in self._pendingStreams:
                                        if index == 1:
                                            # new stream
                                            self._pendingStreams[nodeId] = {
                                                't0': time.time(),
                                                'ts': 0,
                                                'lastIndex': 255,
                                                'data': '',
                                                'packetCount': 0,
                                                'type': message.subType
                                            }
                                        else:
                                            self.log.warn(
                                                "MySensors: STREAM: first packet must start with index=1, got %s" % index)

                                    if nodeId in self._pendingStreams:

                                        stream = self._pendingStreams[nodeId]

                                        if stream['type'] == message.subType:
                                            expectedIndex = 1 if stream['lastIndex'] == 255 else stream['lastIndex'] + 1

                                            if index == 0 or expectedIndex == index:
                                                # append this chunk
                                                stream['data'] += payload[1:]
                                                stream['lastIndex'] = index
                                                stream['packetCount'] += 1
                                                stream['ts'] = time.time()

                                                if index == 0:
                                                    # end of the stream

                                                    size = len(stream['data'])
                                                    timeElapsed = time.time() - \
                                                                  stream['t0']

                                                    sensor.storeStream(
                                                        stream['type'], stream['data'])

                                                    # remove stream from list
                                                    del self._pendingStreams[nodeId]

                                                    self.log.warn(
                                                        "MySensors: STREAM: end of stream, packetCount=%d , size(B)=%d , time(s)=%f" % (
                                                            stream['packetCount'], size, timeElapsed))

                                            else:
                                                # remove on first error
                                                del self._pendingStreams[nodeId]
                                                self.log.warn(
                                                    "MySensors: STREAM: index mismatch")

                                        else:
                                            self.log.warn(
                                                "MySensors: STREAM: type mismatch")

                            else:
                                self.log.warn(
                                    "MySensors: message not processed : %s" % str(message))

                        else:
                            raise Exception("unknown message %s" %
                                            str(message))

                    except Exception as e:
                        self.log.exception(e)
                        r = False

                    i = 0
                    while i < len(self._responseListeners):
                        responseListener = self._responseListeners[i]

                        if (('nodeId' not in responseListener) or responseListener['nodeId'] == message.nodeId) and \
                                (('childSensorId' not in responseListener) or responseListener[
                                    'childSensorId'] == message.childSensorId) and \
                                (('messageType' not in responseListener) or responseListener[
                                    'messageType'] == message.messageType) and \
                                (('subType' not in responseListener) or responseListener['subType'] == message.subType):

                            # remove this item
                            self._responseListeners.pop(i)
                            i -= 1

                            if callable(responseListener['callback']):
                                responseListener['callback'](False, message)

                        i += 1

                else:
                    # ack message

                    i = 0
                    while i < len(self._ackWaitingMessages):
                        ackWaitingMessage = self._ackWaitingMessages[i]
                        originalMessage = ackWaitingMessage['message']

                        if originalMessage.nodeId == message.nodeId and \
                                originalMessage.childSensorId == message.childSensorId and \
                                originalMessage.messageType == message.messageType and \
                                originalMessage.subType == message.subType:

                            # remove this item
                            self._ackWaitingMessages.pop(i)
                            i -= 1

                            if callable(ackWaitingMessage['callback']):
                                ackWaitingMessage['callback'](
                                    False, originalMessage)

                            break

                        i += 1

        return r

    def send(self, message, smartSleep=None, callback=None, waitResponse=None):
        """
         $message message to send
         $smartSleep (optional) true|false|null if a boolean is given, force or not the smartSleep feature
         $callback (optional) function($error, $messageSent, $messageReceived = null)
         $waitResponse (optional) true|false wait for a response or not
        """
        cb = None

        if smartSleep is None:
            smartSleep = False
            if message.nodeId != GATEWAY_ADDRESS and message.nodeId != BROADCAST_ADDRESS:
                destinationNode = self.gateway.getNode(message.nodeId)
                if destinationNode:
                    smartSleep = destinationNode.smartSleep

        if callable(callback):
            if waitResponse:

                filter = {}

                if message.messageType == REQ:
                    filter['messageType'] = SET

                elif message.messageType == INTERNAL:

                    if message.subType == I_ID_REQUEST:
                        filter['subType'] = I_ID_RESPONSE
                    elif message.subType == I_NONCE_REQUEST:
                        filter['subType'] = I_NONCE_RESPONSE
                    elif message.subType == I_HEARTBEAT_REQUEST:
                        filter['subType'] = I_HEARTBEAT_RESPONSE
                    elif message.subType == I_DISCOVER_REQUEST:
                        filter['subType'] = I_DISCOVER_RESPONSE
                    elif message.subType == I_PING:
                        filter['subType'] = I_PONG
                    elif message.subType == I_REGISTRATION_REQUEST:
                        filter['subType'] = I_REGISTRATION_RESPONSE
                    elif message.subType == I_PRESENTATION:
                        # todo
                        # multiple response
                        pass
                    elif message.subType == I_DEBUG or message.subType == I_VERSION:
                        filter['subType'] = message.subType

                    if filter:
                        filter['messageType'] = INTERNAL

                def waitresp_cb(error, messageSent):
                    if error:
                        # an error occurs, the message could not have been sent
                        callback(error, messageSent, None)
                    else:
                        # wait for a response

                        def cb(error, messageReceived):
                            callback(error, messageSent, messageReceived)

                        self._responseListeners.append(dict_recursive_update({
                            'callback': cb,
                            'ts': time.time(),
                            'nodeId': messageSent.nodeId,
                            'childSensorId': messageSent.childSensorId,
                            'messageType': messageSent.messageType,
                            'subType': messageSent.subType
                        }, filter))

                cb = waitresp_cb

            else:

                def nowaitresp_cb(error, messageSent):
                    callback(error, messageSent, None)

                cb = nowaitresp_cb

        self.log.debug("MySensors: message send nodeId=%d sensorId=%d messageType=%d smartSleep=%s" % (
            message.nodeId, message.childSensorId, message.messageType, str(smartSleep)))

        ts = time.time()

        message.ts = ts

        if not self.process.is_open:
            if cb:
                cb('not connected', message)

            return

        if smartSleep:
            # buffer this message
            # wait for a heartbeat message to send it !

            self._pendingMessages.append({
                'message': message,
                'callback': cb,
                'ts': ts
            })

            return
        else:

            if message.ack == REQUEST_ACK:
                # ack requested
                self._ackWaitingMessages.append({
                    'message': message,
                    'callback': cb,
                    'ts': ts
                })

            wb = self.write_line(message.raw(), encode = False) # raw() returns binary, no need to encode

            if message.ack != REQUEST_ACK and cb:
                cb(False, message)

            return

    def updateFirmware(self, node, firmware, callback=None):

        # tells the node, there is a new firmware
        type = random.randint(1, 32767)
        version = 256  # === 1.0 or 0100 in hex
        nbBlocks = int(math.ceil(len(firmware) / self.FIRMWARE_BLOCK_SIZE))
        crc = binascii.crc_hqx(firmware, 0)

        self._pendingFirmware[node.nodeId] = {
            'callback': callback,
            'firmware': firmware,
            'deviceId': node.id,
            'ts': time.time(),
            'lastBlockSent': -1,
            'blockSent': 0,
            'type': type,
            'version': version,
            'nbBlocks': nbBlocks,
            'crc': crc
        }

        message = Message(node.nodeId, INTERNAL_CHILD, STREAM, NO_ACK,
                          ST_FIRMWARE_CONFIG_RESPONSE, pack('nnnn', type, version, nbBlocks, crc))

        def cb(error, messageSent, messageReceived):
            if error:
                # free memory
                del self._pendingFirmware[node.nodeId]

                if callable(callback):
                    callback(error)

        self.send(message, callback=cb)

    def connection_lost(self, exc):

        self.gateway.setConnectState(False)

        for responseListener in self._responseListeners:
            responseListener['callback']('disconnected', None)
        self._responseListeners = []

        super(MySensorsProtocol, self).connection_lost(exc)

    def check_timeout(self):
        # check for timeout !
        now = time.time()

        # check for timeout ack messages
        i = 0
        while i < len(self._ackWaitingMessages):
            ackWaitingMessage = self._ackWaitingMessages[i]

            if now - ackWaitingMessage['ts'] > self.ACK_TIMEOUT:

                # remove this item
                self._ackWaitingMessages.pop(i)
                i -= 1

                if callable(ackWaitingMessage['callback']):
                    ackWaitingMessage['callback'](
                        'ack timeout', ackWaitingMessage['message'])

            i += 1

        # check for pending message timeout
        i = 0
        while i < len(self._pendingMessages):
            pendingMessage = self._pendingMessages[i]

            if now - pendingMessage['ts'] > self.PENDING_MESSAGE_TIMEOUT:

                # remove this item
                self._pendingMessages.pop(i)
                i -= 1

                if callable(pendingMessage['callback']):
                    pendingMessage['callback'](
                        'smartSleep timeout', pendingMessage['message'])

            i += 1

        # check firmware update timeout
        for nodeId, firmwareInfo in iteritems(self._pendingFirmware):
            if now - firmwareInfo['ts'] > self.FIRMWARE_UPDATE_TIMEOUT:

                # remove this item
                del self._pendingFirmware[nodeId]

                if callable(firmwareInfo['callback']):
                    firmwareInfo['callback']('firmware update timeout')

        # check stream timeout
        for nodeId, stream in iteritems(self._pendingStreams):
            if now - stream['ts'] > self.STREAM_TIMEOUT:
                # remove this item
                del self._pendingStreams[nodeId]

        # check response timeout
        i = 0
        while i < len(self._responseListeners):
            responseListener = self._responseListeners[i]

            if now - responseListener['ts'] > self.RESPONSE_TIMEOUT:

                # remove this item
                self._responseListeners.pop(i)
                i -= 1

                if callable(responseListener['callback']):
                    responseListener['callback']('response timeout', None)

            i += 1


class MySensorsController(TransportProcess):
    RESET_ATTR = ['port', 'baudrate', 'address']

    def __init__(self, gateway):

        if isinstance(gateway, MySensorsSerialGateway):
            transport = SerialTransport(
                port=gateway.port,
                baudrate=gateway.baudrate
            )
        elif isinstance(gateway, MySensorsEthernetGateway):
            o = urlparse('tcp://' + gateway.address)
            transport = NetTransport(
                host=o.hostname,
                port=o.port
            )
        else:
            raise RuntimeError('invalid gateway type %s' % type(gateway).__name__)

        super(MySensorsController, self).__init__(
            'mysensors',
            transport=transport,
            protocol=MySensorsProtocol(gateway)
        )
        self.gateway = gateway

    def send(self, *args, **kwargs):
        self.protocol.send(*args, **kwargs)

    def updateFirmware(self, *args, **kwargs):
        self.protocol.updateFirmware(*args, **kwargs)

