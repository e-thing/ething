# coding: utf-8
from .RFLinkGateway import RFLinkGateway
from .RFLinkSerialGateway import RFLinkSerialGateway
from .RFLinkNode import RFLinkNode
from ething.plugin import Plugin
from ething.TransportProcess import LineReader, TransportProcess, SerialTransport
from ething.Scheduler import Scheduler
from .helpers import convertSwitchId, getSubType
import time
import re
import datetime


class RFLink(Plugin):

    def load(self):

        self.controllers = {}

        gateways = self.core.find({
            'type': {'$regex': '^RFLink.*Gateway$'}
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
        if isinstance(device, RFLinkGateway):
            self._start_controller(device)

    def _on_resource_deleted(self, signal):
        device = self.core.get(signal['resource'])
        if isinstance(device, RFLinkGateway):
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
        if isinstance(device, RFLinkSerialGateway):
            controller = RFLinkSerialController(device)
            self.controllers[device.id] = controller
            controller.start()
            
            self.core.rpc.register('process.%s.send' % device.id, controller.send, callback_name = 'callback')
        else:
            raise Exception('Unknown gateway type "%s"' % type(device).__name__)

    def _stop_controller(self, id):

        if id in self.controllers:
            controller = self.controllers[id]
            controller.stop()
            del self.controllers[id]
            self.core.rpc.unregister('process.%s.send' % id)

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

        with self.gateway as gateway:

            gateway.setConnectState(True)

            words = line.rstrip(';').split(';')
            wordsCount = len(words)

            if wordsCount < 3:
                self.log.warn("RFLink: invalid message received '%s'" % line)
                return

            # keep only messages destined to the gateway
            if words[0] != "20":
                return

            if wordsCount == 3 or words[2][0:4] == 'VER=':
                # system command/response

                # does a user request wait for a response
                for responseListener in self._responseListeners:
                    responseListener['callback'](False, line)
                self._responseListeners = []

                matches = re.search(
                    'Nodo RadioFrequencyLink - RFLink Gateway V([\d\.]+) - R([\d]+)', words[2])
                if matches:
                    gateway._version = matches.group(1)
                    gateway._revision = matches.group(2)
                    self.log.info("RFLink: ver:%s rev:%s" %
                                  (matches.group(1), matches.group(2)))
                else:
                    matches = re.search(
                        ';VER=([\d\.]+);REV=([\d]+);BUILD=([0-9a-fA-F]+);', line)
                    if matches:
                        gateway._version = matches.group(1)
                        gateway._revision = matches.group(2)
                        gateway._build = matches.group(3)
                        self.log.info("RFLink: ver:%s rev:%s build:%s" % (
                            matches.group(1), matches.group(2), matches.group(3)))

            else:

                protocol = words[2]
                args = {}

                for i in range(3, wordsCount):
                    sepi = words[i].find('=')
                    if sepi >= 0:
                        # key value pair
                        key = words[i][0:sepi]
                        value = words[i][sepi + 1:]
                        args[key] = value

                if 'ID' in args:

                    switchId = convertSwitchId(
                        args['SWITCH']) if 'SWITCH' in args else None

                    device = gateway.getNode({
                        'nodeId': args['ID'],
                        'protocol': protocol,
                        'switchId': switchId
                    })

                    if not device:
                        if gateway.data.get('inclusion', False):
                            # the device does not exist !

                            subType = getSubType(protocol, args)

                            # find the best subType suited from the protocol and args
                            if subType:

                                # create it !
                                device = RFLinkNode.createDeviceFromMessage(
                                    subType, protocol, args, gateway)

                                if device:
                                    self.log.info(
                                        "RFLink: new node (%s) from %s" % (subType, line))
                                else:
                                    self.log.error(
                                        "RFLink: fail to create the node (%s) from %s" % (subType, line))

                            else:
                                self.log.warn(
                                    "RFLink: unable to handle the message %s" % line)

                        else:
                            self.log.warn(
                                "RFLink: new node from %s, rejected because inclusion=False" % line)

                    if device:
                        with device:
                            device.setConnectState(True)
                            device.processMessage(protocol, args)

                else:
                    self.log.warn(
                        "RFLink: unable to handle the message %s, no id." % line)

    # $message message to send
    # $callback (optional) function(error, messageSent, messageReceived = None)
    # $waitResponse (optional) true|false wait for a response or not
    def send(self, message, callback=None, waitResponse=False):

        self.log.debug("RFLink: send message '%s'" % message)

        self.write_line(message)

        if waitResponse:

            def cb(error, messageReceived):
                if callable(callback):
                    callback(error, message, messageReceived)

            # wait for a response
            self._responseListeners.append({
                'callback': cb,
                'ts': time.time(),
                'messageSent': message
            })

        else:
            if callable(callback):
                callback(False, message, None)

    def connection_lost(self, exc):

        self.gateway.setConnectState(False)

        for responseListener in self._responseListeners:
            responseListener['callback']('disconnected', None)
        self._responseListeners = []

        super(RFLinkProtocol, self).connection_lost(exc)

    def check_response_timeout(self):
        # check for timeout !
        now = time.time()
        i = 0
        while i < len(self._responseListeners):
            responseListener = self._responseListeners[i]

            if now - responseListener['ts'] > self.RESPONSE_TIMEOUT:
                # remove this item
                self._responseListeners.pop(i)
                i -= 1

                responseListener['callback']('response timeout', None)

            i += 1
    
    def check_disconnect(self):
        devices = self.core.find({
            'extends': 'RFLinkNode',
            'subType': { '$in': ['thermometer', 'weatherStation', 'multimeter'] }
        })
        
        now = datetime.datetime.utcnow()
        
        for device in devices:
            if device.lastSeenDate and now - device.lastSeenDate > datetime.timedelta(seconds=1800):
                device.setConnectState(False)
    

class RFLinkSerialController(TransportProcess):
    RESET_ATTR = ['port', 'baudrate']

    def __init__(self, gateway):
        super(RFLinkSerialController, self).__init__(
            'rflink',
            transport = SerialTransport(
                port = gateway.port,
                baudrate = gateway.baudrate
            ),

            protocol = RFLinkProtocol(gateway)
        )
        self.gateway = gateway

    def send(self, *args, **kwargs):
        self.protocol.send(*args, **kwargs)



