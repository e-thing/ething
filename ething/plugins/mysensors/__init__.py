# coding: utf-8
from future.utils import iteritems
from .MySensorsGateway import MySensorsGateway
from .MySensorsSerialGateway import MySensorsSerialGateway
from .MySensorsEthernetGateway import MySensorsEthernetGateway
from .MySensorsNode import MySensorsNode
from .MySensorsSensor import MySensorsSensor

from .MySensorsThermometer import MySensorsThermometer
from .MySensorsHumiditySensor import MySensorsHumiditySensor
from .MySensorsPressureSensor import MySensorsPressureSensor
from .MySensorsBinary import MySensorsBinary
from .MySensorsGenericSensor import MySensorsGenericSensor
from .MySensorsRGB import MySensorsRGB
from .MySensorsRGBW import MySensorsRGBW
from .MySensorsDimmer import MySensorsDimmer

from .helpers import *
from .Message import Message
from ething.core.utils import NullContextManager
from ething.core.plugin import Plugin
from ething.core.TransportProcess import LineReader, TransportProcess, SerialTransport, NetTransport, BaseResult
from ething.core.scheduler import Scheduler
import time
import re
import datetime


class MySensors(Plugin):

    def start(self):
        super(MySensors, self).start()

        self.controllers = {}

        gateways = self.core.find(lambda r: r.isTypeof('resources/MySensorsGateway'))

        for gateway in gateways:
            try:
                self._start_controller(gateway)
            except:
                self.log.exception('unable to start the controller for the gateway %s' % gateway)

        self.core.signalDispatcher.bind('ResourceCreated', self._on_resource_created)
        self.core.signalDispatcher.bind('ResourceDeleted', self._on_resource_deleted)
        self.core.signalDispatcher.bind('ResourceUpdated', self._on_resource_updated)

    def stop(self):
        super(MySensors, self).stop()
        self.core.signalDispatcher.unbind('ResourceCreated', self._on_resource_created)
        self.core.signalDispatcher.unbind('ResourceDeleted', self._on_resource_deleted)
        self.core.signalDispatcher.unbind('ResourceUpdated', self._on_resource_updated)

        self.stop_all_controllers()

    def _on_resource_created(self, signal):
        device = signal.resource
        if isinstance(device, MySensorsGateway):
            self._start_controller(device)

    def _on_resource_deleted(self, signal):
        device = signal.resource
        if isinstance(device, MySensorsGateway):
            self._stop_controller(device.id)

    def _on_resource_updated(self, signal):
        id = signal.resource.id
        if id in self.controllers:
            controller = self.controllers[id]
            for attr in signal['attributes']:
                if attr in controller.RESET_ATTR:
                    self._stop_controller(id)
                    self._start_controller(controller.gateway)
                    break

    def _start_controller(self, device):
        if isinstance(device, MySensorsGateway):
            controller = MySensorsController(device)
            self.controllers[device.id] = controller
            controller.start()
        else:
            raise Exception('Unknown gateway type "%s"' % type(device).__name__)

    def _stop_controller(self, id):

        if id in self.controllers:
            controller = self.controllers[id]
            controller.stop()
            del self.controllers[id]

    def stop_all_controllers(self):
        if hasattr(self, 'controllers'):
            for id in list(self.controllers):
                self._stop_controller(id)




class Result(BaseResult):
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

    def __init__(self, gateway):
        super(MySensorsProtocol, self).__init__(terminator = b'\n')
        self.gateway = gateway
        self.core = gateway.ething
        self.scheduler = Scheduler()

        self.gatewayReady = False
        self.gatewayLibVersion = False

        self._pendingMessages = []

    def connection_made(self):
        super(MySensorsProtocol, self).connection_made()
        self._pendingMessages = []
        self.gateway.setConnectState(True)

        self.core.scheduler.setInterval(1, self.check_timeout)
        self.core.scheduler.setInterval(60, self.check_disconnect)

    def createNode(self, nodeId):
        gateway = self.gateway

        node = self.core.create('resources/MySensorsNode', {
            'nodeId': nodeId,
            'name': '%s/node-%d' % (gateway.name, nodeId),
            'createdBy': gateway.id
        })

        if not node:
            raise Exception("fail to create the node nodeId=%d" % nodeId)

        self.log.info("MySensors: new node nodeId=%d" % nodeId)

        return node

    def createSensor(self, node, sensorId, sensorType):

        attributes = {
            'name':  sensorTypeToName(sensorType) or ('%s/sensor-%d' % (node.name, sensorId)),
            'sensorId': sensorId,
            'sensorType': sensorTypeStr(sensorType),
            'createdBy': node.id
        }

        if sensorType == S_TEMP:
            sensor = self.core.create('resources/MySensorsThermometer', attributes)

        elif sensorType == S_HUM:
            sensor = self.core.create('resources/MySensorsHumiditySensor', attributes)

        elif sensorType == S_BARO:
            sensor = self.core.create('resources/MySensorsPressureSensor', attributes)

        elif sensorType == S_BINARY or sensorType == S_SPRINKLER:
            sensor = self.core.create('resources/MySensorsBinary', attributes)

        elif sensorType == S_DIMMER:
            sensor = self.core.create('resources/MySensorsDimmer', attributes)

        elif sensorType == S_RGB_LIGHT:
            sensor = self.core.create('resources/MySensorsRGB', attributes)

        elif sensorType == S_RGBW_LIGHT:
            sensor = self.core.create('resources/MySensorsRGBW', attributes)

        else:
            sensor = self.core.create('resources/MySensorsGenericSensor', attributes)

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
                    if message.messageType == PRESENTATION:
                        sensor = self.createSensor(node, sensorId, message.subType)
                    else:
                        self.log.warning('unable to create sensor (node=%s sensor=%s), waiting for a presentation packet, restart the node' % (nodeId, sensorId))

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

                            if sensorId == INTERNAL_CHILD:
                                # node presentation :
                                if node:
                                    node.libVersion = message.value
                            else:
                                if sensor:
                                    sensor.description = message.value

                        elif message.messageType == SET:

                            if sensor:

                                self.log.debug("MySensors: set value nodeId=%d sensorId=%d valueType=%d value=%s" % (
                                    nodeId, sensorId, message.subType, message.payload))

                                datatype = valueTypeStr(message.subType)

                                if datatype:

                                    # save the raw data payload. used internally for REQ response (see below)
                                    sensor.data['_' + datatype] = message.payload

                                    try:
                                        sensor._set_data(message.subType, message.value)
                                    except:
                                        self.log.exception('error in sensor._set_data for sensor %s and datatype=%s' % (sensor, datatype))

                                else:
                                    self.log.warning(
                                        "MySensors: unknown value subtype %d" % message.subType)

                        elif message.messageType == REQ:

                            if sensor:

                                datatype = valueTypeStr(message.subType)

                                if datatype:
                                    payload = sensor.data.get('_' + datatype)
                                    if payload is not None:
                                        response = Message(
                                            nodeId, sensorId, SET, message.subType, payload=payload)
                                        self.send(response)
                                    else:
                                        # no value stored ! No response
                                        pass

                                else:
                                    self.log.warning(
                                        "MySensors: unknown value subtype %d" % message.subType)

                        elif message.messageType == INTERNAL:

                            if message.subType == I_GATEWAY_READY:
                                self.gatewayReady = True
                                self.log.info("info: gateway ready")

                            elif message.subType == I_VERSION:
                                self.gatewayLibVersion = message.value
                                gateway.libVersion = message.value
                                self.log.info(
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
                                    'M' if gateway.isMetric else 'I')
                                self.send(response)

                            elif message.subType == I_ID_REQUEST:
                                # get a free node id

                                f = None
                                occupied_node_id = [n.nodeId for n in gateway.getNodes()]
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
                                self.log.info("MySensors: nodeId=%d sensorId=%d %s" % (
                                    message.nodeId, message.childSensorId, message.value))

                            elif message.subType == I_DISCOVER_RESPONSE:
                                # the payload contains the parent node
                                # useful to get the topology of the network
                                pass

                            else:
                                self.log.warning(
                                    "MySensors: message not processed : %s" % str(message))

                        #elif message.messageType == STREAM:

                            # todo
                            # self.handle_stream(...)

                        else:
                            raise Exception("unknown message %s" %
                                            str(message))

                    except Exception as e:
                        self.log.exception(e)
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
                    self.log.debug("ack message received")

                    i = 0
                    while i < len(self._pendingMessages):
                        pendingMessage = self._pendingMessages[i]
                        originalMessage = pendingMessage.command

                        if originalMessage.nodeId == message.nodeId and \
                                originalMessage.childSensorId == message.childSensorId and \
                                originalMessage.messageType == message.messageType and \
                                originalMessage.subType == message.subType:
                            
                            self.log.debug("ack match")

                            pendingMessage.next()

                            break
                        
                        i += 1

        return r

    def send(self, message, smartSleep=None, done=None, err=None, response=None):

        self.log.debug("message send smartSleep=%s msg=%s" % (str(smartSleep), message))

        result = Result(self, message, done = done, err = err, smartSleep=smartSleep, response=response)

        if self.process.is_open:
            result.next()

            if result.state != Result.DONE:
                self._pendingMessages.append(result)
        else:
            result.reject('not connected')

        return result

    def connection_lost(self, exc):

        self.core.scheduler.unbind(self.check_timeout)
        self.core.scheduler.unbind(self.check_disconnect)

        self.gateway.setConnectState(False)

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
    
    def check_disconnect(self):
        devices = self.core.find(lambda r: r.isTypeof('resources/MySensorsNode'))
        
        now = datetime.datetime.utcnow()
        
        for device in devices:
            if device.lastSeenDate and now - device.lastSeenDate > datetime.timedelta(seconds=1800):
                device.setConnectState(False)
                for sensor in device.getSensors():
                    sensor.setConnectState(False)


class MySensorsController(TransportProcess):
    RESET_ATTR = ['port', 'baudrate', 'host']

    def __init__(self, gateway):

        if isinstance(gateway, MySensorsSerialGateway):
            transport = SerialTransport(
                port=gateway.port,
                baudrate=gateway.baudrate
            )
        elif isinstance(gateway, MySensorsEthernetGateway):
            transport = NetTransport(
                host=gateway.host,
                port=gateway.port
            )
        else:
            raise RuntimeError('invalid gateway type %s' % type(gateway).__name__)

        super(MySensorsController, self).__init__(
            'mysensors.%s' % gateway.id,
            transport=transport,
            protocol=MySensorsProtocol(gateway)
        )
        self.gateway = gateway

    def send(self, *args, **kwargs):
        return self.protocol.send(*args, **kwargs)

