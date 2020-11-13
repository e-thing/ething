# coding: utf-8

from .helpers import *
from .Message import Message
from ething.utils import NullContextManager
from ething.TransportProcess import LineReader, AsyncResult
from ething.scheduler import set_interval, unbind
import time
import re
import logging


LOGGER = logging.getLogger(__name__)


class Result(AsyncResult):
    INIT = 0
    SMART_SLEEP = 1
    SENDING = 2
    WAIT_ACK = 3
    WAIT_RESPONSE = 4
    DONE = 5

    def __init__(self, protocol, message, smartSleep=False, response=False, **kwargs):
        super(Result, self).__init__(message, **kwargs)
        self.protocol = protocol
        self.smartSleep = smartSleep
        self.response = response
        self.ack = message.ack
        self._current_state_index = 0
        self._states = []
        self._states.append(self.INIT)

        if self.smartSleep:
            self._states.append(self.SMART_SLEEP)

        self._states.append(self.SENDING)

        if self.ack:
            self._states.append(self.WAIT_ACK)
        if self.response:
            self._states.append(self.WAIT_RESPONSE)

        self._states.append(self.DONE)

    @property
    def state(self):
        return self._states[self._current_state_index]

    def next(self, **kwargs):

        if self._current_state_index + 1 >= len(self._states):
            return

        self._current_state_index += 1

        current_state = self.state

        if current_state == self.SMART_SLEEP:
            pass
        elif current_state == self.SENDING:
            self.protocol.write_line(self.command.raw(), encode=False)  # raw() returns binary, no need to encode
            self.next(**kwargs)
        elif current_state == self.WAIT_ACK:
            pass
        elif current_state == self.WAIT_RESPONSE:
            pass
        elif current_state == self.DONE:
            self.resolve(**kwargs)

    def resolve(self, *args, **kwargs):
        if self.state == self.DONE:
            super(Result, self).resolve(*args, **kwargs)

    def reject(self, *args, **kwargs):
        self._current_state_index = len(self._states) - 1
        super(Result, self).reject(*args, **kwargs)


class MySensorsProtocol(LineReader):
    TIMEOUT = 10  # seconds (maybe float number)

    def __init__(self, plugin):
        super(MySensorsProtocol, self).__init__(terminator = b'\n')
        self.plugin = plugin
        self.core = plugin.core

        self.gatewayReady = False
        self.gatewayLibVersion = False

        self._pendingMessages = []

    def connection_made(self):
        super(MySensorsProtocol, self).connection_made()
        self._pendingMessages = []

        set_interval(1, self.check_timeout)

    def createNode(self, nodeId):
        plugin = self.plugin

        node = self.core.create('resources/MySensorsNode', {
            'nodeId': nodeId,
            'name': 'node-%d' % (nodeId, )
        })

        if not node:
            raise Exception("fail to create the node nodeId=%d" % nodeId)

        LOGGER.info("MySensors: new node nodeId=%d" % nodeId)

        return node

    def createSensor(self, node, sensorId, sensorType, name=None):

        attributes = {
            'sensorId': sensorId,
            'sensorType': sensorTypeStr(sensorType),
            'createdBy': node.id
        }

        if name:
            attributes['name'] = name

        sensor = None

        for cls in mysensors_sensor_classes:
            S = getattr(cls, 'S', None)

            if (isinstance(S, (list, tuple)) and sensorType in S) or sensorType == S:
                sensor = self.core.create(cls, attributes)
                break

        if not sensor:
            raise Exception("fail to create the sensor nodeId=%d sensorId=%d sensorType=%s" % (
                node.nodeId, sensorId, sensorType))

        LOGGER.info("MySensors: new sensor nodeId=%d sensorId=%d sensorType=%s" % (
            node.nodeId, sensorId, sensorType))

        return sensor

    def handle_line(self, line):
        LOGGER.debug('read: %s', line)

        message = Message.parse(line)

        r = True

        with self.plugin as plugin:

            nodeId = message.nodeId
            sensorId = message.childSensorId
            node = None
            sensor = None
            node_err = False

            # automatically create unknown node and sensor
            if nodeId > 0 and nodeId != BROADCAST_ADDRESS:
                node = plugin.getNode(nodeId)
                if not node:
                    node = self.createNode(nodeId)

            if node and sensorId >= 0 and sensorId != INTERNAL_CHILD:
                sensor = node.getSensor(sensorId)
                if not sensor:
                    if message.messageType == PRESENTATION:
                        sensor = self.createSensor(node, sensorId, message.subType, message.value)
                        node_err = None
                    else:
                        LOGGER.warning('unable to create sensor (node=%s sensor=%s), waiting for a presentation packet, restart the node' % (nodeId, sensorId))
                        node_err = 'restart of the node needed'

            if not node:
                node = NullContextManager()
            if not sensor:
                sensor = NullContextManager()

            with node, sensor:

                if node:
                    node.refresh_connect_state(True)
                    if node_err is not False:
                        node.error = node_err

                if sensor:
                    sensor.refresh_connect_state(True)

                # is ack ?
                if message.ack == NO_ACK:

                    try:

                        if message.messageType == PRESENTATION:

                            if sensorId == INTERNAL_CHILD:
                                # node presentation :
                                if node:
                                    node.libVersion = message.value
                            else:
                                if sensor:
                                    sensor.description = str(message.value)

                        elif message.messageType == SET:

                            if sensor:

                                LOGGER.debug("MySensors: set value nodeId=%d sensorId=%d valueType=%d value=%s",
                                    nodeId, sensorId, message.subType, message.payload)

                                datatype = valueTypeStr(message.subType)

                                if datatype:

                                    # save the raw data payload. used internally for REQ response (see below)
                                    sensor.data['_' + datatype] = message.payload

                                    try:
                                        sensor._set_data(message.subType, message.value)
                                    except:
                                        LOGGER.exception('error in sensor._set_data for sensor %s and datatype=%s' % (sensor, datatype))

                                else:
                                    LOGGER.warning(
                                        "MySensors: unknown value subtype %d" % message.subType)

                        elif message.messageType == REQ:

                            if sensor:

                                datatype = valueTypeStr(message.subType)
                                response = None

                                if datatype:

                                    try:
                                        value = sensor._get_data(message.subType)
                                    except:
                                        LOGGER.exception('error in sensor._get_data for sensor %s and datatype=%s' % (sensor, datatype))
                                        value = None

                                    if value is not None:
                                        response = Message(nodeId, sensorId, SET, message.subType, value=value)
                                    else:
                                        payload = sensor.data.get('_' + datatype)
                                        if payload is not None:
                                            response = Message(nodeId, sensorId, SET, message.subType, payload=payload)

                                    if response:
                                        self.send(response)
                                    else:
                                        # no value stored ! No response
                                        pass

                                else:
                                    LOGGER.warning(
                                        "MySensors: unknown value subtype %d" % message.subType)

                        elif message.messageType == INTERNAL:

                            if message.subType == I_GATEWAY_READY:
                                self.gatewayReady = True
                                LOGGER.info("info: gateway ready")
                                # get the version
                                self.send(Message(GATEWAY_ADDRESS, INTERNAL_CHILD, INTERNAL, I_VERSION))

                            elif message.subType == I_VERSION:
                                self.gatewayLibVersion = message.value
                                plugin.libVersion = message.value
                                LOGGER.info(
                                    "MySensors: gateway version = %s" % self.gatewayLibVersion)

                            elif message.subType == I_TIME:
                                # return current time
                                response = Message(
                                    message.nodeId, message.childSensorId, INTERNAL, I_TIME, int(time.time()))
                                self.send(response)

                            elif message.subType == I_CONFIG:
                                # return M (metric) or I (Imperial)
                                response = Message(
                                    message.nodeId, message.childSensorId, INTERNAL, I_CONFIG,
                                    'M' if plugin.isMetric else 'I')
                                self.send(response)

                            elif message.subType == I_ID_REQUEST:
                                # get a free node id

                                f = None
                                occupied_node_id = [n.nodeId for n in plugin.getNodes()]
                                for i in range(1, 255):
                                    if i not in occupied_node_id:
                                        self.send(Message(
                                            BROADCAST_ADDRESS, INTERNAL_CHILD, INTERNAL, I_ID_RESPONSE, i))
                                        break
                                else:
                                    raise Exception('No free id available')

                            elif message.subType == I_SKETCH_NAME:
                                if node:
                                    sketchName = message.value or ''
                                    node.sketchName = sketchName
                                    # if the default name has not been changed by the user, overwrite it with the sketch name
                                    if re.search('/node-[0-9]+$', node.name) and sketchName:
                                        node.name = sketchName

                            elif message.subType == I_SKETCH_VERSION:
                                if node:
                                    node.sketchVersion = message.value

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

                                    if pendingMessage.state == Result.SMART_SLEEP:
                                        originalMessage = pendingMessage.command
                                        if originalMessage.nodeId == message.nodeId:
                                            pendingMessage.next()

                                    i += 1

                            elif message.subType == I_LOG_MESSAGE:
                                LOGGER.info("MySensors: nodeId=%d sensorId=%d %s" % (
                                    message.nodeId, message.childSensorId, message.value))

                            elif message.subType == I_DISCOVER_RESPONSE:
                                # the payload contains the parent node
                                # useful to get the topology of the network
                                pass

                            else:
                                LOGGER.warning(
                                    "MySensors: message not processed : %s" % str(message))

                        #elif message.messageType == STREAM:

                            # todo
                            # self.handle_stream(...)

                        else:
                            raise Exception("unknown message %s" %
                                            str(message))

                    except Exception as e:
                        LOGGER.exception(e)
                        r = False

                    i = 0
                    while i < len(self._pendingMessages):
                        pendingMessage = self._pendingMessages[i]

                        if pendingMessage.state == Result.WAIT_RESPONSE:
                            originalMessage = pendingMessage.command
                            if originalMessage.nodeId == message.nodeId and originalMessage.childSensorId == message.childSensorId:

                                response_filter = pendingMessage.response
                                ok = True

                                if isinstance(response_filter, dict):
                                    if 'messageType' in response_filter and response_filter['messageType'] != message.messageType:
                                        ok = False
                                    if 'subType' in response_filter and response_filter['subType'] != message.subType:
                                        ok = False

                                if ok:
                                    pendingMessage.next(data = message)

                        i += 1

                else:
                    # ack message
                    LOGGER.debug("ack message received")

                    i = 0
                    while i < len(self._pendingMessages):
                        pendingMessage = self._pendingMessages[i]
                        originalMessage = pendingMessage.command

                        if originalMessage.nodeId == message.nodeId and \
                                originalMessage.childSensorId == message.childSensorId and \
                                originalMessage.messageType == message.messageType and \
                                originalMessage.subType == message.subType:
                            
                            LOGGER.debug("ack match")

                            pendingMessage.next()

                            break
                        
                        i += 1

        return r

    def send(self, message, smartSleep=None, done=None, err=None, response=None):

        LOGGER.debug("message send smartSleep=%s msg=%s", str(smartSleep), message)

        result = Result(self, message, done = done, err = err, smartSleep=smartSleep, response=response)

        if self.transport.is_open:
            result.next()

            if result.state != Result.DONE:
                self._pendingMessages.append(result)
        else:
            result.reject('not connected')

        return result

    def connection_lost(self, exc):

        unbind(self.check_timeout)

        for pendingMessages in self._pendingMessages:
            pendingMessages.reject('disconnected')
        self._pendingMessages = []

        super(MySensorsProtocol, self).connection_lost(exc)

    def check_timeout(self):
        # check for timeout !
        now = time.time()

        # check for pending message timeout
        i = 0
        while i < len(self._pendingMessages):
            pendingMessage = self._pendingMessages[i]
            remove = False

            if now - pendingMessage.send_ts > self.TIMEOUT:
                pendingMessage.reject('timeout')
                remove = True

            if pendingMessage.state == Result.DONE:
                remove = True

            if remove:
                # remove this item
                self._pendingMessages.pop(i)
                i -= 1

            i += 1




