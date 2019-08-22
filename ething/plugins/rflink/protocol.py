# coding: utf-8
from .RFLinkSwitch import RFLinkSwitch
from .RFLinkGenericSensor import RFLinkGenericSensor
from ething.TransportProcess import LineReader
from ething.scheduler import set_interval, unbind
from .helpers import parse_incoming_data, is_protocol, Result
import time
import re
import logging


LOGGER = logging.getLogger(__name__)


class RFLinkProtocol(LineReader):

    RESPONSE_TIMEOUT = 10  # seconds

    def __init__(self, gateway):
        super(RFLinkProtocol, self).__init__()
        self.gateway = gateway
        self.core = gateway.core
        # response management
        self._responseListeners = []

    def connection_made(self):
        super(RFLinkProtocol, self).connection_made()
        self._responseListeners = []

        set_interval(1, self.check_response_timeout)

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
        LOGGER.debug('read: %s', line)

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
                    if r.typeof('resources/RFLinkNode') and r.nodeId == data['ID'] and r.protocol == protocol and r.createdBy == self:
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
                            LOGGER.warning("fail to create the node from %s" % (line))

                if device:
                    with device:
                        device.refresh_connect_state(True)
                        device._handle_incoming_data(protocol, data)

        else:

            matches = re.search(
                'Nodo RadioFrequencyLink - RFLink Gateway V([\d\.]+) - R([\d]+)', parts[2])
            if matches:
                with gateway:
                    gateway.version = matches.group(1)
                    gateway.revision = matches.group(2)
                LOGGER.info("RFLink: ver:%s rev:%s" %
                              (matches.group(1), matches.group(2)))
            else:
                matches = re.search(
                    ';VER=([\d\.]+);REV=([\d]+);BUILD=([0-9a-fA-F]+);', line)
                if matches:
                    with gateway:
                        gateway.version = matches.group(1)
                        gateway.revision = matches.group(2)
                        gateway.build = matches.group(3)
                    LOGGER.info("RFLink: ver:%s rev:%s build:%s" % (
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
            return self.core.create(RFLinkSwitch, attributes)

        # try to generate a generic sensor
        interfaces = list()

        if 'TEMP' in data:
            interfaces.append('interfaces/Thermometer')
        if 'HUM' in data:
            interfaces.append('interfaces/HumiditySensor')
        if 'BARO' in data:
            interfaces.append('interfaces/PressureSensor')

        if len(interfaces) > 0:
            return self.core.create(RFLinkGenericSensor.create_dynamic_class(*interfaces), attributes)


    # $message message to send
    # $callback (optional) function(error, messageSent, messageReceived = None)
    # $waitResponse (optional) true|false wait for a response or not
    def send(self, message, done = None, err = None, response = None):

        LOGGER.debug("RFLink: send message '%s'", message)

        result = Result(response, message, done = done, err = err)

        self.write_line(message)

        if not response:
            result.resolve()
        else :
            self._responseListeners.append(result)

        return result

    def connection_lost(self, exc):

        unbind(self.check_response_timeout)

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
    



