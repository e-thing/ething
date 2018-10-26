# coding: utf-8
from .YeelightDevice import YeelightDevice
from .YeelightBulbRGBW import YeelightBulbRGBW
from ething.core.plugin import Plugin
from ething.core.TransportProcess import LineReader, TransportProcess, NetTransport, UdpTransport, Protocol
from ething.core.Scheduler import Scheduler
from . import yeelight
import time
import random
import json
import re


class Yeelight(Plugin):

    def load(self):
        super(Yeelight, self).load()

        self.controllers = {}

        gateways = self.core.find(lambda r: r.isTypeof('resources/YeelightDevice'))

        for gateway in gateways:
            try:
                self._start_controller(gateway)
            except Exception as e:
                self.log.exception('unable to start the controller for the device %s' % gateway)

        self.core.signalDispatcher.bind('ResourceCreated', self._on_resource_created)
        self.core.signalDispatcher.bind('ResourceDeleted', self._on_resource_deleted)
        self.core.signalDispatcher.bind('ResourceUpdated', self._on_resource_updated)

        self.advertisement_controller = AdvertisementController(self.core)
        self.advertisement_controller.start()

    def unload(self):
        super(Yeelight, self).unload()
        self.core.signalDispatcher.unbind('ResourceCreated', self._on_resource_created)
        self.core.signalDispatcher.unbind('ResourceDeleted', self._on_resource_deleted)
        self.core.signalDispatcher.unbind('ResourceUpdated', self._on_resource_updated)

        self.stop_all_controllers()

        if hasattr(self, 'advertisement_controller'):
            self.advertisement_controller.stop()
            del self.advertisement_controller

    def _on_resource_created(self, signal):
        device = signal.resource
        if isinstance(device, YeelightDevice):
            self._start_controller(device)

    def _on_resource_deleted(self, signal):
        device = signal.resource
        if isinstance(device, YeelightDevice):
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
        controller = Controller(device)
        self.controllers[device.id] = controller
        controller.start()

    def _stop_controller(self, id):

        if id in self.controllers:
            controller = self.controllers[id]
            controller.stop()
            del self.controllers[id]

    def stop_all_controllers(self):
        if hasattr(self, 'controllers'):
            for id in list(self.controllers):
                self._stop_controller(id)


class YeelightProtocol(LineReader):
    RESPONSE_TIMEOUT = 10  # seconds

    def __init__(self, gateway):
        super(YeelightProtocol, self).__init__(terminator = b'\r\n')
        self.gateway = gateway
        # response management
        self._pending_cmds = {}
        self.scheduler = Scheduler()

        self.scheduler.setInterval(0.5, self.check_response_timeout)

    def connection_made(self):
        super(YeelightProtocol, self).connection_made()
        self._pending_cmds.clear()
        self.gateway.setConnectState(True)
    
    def loop(self):
        self.scheduler.process()

    def handle_line(self, line):
        self.log.debug('read: %s' % line)

        try:
            # must be json
            message = json.loads(line)
        except Exception as e:
            # skip the line
            self.log.exception(
                "Yeelight: unable to handle the message %s" % line)
            return

        with self.gateway as device:

            device.setConnectState(True)

            if "id" in message:
                # result / response

                id = int(message["id"])

                if id in self._pending_cmds:
                    result = self._pending_cmds[id]
                    result.resolve(message, args = (device,))

                    del self._pending_cmds[id]

            elif ("method" in message) and ("params" in message):
                # notification

                method = message["method"]
                params = message["params"]

                if method == "props":
                    if params:
                        device._update(params)

                else:
                    raise Exception('unknown method %s' % str(method))

            else:
                raise Exception('unable to parse the message')


    def refresh(self):

        requestedProperties = [
            "power", "bright", "ct", "rgb", "hue", "sat",
            "color_mode", "flowing", "delayoff", "flow_params",
            "music_on", "name", "bg_power", "bg_flowing", "bg_flow_params",
            "bg_ct", "bg_lmode", "bg_bright", "bg_rgb", "bg_hue", "bg_sat", "nl_br"
        ]

        def done(result, device):
            if len(result.data) == len(requestedProperties):

                params = {}

                for i in range(len(requestedProperties)):
                    prop = requestedProperties[i]
                    value = result.data[i]
                    if i == '':
                        continue
                    params[prop.lower()] = value

                device._update(params)

        return self.send("get_prop", requestedProperties, done = done)

    def send(self, method, params = [], done = None, err = None):

        id = random.randint(1, 9999)

        command = {
            'id': id,
            'method': method,
            'params': params
        }

        result = yeelight.Result(command, done = done, err = err)

        if self.process.is_open:

            self.log.debug("message send %s" % str(command))

            self.write_line(json.dumps(command))

            self._pending_cmds[id] = result

        else:
            result.reject('not connected', args = (self.gateway,))

        return result


    def connection_lost(self, exc):

        self.gateway.setConnectState(False)

        for id in self._pending_cmds:
            self._pending_cmds[id].reject('disconnected', args = (self.gateway,))

        self._pending_cmds.clear()

        super(YeelightProtocol, self).connection_lost(exc)

    def check_response_timeout(self):
        # check for timeout !
        now = time.time()

        for id in list(self._pending_cmds):
            result = self._pending_cmds[id]

            if now - result.send_ts > self.RESPONSE_TIMEOUT:
                result.reject('response timeout', args = (self.gateway,))
                del self._pending_cmds[id]


class Controller(TransportProcess):
    RESET_ATTR = ['host']

    def __init__(self, gateway):
        super(Controller, self).__init__(
            'yeelight.%s' % gateway.id,
            transport=NetTransport(
                host=gateway.host,
                port=yeelight.PORT
            ),
            protocol=YeelightProtocol(gateway)
        )
        self.gateway = gateway

    def send(self, *args, **kwargs):
        return self.protocol.send(*args, **kwargs)



class YeelightAdvertisementProtocol(Protocol):

    def __init__(self, core):
        self.core = core

    def connection_made(self):
        self.search()

    def data_received(self, from_tupple):
        data, remote_ip_port = from_tupple

        data = data.decode('utf-8', 'replace')

        self.log.debug('rec %s : %s' % (remote_ip_port, data))

        if data[:15] == "HTTP/1.1 200 OK" or data[:17] == "NOTIFY * HTTP/1.1":

            dev_info = {
                'ip': remote_ip_port[0],
                'port': remote_ip_port[1]
            }

            for line in data.splitlines():

                matches = re.search('^([^:]+):\s*(.+)\s*$', line)
                if matches:
                    value = matches.group(2)
                    dev_info[matches.group(1).lower()] = value

            self.process_device_info(dev_info)

    def search(self):
        self.log.debug('search...')
        package = "M-SEARCH * HTTP/1.1\r\nST:wifi_bulb\r\nMAN:\"ssdp:discover\"\r\n"
        self.transport.write(package.encode('utf8'), (yeelight.MULTICAST_ADDRESS, yeelight.MULTICAST_PORT))

    def process_device_info(self, dev_info):

        self.log.debug('device info : %s' % (dev_info))

        id = dev_info.get('id')
        model = dev_info.get('model')

        device = self.core.findOne(lambda r: r.isTypeof('resources/YeelightDevice') and r._dev_id == id and r.model == model)

        if not device:
            self.log.debug('new device : id = %s, model = %s' % (id, model))

            attributes = {
                'dev_id': id,
                'model': model,
                'fw_ver': dev_info.get('fw_ver'),
                'name': dev_info.get('name', '').strip() or model,
                'host': dev_info.get('ip')
            }

            if model == "color":
                device = self.core.create('resources/YeelightBulbRGBW', attributes)

            if not device:
                self.log.warning('unable to create the device : id = %s, model = %s' % (id, model))

        if device:
            with device:
                device.setConnectState(True)
                device._update(dev_info)









class AdvertisementController(TransportProcess):

    def __init__(self, core):
        super(AdvertisementController, self).__init__(
            'yeelight.adv',
            transport=UdpTransport(
                host=yeelight.MULTICAST_ADDRESS,
                port=yeelight.MULTICAST_PORT
            ),
            protocol=YeelightAdvertisementProtocol(core),
            reconnect_delay=60
        )

    def search(self, *args, **kwargs):
        self.protocol.search(*args, **kwargs)






