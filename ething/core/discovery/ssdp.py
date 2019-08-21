# coding: utf-8
# see https://www.electricmonk.nl/log/2016/07/05/exploring-upnp-with-python/
import socket
import logging
import time
import threading
from future.utils import string_types
import requests
from xml.etree import ElementTree
from ..utils import etree_to_dict
from ..utils.weak_ref import proxy_method, LostReferenceException
from collections import Mapping


__all__ = [
    'register',
    'scan'
]


LOGGER = logging.getLogger('ssdp')


SCAN_INTERVAL = 30.


def scan(timeout = 3):

    devices = dict()

    msg = \
        b'M-SEARCH * HTTP/1.1\r\n' \
        b'HOST:239.255.255.250:1900\r\n' \
        b'ST:upnp:rootdevice\r\n' \
        b'MX:2\r\n' \
        b'MAN:"ssdp:discover"\r\n' \
        b'\r\n'

    # Set up UDP socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    s.settimeout(timeout)
    s.sendto(msg, ('239.255.255.250', 1900))

    try:
        while True:
            data, addr = s.recvfrom(65507)
            ip, port = addr
            LOGGER.debug('device found ip=%s, data=%s', ip, data)

            if ip not in devices:
                devices[ip] = SSDP_Device(ip)

            try:
                headers = parse_response(data)
            except UnicodeDecodeError:
                LOGGER.debug('Ignoring invalid unicode response from %s', ip)
                continue
            else:
                devices[ip].update(headers)


    except socket.timeout:
        pass

    return list(devices.values())


def parse_response(data):
    headers = dict()
    lines = data.decode('utf8').splitlines()

    if '200 OK' in lines[0]:
        for line in lines[1:]:
            parts = line.split(':', 1)
            if len(parts) == 2:
                name, value = parts
                headers[name.lower()] = value

    return headers


class SSDP_Device(Mapping):

    def __init__(self, ip):
        self.ip = ip
        self.data = {
            'ip': ip
        }
        self._desc_loc = None
        self._desc = None

    def __iter__(self):
        return iter(self.data)

    def __len__(self):
        return len(self.data)

    def __getitem__(self, key):
        return self.data[key]

    def update(self, data):
        if isinstance(data, SSDP_Device):
            self.data.update(data.data)
        else:
            self.data.update(data)

    @property
    def st(self):
        """Return ST value."""
        return self.data.get('st')

    @property
    def location(self):
        """Return Location value."""
        return self.data.get('location')

    @property
    def usn(self):
        return self.data.get('usn')

    @property
    def server(self):
        return self.data.get('server')

    def __eq__(self, other):
        if isinstance(other, SSDP_Device):
            return self.ip == other.ip
        elif isinstance(other, string_types):
            return self.ip == other
        else:
            return False

    @property
    def description(self):
        """Return the description from the uPnP location."""
        location = self.location

        if location is None:
            return dict()

        if self._desc_loc != location:

            desc = dict()

            # load
            try:
                xml = requests.get(location, timeout=5).text
                if not xml:
                    # Samsung Smart TV sometimes returns an empty document the
                    # first time. Retry once.
                    xml = requests.get(location, timeout=5).text

                tree = ElementTree.fromstring(xml)

                desc = etree_to_dict(tree).get('root', {})

            except requests.RequestException:
                LOGGER.debug("Error fetching description at %s", location)
            except ElementTree.ParseError:
                LOGGER.debug("Found malformed XML at %s", location)

            self._desc = desc
            self._desc_loc = location

        return self._desc

    def __repr__(self):
        return "<SSDP_Device {} {}>".format(self.location or '', self.st or '')

    def match_device_description(self, values):
        """Fetch description and matches against it.
        Values should only contain lowercase keys.
        """
        device = self.description.get('device')

        if device is None:
            return False

        return any(device.get(key) in val
                   if isinstance(val, list)
                   else val == device.get(key)
                   for key, val in values.items())


class SSDP_Service(object):

    def __init__(self, listener, autostart=True):
        self._running = False
        self._t = None
        self._devices = list()
        self._listener = listener
        if autostart:
            self.run()

    @property
    def devices(self):
        return self._devices

    def run(self):
        t = self._t

        if t is not None and t.isAlive():
            # already running
            return

        self._running = True
        t = threading.Thread(target=self._main, daemon=True)
        t.start()
        self._t = t

    def _scan(self):
        devices = scan()

        # update
        for d in devices:
            for _d in self._devices:
                if d.ip == _d.ip:
                    # devie already in the list
                    _d.update(d)
                    self.device_change(_d, 'update')
                    break
            else:
                # new device
                self._devices.append(d)
                self.device_change(d, 'add')

        # device not found ?
        for _d in list(self._devices):
            if _d not in devices:
                #  disconnected
                self._devices.remove(_d)
                self.device_change(_d, 'remove')

    def device_change(self, device, reason):
        args = (device, )
        if reason == 'add':
            self._listener.add_service(*args)
        elif reason == 'removed':
            if hasattr(self._listener, 'remove_service'):
                self._listener.remove_service(*args)
        elif reason == 'update':
            if hasattr(self._listener, 'update_service'):
                self._listener.update_service(*args)

    def _main(self):
        while self._running:
            self._scan()
            # wait until next scan
            t0 = time.time()
            while self._running and time.time() - t0 < SCAN_INTERVAL:
                time.sleep(1)

    def close(self):
        self._running = False
        if self._t is not None:
            self._t.join()
            self._t = None


_registered_items = list()
_ssdp_service = None


def register(filter, callback):
    """

    def handler(is_alive, info):
        if is_alive:
            print('new device discovered')

    register({
        'st': 'roku:ecp',
        'manufacturer': 'roku',
        'deviceType': 'urn:roku-com:device:player:1-0'
    }, handler)

    :param filter: a dictionary that describe a filter
    :param callback: a callable (is_alive, info) => bool
    """
    _registered_items.append((filter, proxy_method(callback)))
    _update()


class _SSDP_Listener(object):

    def add_service(self, device):
        for filter, handler in _registered_items:

            for key, value in filter.items():
                if device.data.get(key) == value:
                    self._run_handler(True, device, handler)
                    break
            else:
                if device.match_device_description(filter):
                    self._run_handler(True, device, handler)

    def remove_service(self, device):
        pass

    def _run_handler(self, is_alive, device, handler):
        try:
            handler(is_alive, device)
        except LostReferenceException:
            pass
        except:
            LOGGER.exception('[%s] exception in handler %s', device.ip, handler)


def _update():
    global _ssdp_service

    if _ssdp_service is None and len(_registered_items) > 0:
        # start service
        _ssdp_service = SSDP_Service(_SSDP_Listener())
