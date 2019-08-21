# coding: utf-8

from zeroconf import ServiceBrowser, Zeroconf
from ..utils.weak_ref import proxy_method, LostReferenceException
import logging
from future.utils import binary_type


LOGGER = logging.getLogger('mdns')


__all__ = ['register_service', 'unregister_service']


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


def register_service(service_name, callback):
    _service_handlers.setdefault(service_name, set())
    _service_handlers[service_name].add(proxy_method(callback))
    _update(service_name)


def unregister_service(service_name, callback=None):
    if service_name in _service_handlers:
        if callback is None:
            _service_handlers.pop(service_name)
        else:
            try:
                _service_handlers[service_name].remove(callback)
            except KeyError:
                pass
        _update(service_name)


def _update(service_name):
    browser = _browsers.get(service_name)
    has_handlers = (service_name in _service_handlers) and _service_handlers[service_name]

    if browser and not has_handlers:
        # stop the service
        LOGGER.debug('[%s] stop service', service_name)
        _browsers.pop(service_name)
        browser.cancel()
        _zc_update()
        return

    if not browser and has_handlers:
        # start the service
        LOGGER.debug('[%s] start service', service_name)
        zeroconf = _zc()
        browser = ServiceBrowser(zeroconf, service_name, ServiceListener(service_name))
        _browsers[service_name] = browser
        return


class ServiceListener:

    def __init__(self, service_name):
        self._service_name = service_name

    @property
    def service_name(self):
        return self._service_name

    @property
    def handlers(self):
        _hs = _service_handlers.get(self._service_name)
        if _hs:
            return _hs
        return []

    def _run_handlers(self, *args, **kwargs):
        need_update = False

        for h in self.handlers:
            try:
                h(*args, **kwargs)
            except LostReferenceException:
                need_update = True
            except:
                LOGGER.exception('[%s] exception in handler %s', self.service_name, h)

        if need_update:
            _update(self.service_name)


    def remove_service(self, zeroconf, type, name):
        #
        LOGGER.info("Service %s removed" % (name,))

        info = dict()
        info.setdefault('type', type)
        info.setdefault('name', name)

        self._run_handlers(False, info)


    def add_service(self, zeroconf, type, name):
        # Service LIVEBOX._http._tcp.local. added, service info: ServiceInfo(type='_http._tcp.local.', name='LIVEBOX._http._tcp.local.', addresses=[b'\xc0\xa8\x01\x01'], port=80, weight=0, priority=0, server='LIVEBOX.local.', properties={})
        info = zeroconf.get_service_info(type, name)
        LOGGER.info("Service %s added, service info: %s" % (name, info))

        if info is None:
            info = dict()
            info.setdefault('type', type)
            info.setdefault('name', name)
        else:
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

            info = _info

        self._run_handlers(True, info)


