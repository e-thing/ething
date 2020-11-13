# coding: utf-8

from zeroconf import ServiceBrowser, Zeroconf, ZeroconfServiceTypes, ServiceListener
import weakref
import inspect
import logging
from future.utils import binary_type
from .scanner import *
import time


LOGGER = logging.getLogger(__name__)


__all__ = ['register_service']


_service_handlers = dict()
_browsers = dict()
_zc_instance = None


def _zc():
    global _zc_instance
    if _zc_instance is None:
        LOGGER.debug('start Zeroconf service')
        _zc_instance = Zeroconf()
    return _zc_instance


def _zc_update():
    global _zc_instance
    if _zc_instance is not None:
        if len(_browsers) == 0:
            # no more registered services
            LOGGER.debug('stop Zeroconf service')
            _zc_instance.close()
            _zc_instance = None


def register_service(service_name, callback, device_name=None):
    _service_handlers.setdefault(service_name, set())
    if inspect.ismethod(callback):
        callback = weakref.WeakMethod(callback)
    _service_handlers[service_name].add((callback, device_name))
    _update(service_name)


def _update(service_name):
    browser = _browsers.get(service_name)
    has_handlers = (service_name in _service_handlers) and len(_service_handlers[service_name]) > 0

    if browser and not has_handlers:
        # stop the service
        LOGGER.debug('[%s] stop service', service_name)
        _browsers.pop(service_name)
        browser.cancel()
        _zc_update()
        return

    if not browser and has_handlers:
        # start the service
        zeroconf = _zc()
        LOGGER.debug('[%s] start service', service_name)
        browser = ServiceBrowser(zeroconf, service_name, MdnsServiceListener(service_name))
        _browsers[service_name] = browser
        return


def _convert_service_info(info):
    _info = dict()

    for name in (
            'type',
            'name',
            'port',
            'weight',
            'priority',
            'server',
    ):
        _info[name] = getattr(info, name, None)

    try:
        address = info.addresses[0]
    except IndexError:
        address = None

    if isinstance(address, binary_type):
        address = '.'.join(map(str, address))

    _info['address'] = address

    properties = info.properties
    for name in properties:
        val = properties[name]
        name = name.decode('utf8')
        if name not in _info:
            if isinstance(val, binary_type):
                val = val.decode('utf8')
            _info[name] = val

    return _info

class MdnsServiceListener(ServiceListener):

    def __init__(self, service_name):
        self._service_name = service_name

    @property
    def service_name(self):
        return self._service_name

    def _run_handlers(self, is_alive, info):
        need_update = False
        handlers_items = _service_handlers.get(self._service_name, [])

        for item in list(handlers_items):
            h, dev_name = item
            if isinstance(h, weakref.WeakMethod):
                h = h()
                if h is None: # lost reference
                    handlers_items.remove(item)
                    need_update = True
                    continue
            if dev_name and not info['name'].startswith(dev_name):
                continue
            try:
                h(is_alive, info)
            except:
                LOGGER.exception('[%s] exception in handler %s', self.service_name, h)

        if need_update:
            _update(self.service_name)

    def remove_service(self, zeroconf, type, name):
        #
        LOGGER.debug("Service %s removed" % (name,))

        info = dict()
        info.setdefault('type', type)
        info.setdefault('name', name)

        self._run_handlers(False, info)


    def add_service(self, zeroconf, type, name):
        info = zeroconf.get_service_info(type, name)
        LOGGER.debug("Service %s added, service info: %s" % (name, info))

        if info is None:
            info = dict()
            info.setdefault('type', type)
            info.setdefault('name', name)
        else:
            info = _convert_service_info(info)

        self._run_handlers(True, info)

    def update_service(self, zeroconf, type, name):
        pass


class MdnsScanner(Scanner):

    def scan(self, timeout):
        zc = _zc()
        services = ZeroconfServiceTypes.find(zc, timeout=5)

        browsers = [ServiceBrowser(zc, sevice, self) for sevice in services]

        time.sleep(timeout - 5)

        for b in browsers:
            b.cancel()

        _zc_update()

    def remove_service(self, zeroconf, type, name):
        pass

    def add_service(self, zeroconf, type, name):
        info = zeroconf.get_service_info(type, name)
        info = _convert_service_info(info)
        self.results.put(NetScannerResult(info.get('address'), info))
