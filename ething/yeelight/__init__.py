# coding: utf-8
from .YeelightDevice import YeelightDevice
from .YeelightBulbRGBW import YeelightBulbRGBW
from ething.plugin import Plugin
from ething.TransportProcess import LineReader, TransportProcess, NetTransport
from ething.Scheduler import Scheduler
from . import yeelight
import time
import random
import json


class Yeelight(Plugin):

    def load(self):

        self.controllers = {}

        gateways = self.core.find({
            'type': {'$regex': '^Yeelight.*$'}
        })

        for gateway in gateways:
            try:
                self._start_controller(gateway)
            except Exception as e:
                self.log.exception('unable to start the controller for the device %s' % gateway)

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
        if isinstance(device, YeelightDevice):
            self._start_controller(device)

    def _on_resource_deleted(self, signal):
        device = self.core.get(signal['resource'])
        if isinstance(device, YeelightDevice):
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
        controller = Controller(device)
        self.controllers[device.id] = controller
        controller.start()

        self.core.rpc.register('process.%s.send' % device.id, controller.send, callback_name='callback')

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


class YeelightProtocol(LineReader):
    RESPONSE_TIMEOUT = 10  # seconds

    def __init__(self, gateway):
        super(YeelightProtocol, self).__init__(terminator = b'\n')
        self.gateway = gateway
        # response management
        self._responseListeners = []
        self.scheduler = Scheduler()

        self.scheduler.setInterval(0.5, self.check_response_timeout)

    def connection_made(self):
        super(YeelightProtocol, self).connection_made()
        self._responseListeners = []
        self.gateway.setConnectState(True)
    
    def loop(self):
        self.scheduler.process()

    def handle_line(self, line):
        self.log.debug('read: %s' % line)

        try:
            # must be json
            message = json.loads(line.decode('utf8'))
        except Exception as e:
            # skip the line
            self.log.exception(
                "Yeelight: unable to handle the message %s" % line)
            return

        with self.gateway as device:

            device.setConnectState(True)

            if "id" in message:

                responseId = int(message["id"])
                responseResult = message["result"] if "result" in message else [
                ]

                i = 0
                while i < len(self._responseListeners):
                    responseListener = self._responseListeners[i]

                    if responseListener['id'] == responseId:

                        # remove this item
                        self._responseListeners.pop(i)
                        i -= 1

                        if callable(responseListener['callback']):
                            responseListener['callback'](False, responseResult)

                        break

                    i += 1

            elif ("method" in message) and ("params" in message):
                # notification

                method = message["method"]
                params = message["params"]

                if method == "props":
                    if params:
                        device.storeData(params)

                else:
                    raise Exception('unknown method %s' % str(method))

            else:
                raise Exception('unable to parse the message')


    def refresh(self):

        device = self.gateway

        requestedProperties = [
            "power", "bright", "ct", "rgb", "hue", "sat",
            "color_mode", "flowing", "delayoff", "flow_params",
            "music_on", "name"
        ]

        def cb(error, messageSent, response):

            if not error and isinstance(response, list) and len(response) == len(requestedProperties):

                # some formatting
                for i in range(0, len(response)):
                    v = response[i]
                    try:
                        response[i] = int(response[i])
                    except ValueError:
                        pass

                params = dict(zip(requestedProperties, response))

                device.storeData(params)

        self.send({
            "method": "get_prop",
            "params": requestedProperties
        }, cb, True)



    def send(self, message, callback=None, waitResponse=None):
        """
         $message message to send
         $callback (optional) function($error, $messageSent, $messageReceived = null)
         $waitResponse (optional) true|false wait for a response or not
        """

        if self.process.is_open:

            message['id'] = random.randint(1, 9999)

            self.log.debug("Yeelight: message send %s" % str(message))

            self._lastActivity = time.time()

            self.write_line(json.dumps(message).encode('utf8'))

            if waitResponse:
                # wait for a response

                def cb(error, messageReceived):
                    if callable(callback):
                        callback(error, message, messageReceived)

                self._responseListeners.append({
                    'callback': cb,
                    'ts': time.time(),
                    'messageSent': message,
                    'id': message['id']
                })

            else:
                if callable(callback):
                    callback(False, message, None)

            return

        else:

            if callable(callback):
                callback('not connected', message, None)

            return

    def connection_lost(self, exc):

        self.gateway.setConnectState(False)

        for responseListener in self._responseListeners:
            responseListener['callback']('disconnected', None)
        self._responseListeners = []

        super(YeelightProtocol, self).connection_lost(exc)

    def check_response_timeout(self):
        # check for timeout !
        now = time.time()
        i = 0
        while i < len(self._responseListeners):
            responseListener = self._responseListeners[i]

            if now - responseListener['ts'] > Controller.RESPONSE_TIMEOUT:
                # remove this item
                self._responseListeners.pop(i)
                i -= 1

                responseListener['callback']('response timeout', None)

            i += 1


class Controller(TransportProcess):
    RESET_ATTR = ['host']

    def __init__(self, gateway):
        super(Controller, self).__init__(
            'yeelight',
            transport=NetTransport(
                host=gateway.host,
                port=yeelight.PORT
            ),
            protocol=YeelightProtocol(gateway)
        )
        self.gateway = gateway

    def send(self, *args, **kwargs):
        self.protocol.send(*args, **kwargs)



