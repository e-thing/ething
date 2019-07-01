# coding: utf-8
from ething.core.TransportProcess import LineReader, Protocol
from . import yeelight
import time
import random
import json
import re


class YeelightProtocol(LineReader):
    RESPONSE_TIMEOUT = 10  # seconds

    def __init__(self, device):
        super(YeelightProtocol, self).__init__(terminator = b'\r\n')
        self.device = device
        self.core = device.core
        # response management
        self._pending_cmds = {}

    def connection_made(self):
        super(YeelightProtocol, self).connection_made()
        self._pending_cmds.clear()
        self.device.connected = True

        self.core.scheduler.setInterval(1, self.check_response_timeout)

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

        with self.device as device:

            device.connected = True

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
            result.reject('not connected', args = (self.device,))

        return result


    def connection_lost(self, exc):

        self.core.scheduler.unbind(self.check_response_timeout)

        self.device.connected = False

        for id in self._pending_cmds:
            self._pending_cmds[id].reject('disconnected', args = (self.device,))

        self._pending_cmds.clear()

        super(YeelightProtocol, self).connection_lost(exc)

    def check_response_timeout(self):
        # check for timeout !
        now = time.time()

        for id in list(self._pending_cmds):
            result = self._pending_cmds[id]

            if now - result.send_ts > self.RESPONSE_TIMEOUT:
                result.reject('response timeout', args = (self.device,))
                del self._pending_cmds[id]




class YeelightAdvertisementProtocol(Protocol):

    def __init__(self, core):
        super(YeelightAdvertisementProtocol, self).__init__()
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

        device = self.core.findOne(lambda r: r.isTypeof('resources/YeelightDevice') and r.dev_id == id and r.model == model)

        if not device:
            self.log.debug('new device : id = %s, model = %s' % (id, model))

            support = dev_info.get('support', '').split()

            attributes = {
                'dev_id': id,
                'model': model,
                'fw_ver': dev_info.get('fw_ver'),
                'name': dev_info.get('name', '').strip() or model,
                'host': dev_info.get('ip'),
                '_support': support,
            }

            if model == "color":
                device = self.core.create('resources/YeelightBulbRGBW', attributes)
            elif model == "mono":
                device = self.core.create('resources/YeelightBulbMono', attributes)
            else:
                if ('set_hsv' in support) or ('set_rgb' in support):
                    device = self.core.create('resources/YeelightBulbRGBW', attributes)
                elif 'set_bright' in support:
                    device = self.core.create('resources/YeelightBulbMono', attributes)

            if not device:
                self.log.warning('unable to create the device : id = %s, model = %s' % (id, model))

        if device:
            with device:
                device.connected = True
                device._update(dev_info)

        return device







