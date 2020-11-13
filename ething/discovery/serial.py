from serial.tools.list_ports import comports
import logging
import threading
import time
from .scanner import *


SCAN_INTERVAL = 30 # sec

LOGGER = logging.getLogger(__name__)


port_attr_list = [
    'device',
    'name',
    'description',
    'hwid',
    'vid',
    'pid',
    'serial_number',
    'location',
    'manufacturer',
    'product',
    'interface',
]


_prev_ports = list()
_reg_items = list()


def _call_handlers(is_alive, info):
    for cb, filter in _reg_items:

        for key, val in filter.items():
            if info[key] != val:
                break
        else:
            try:
                cb(is_alive, info)
            except:
                LOGGER.exception('exception in callback for device %s', info['device'])


def _port_info_to_dict(port):
    info = dict()
    for attr in port_attr_list:
        info[attr] = getattr(port, attr, None)
    return info


def scan ():
    global _prev_ports

    ports = comports()
    for p in ports:
        info = _port_info_to_dict(p)

        # just connected ?
        for _p in _prev_ports:
            if p.device == _p.device:
                break
        else:
            # appear
            LOGGER.debug('serial port connected %s', p['device'])
            _call_handlers(True, p)

    # check for diconnected devices
    for p in _prev_ports:
        for _p in ports:
            if p.device == _p.device:
                break
        else:
            # not found
            LOGGER.debug('serial port disconnected %s', p['device'])
            _call_handlers(False, p)

    _prev_ports = ports


def _run():
    while True:
        scan()
        time.sleep(SCAN_INTERVAL)


_t = None


def _update():
    global _t
    if _t is None and len(_reg_items) > 0:
        _t = threading.Thread(target=_run, daemon=True)
        _t.start()


def register(callback, **filter):
    _reg_items.append((callback, filter))
    _update()


class SerialScanner(Scanner):

    def scan(self, timeout):
        return [SerialScannerResult(p.device, _port_info_to_dict(p)) for p in comports()]

