# coding: utf-8
from .RFLinkGateway import RFLinkGateway
from .RFLinkSerialGateway import RFLinkSerialGateway
from .RFLinkSwitch import RFLinkSwitch
from .RFLinkGenericSensor import RFLinkGenericSensor
from ething.plugin import Plugin
from ething.TransportProcess import LineReader, TransportProcess, SerialTransport
from ething.Scheduler import Scheduler
from .helpers import parse_incoming_data, is_protocol, Result
import time
import re
import datetime


class RFLink(Plugin):

    def load(self):

        self.controllers = {}

        gateways = self.core.find(lambda r: r.isTypeof('resources/RFLinkGateway'))

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
        device = signal.resource
        if isinstance(device, RFLinkGateway):
            self._start_controller(device)

    def _on_resource_deleted(self, signal):
        device = signal.resource
        if isinstance(device, RFLinkGateway):
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
        if isinstance(device, RFLinkSerialGateway):
            controller = RFLinkSerialController(device)
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



class RFLinkProtocol(LineReader):

    RESPONSE_TIMEOUT = 10  # seconds

    def __init__(self, gateway):
        super(RFLinkProtocol, self).__init__()
        self.gateway = gateway
        self.core = gateway.ething
        # response management
        self._responseListeners = []
        self.scheduler = Scheduler()

        self.scheduler.setInterval(0.5, self.check_response_timeout)
        self.scheduler.setInterval(60, self.check_disconnect)

    def connection_made(self):
        super(RFLinkProtocol, self).connection_made()
        self._responseListeners = []
        self.gateway.setConnectState(True)
    
    def loop(self):
        self.scheduler.process()

    # exemple of messages :
    #     20;00;Nodo RadioFrequencyLink - RFLink Gateway V1.1 - R46;
    #     20;01;MySensors=OFF;NO NRF24L01;
    #     20;02;setGPIO=ON;
    #     20;03;Cresta;ID=8301;WINDIR=0005;WINSP=0000;WINGS=0000;WINTMP=00c3;WINCHL=00c3;BAT=LOW;
    #     20;04;Cresta;ID=3001;TEMP=00b4;HUM=50;BAT=OK;
    #     20;05;Cresta;ID=2801;TEMP=00af;HUM=53;BAT=OK;
    #     20;06;NewKaku;ID=008440e6;SWITCH=1;CMD=OFF;
    #     20;02;VER=1.1;REV=46;BUILD=0c;
    def handle_line(self, line):
        self.log.debug('read: %s' % line)

        gateway = self.gateway

        # keep only messages destined to the gateway
        if not line.startswith('20;'):
            return

        # remove trailing ';'
        line = line.rstrip(';')

        parts = line.split(';', 3)

        if len (parts) == 4 and is_protocol(parts[2]):

            _, packet_counter, protocol, message = parts

            data = parse_incoming_data(protocol, message)

            if 'ID' in data:

                def filter (r):
                    if r.isTypeof('resources/RFLinkNode') and r.nodeId == data['ID'] and r.protocol == protocol and r.createdBy == self:
                        if 'SWITCH' in data:
                            return r.switchId == data['SWITCH']
                        return True

                device = gateway.getNode(filter)

                if not device:

                    if gateway.inclusion:

                        attributes = {
                            'nodeId': data['ID'],
                            'protocol': protocol,
                            'name': data['ID'],
                            'createdBy': gateway.id
                        }

                        device = self.create_device(protocol, data, attributes)

                        if not device:
                            self.log.warning("fail to create the node from %s" % (line))

                if device:
                    with device:
                        device.setConnectState(True)
                        device._handle_incoming_data(protocol, data)

        else:

            matches = re.search(
                'Nodo RadioFrequencyLink - RFLink Gateway V([\d\.]+) - R([\d]+)', parts[2])
            if matches:
                with gateway:
                    gateway._version = matches.group(1)
                    gateway._revision = matches.group(2)
                self.log.info("RFLink: ver:%s rev:%s" %
                              (matches.group(1), matches.group(2)))
            else:
                matches = re.search(
                    ';VER=([\d\.]+);REV=([\d]+);BUILD=([0-9a-fA-F]+);', line)
                if matches:
                    with gateway:
                        gateway._version = matches.group(1)
                        gateway._revision = matches.group(2)
                        gateway._build = matches.group(3)
                    self.log.info("RFLink: ver:%s rev:%s build:%s" % (
                        matches.group(1), matches.group(2), matches.group(3)))

        i = 0
        while i < len(self._responseListeners):
            responseListener = self._responseListeners[i]

            if re.search(responseListener.response, line):
                responseListener.resolve(line)
                self._responseListeners.pop(i)
                i -= 1


    def create_device(self, protocol, data, attributes):

        # generic node
        if 'SWITCH' in data:
            attributes['name'] = 'switch-%s' % data['ID']
            attributes['switchId'] = data['SWITCH']
            return RFLinkSwitch.create(attributes, ething = self.core)

        # try to generate a generic sensor
        sensor_cls = RFLinkGenericSensor.create_class_from_data(protocol, data)
        if sensor_cls:
            return sensor_cls.create(attributes, ething = self.core)


    # $message message to send
    # $callback (optional) function(error, messageSent, messageReceived = None)
    # $waitResponse (optional) true|false wait for a response or not
    def send(self, message, done = None, err = None, response = None):

        self.log.debug("RFLink: send message '%s'" % message)

        result = Result(response, message, done = done, err = err)

        self.write_line(message)

        if not response:
            result.resolve()
        else :
            self._responseListeners.append(result)

        return result

    def connection_lost(self, exc):

        self.gateway.setConnectState(False)

        for responseListener in self._responseListeners:
            responseListener.reject('disconnected')
        self._responseListeners = []

        super(RFLinkProtocol, self).connection_lost(exc)

    def check_response_timeout(self):
        # check for timeout !
        now = time.time()
        i = 0
        while i < len(self._responseListeners):
            responseListener = self._responseListeners[i]

            if now - responseListener.send_ts > self.RESPONSE_TIMEOUT:
                # remove this item
                self._responseListeners.pop(i)
                i -= 1

                responseListener.reject('response timeout')

            i += 1
    
    def check_disconnect(self):
        devices = self.core.find(lambda r: r.isTypeof('resources/RFLinkNode'))
        
        now = datetime.datetime.utcnow()
        
        for device in devices:
            if device.lastSeenDate and now - device.lastSeenDate > datetime.timedelta(seconds=1800):
                device.setConnectState(False)
    

class RFLinkSerialController(TransportProcess):
    RESET_ATTR = ['port', 'baudrate']

    def __init__(self, gateway):
        super(RFLinkSerialController, self).__init__(
            'rflink.%s' % gateway.id,
            transport = SerialTransport(
                port = gateway.port,
                baudrate = gateway.baudrate
            ),

            protocol = RFLinkProtocol(gateway)
        )
        self.gateway = gateway

    def send(self, *args, **kwargs):
        self.protocol.send(*args, **kwargs)



