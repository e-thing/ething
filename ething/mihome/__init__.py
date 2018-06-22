# coding: utf-8
from future.utils import iteritems, string_types
from .MihomeGateway import MihomeGateway
from .MihomeSensorHT import MihomeSensorHT
from ething.plugin import Plugin
from ething.TransportProcess import Protocol, TransportProcess, UdpTransport
from ething.Scheduler import Scheduler
from .helpers import *
import time
import re


class Mihome(Plugin):

    def load(self):
        self._start_controller()

    def unload(self):
        self._stop_controller()

    def _start_controller(self):
        self.controller = Controller(self.core)
        self.controller.start()
        self.core.rpc.register('mihome.send', self.controller.send, callback_name='callback')

    def _stop_controller(self):
        self.controller.stop()
        self.core.rpc.unregister('mihome.send')
        self.controller = None


class MihomeProtocol(Protocol):
    RESPONSE_TIMEOUT = 10  # seconds
    ACTIVITY_TIMEOUT = 3600  # 1 hour

    def __init__(self, core):
        super(MihomeProtocol, self).__init__()
        self.core = core
        self.scheduler = Scheduler()

        # response management
        self._responseListeners = []

        # activity management
        self._activities = {}

        self.scheduler.setInterval(0.5, self.check_timeout)

    def connection_made(self, process):
        super(MihomeProtocol, self).connection_made(process)
        self._responseListeners = []


    def data_received(self, from_tupple):
        data, addr = from_tupple

        self.log.debug("Mihome: receive data from %s : %s" % (str(addr), data))

        data = data.decode("utf-8")
        ip = addr[0]

        response = json.loads(data)
        response_data = json.loads(response.get('data', '{}'))

        if isinstance(response, dict):

            sid = response.get('sid')
            cmd = response.get('cmd')

            self._activities[sid] = time.time()

            if cmd == 'heartbeat' or cmd == 'report' or cmd == 'read_ack':

                """
                 {"cmd":"report","model":"gateway","sid":"34ce00fb61a9","short_id":0,"data":"{\"rgb\":0,\"illumination\":503}"}
                 {"cmd":"report","model":"weather.v1","sid":"158d0001a4b64a","short_id":22319,"data":"{\"temperature\":\"1983\"}"}
                 {"cmd":"report","model":"weather.v1","sid":"158d0001a4b64a","short_id":22319,"data":"{\"humidity\":\"3914\"}"}
                 {"cmd":"heartbeat","model":"gateway","sid":"34ce00fb61a9","short_id":"0","token":"JxtPXoxj2FmBrTqA","data":"{\"ip\":\"192.168.1.8\"}"}
                 {"cmd":"heartbeat","model":"sensor_magnet.aq2","sid":"158d0001d84e77","short_id":10731,"data":"{\"voltage\":2965,\"status\":\"close\"}"}
                """

                if response.get('model') == 'gateway':
                    # concerning a gateway

                    gatewayDevice = self.core.findOne({
                        'type': 'MihomeGateway',
                        'sid': sid
                    })

                    if not gatewayDevice:
                        ip = ip or response_data.get('ip')

                        if ip:
                            gatewayDevice = self.core.create('MihomeGateway', {
                                'name': 'gateway',
                                'sid': sid,
                                'ip': ip
                            })
                            if not gatewayDevice:
                                self.log.error(
                                    "Mihome: unable to create the gateway sid:%s" % sid)

                    if gatewayDevice:
                        with gatewayDevice:
                            gatewayDevice.setConnectState(True)
                            gatewayDevice.processData(response)

                else:
                    # concerning a device

                    device = self.core.findOne({
                        'extends': 'MihomeDevice',
                        'sid': sid
                    })

                    if not device:

                        model = response.get('model')

                        if model == 'sensor_ht' or model == 'weather.v1':
                            device = self.core.create('MihomeSensorHT', {
                                'name': 'thermometer',
                                'sid': sid
                            })

                        if not device:
                            self.log.error(
                                "Mihome: unable to create the device model: %s , sid:%s" % (model, sid))

                    if device:
                        with device:
                            device.setConnectState(True)
                            device.processData(response)

            elif cmd == 'write_ack':
                pass
            else:
                self.log.warn("Mihome: received unk command %s" % cmd)

            if cmd in ['read_ack', 'write_ack', 'get_id_list_ack']:

                # response ?

                i = 0
                while i < len(self._responseListeners):
                    responseListener = self._responseListeners[i]

                    if responseListener['sid'] == sid and responseListener['ack'] == cmd:

                        # remove this item
                        self._responseListeners.pop(i)
                        i -= 1

                        if callable(responseListener['callback']):
                            responseListener['callback'](
                                False, responseListener['command'], response)

                    i += 1

    def send(self, gateway, command, callback=None):

        if isinstance(gateway, string_types):
            gateway = self.core.get(gateway)

        if command.get('cmd') == 'write' and isinstance(command.get('data'), dict):
            command['data']['key'] = gateway.getGatewayKey()

        return self.sendCommand(command, callback, gateway.ip)

    def sendCommand(self, command, callback=None, addr=MULTICAST_ADDRESS):
        commandStr = json.dumps(command).encode("utf-8")

        if self.process.is_open:

            self.log.debug("Mihome: send data to %s : %s" % (addr, commandStr))

            try:
                self.transport.write(commandStr, (addr, MULTICAST_PORT))
            except:
                if callable(callback):
                    callback('send error', command, None)
            else:
                if callable(callback):
                    cmd = command.get('cmd')
                    sid = command.get('sid')

                    self._responseListeners.append({
                        'callback': callback,
                        'ts': time.time(),
                        'sid': sid,
                        'ack': cmd + '_ack',
                        'command': command
                    })

        else:
            if callable(callback):
                callback('not connected', command, None)

    def connection_lost(self, exc):

        for responseListener in self._responseListeners:
            responseListener['callback']('disconnected', None)
        self._responseListeners = []

        super(MihomeProtocol, self).connection_lost(exc)

    def check_timeout(self):
        # check for timeout !
        now = time.time()

        i = 0
        while i < len(self._responseListeners):
            responseListener = self._responseListeners[i]

            if now - responseListener['ts'] > self.RESPONSE_TIMEOUT:
                # remove this item
                self._responseListeners.pop(i)
                i -= 1

                responseListener['callback'](
                    'response timeout', responseListener['command'], None)

            i += 1

        # _activities check
        for sid, lastActivity in iteritems(self._activities):
            if now - lastActivity > self.ACTIVITY_TIMEOUT:

                # remove this item
                del self._activities[sid]

                device = self.core.findOne({
                    'sid': sid
                })

                if device:
                    device.setConnectState(False)


class Controller(TransportProcess):

    def __init__(self, core):
        super(Controller, self).__init__(
            'mihome',
            transport=UdpTransport(
                host=MULTICAST_ADDRESS,
                port=MULTICAST_PORT
            ),

            protocol=MihomeProtocol(core)
        )

    def send(self, *args, **kwargs):
        self.protocol.send(*args, **kwargs)



