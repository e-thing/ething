# coding: utf-8
from future.utils import string_types
from .MihomeGateway import MihomeGateway
from .MihomeSensorHT import MihomeSensorHT
from ething.core.plugin import Plugin
from ething.core.TransportProcess import Protocol, TransportProcess, UdpTransport
from ething.core.Scheduler import Scheduler
from .helpers import *
import time
import re
import datetime


class Mihome(Plugin):

    def load(self):
        super(Mihome, self).load()
        self._start_controller()

    def unload(self):
        super(Mihome, self).unload()
        self._stop_controller()

    def _start_controller(self):
        self.controller = Controller(self.core)
        self.controller.start()

    def _stop_controller(self):
        if hasattr(self, 'controller'):
            self.controller.stop()
            del self.controller


class MihomeProtocol(Protocol):
    RESPONSE_TIMEOUT = 10  # seconds
    ACTIVITY_TIMEOUT = 3600  # 1 hour

    def __init__(self, core):
        super(MihomeProtocol, self).__init__()
        self.core = core
        self.scheduler = Scheduler()

        # response management
        self._responseListeners = []

        self.scheduler.setInterval(1, self.check_timeout)
        self.scheduler.setInterval(60, self.check_disconnect)
    
    def loop(self):
        self.scheduler.process()

    def connection_made(self):
        super(MihomeProtocol, self).connection_made()
        self._responseListeners = []

        self.search()


    def data_received(self, from_tupple):
        data, addr = from_tupple

        self.log.debug("Mihome: receive data from %s : %s" % (str(addr), data))

        data = data.decode("utf-8")
        ip = addr[0]

        response = json.loads(data)

        if isinstance(response, dict):
            
            sid = response.get('sid')
            cmd = response.get('cmd')
            model = response.get('model')
            device = None

            #
            # 1 - retrieve the device from the sid
            #
            if sid:
                device = self.core.findOne(lambda r: r.isTypeof('resources/MihomeBase') and r.sid == sid)

                if not device and model is not None:
                    # try to create a new device from the incoming data !
                    # we only need sid and model.

                    attributes = {
                        'sid': sid,
                        'model': model,
                        'short_id': response.get('short_id', 0),
                        'name': model
                    }

                    if model == 'gateway':
                        # concerning a gateway
                        attributes.update({'ip': ip})
                        device = self.core.create('resources/MihomeGateway', attributes)

                    else:
                        # concerning a device

                        gateway = self.core.findOne(lambda r: r.isTypeof('resources/MihomeGateway') and r.ip == ip)

                        if gateway:

                            attributes.update({
                                'createdBy': gateway.id,
                            })

                            if model == 'sensor_ht' or model == 'weather.v1':
                                attributes.update({
                                    'createdBy': gateway.id,
                                })

                                device = self.core.create('resources/MihomeSensorHT', attributes)
                        else:
                            self.log.warning(
                                "Mihome: gateway not found with ip=%s" % (ip))

                    if not device:
                        self.log.error(
                            "Mihome: unable to create the device model: %s , sid:%s" % (model, sid))


                #
                # 2 - parse the packet
                #
                if device:
                    with device:
                        device.setConnectState(True)
                        device._processData(response)

                if '_ack' in cmd:

                    # response ?

                    i = 0
                    while i < len(self._responseListeners):
                        responseListener = self._responseListeners[i]

                        if responseListener.command.get('sid') == sid and responseListener.ack == cmd:

                            # remove this item
                            self._responseListeners.pop(i)
                            i -= 1

                            responseListener.resolve(response, args = (device, ))

                        i += 1

    def send(self, command, ip = None, port = None, done = None, ack = True, err = None):
        ip = ip or MULTICAST_ADDRESS
        port = port or MULTICAST_PORT

        if ack is True:
            ack = command.get('cmd', '') + '_ack'

        result = Result(ack, command=command, done=done, err=err)

        if self.process.is_open:

            self.log.debug("command send %s" % str(command))

            try:
                self.transport.write(json.dumps(command).encode("utf-8"), (ip, port))
            except:
                result.reject('send error')
            else:
                if ack:
                    self._responseListeners.append(result)
                else:
                    result.resolve()
        else:
            result.reject('not connected')

        return result

    def connection_lost(self, exc):

        for responseListener in self._responseListeners:
            responseListener.reject('disconnected')
        self._responseListeners = []

        super(MihomeProtocol, self).connection_lost(exc)

    def check_timeout(self):
        # check for timeout !
        now = time.time()

        i = 0
        while i < len(self._responseListeners):
            responseListener = self._responseListeners[i]

            if now - responseListener.send_ts > self.RESPONSE_TIMEOUT:
                # remove this item
                self._responseListeners.pop(i)
                i -= 1

                self.log.debug("command timeout for : %s" % str(responseListener.command.get('cmd')))

                responseListener.reject('response timeout')

            i += 1
    
    def check_disconnect(self):
        devices = self.core.find(lambda r: r.isTypeof('resources/MihomeDevice'))
        
        now = datetime.datetime.utcnow()
        
        for device in devices:
            if device.lastSeenDate and now - device.lastSeenDate > datetime.timedelta(seconds=self.ACTIVITY_TIMEOUT):
                device.setConnectState(False)

    def search(self):
        self.log.debug('search...')
        self.send({"cmd":"whois"}, port = SERVER_PORT, ack = False)


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



