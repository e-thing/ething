# coding: utf-8
import logging
import threading
import time


LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = 30 # sec

bluepy_imported = False


try:
    from bluepy.btle import Scanner as _Scanner, DefaultDelegate, BTLEException
    bluepy_imported = True
except ImportError:
    LOGGER.error('BLE scanner is not available: bluepy is bot installed')


if bluepy_imported:

    from queue import Queue, Empty
    from .scanner import *
    from ..env import get_option


    def _device_to_dict(dev):
        ret = {
            'mac': dev.addr.upper(),
            'connectable': dev.connectable,
            'addrType': dev.addrType,
            'iface': dev.iface,
            'rssi': dev.rssi
        }

        for (sdid, desc, value) in dev.getScanData():
            if sdid == 0x09:
                ret['name'] = value.strip()
            elif sdid == 0xFF:
                ret['manufacturer'] = value.strip()
            else:
                ret['data-0x%X' % sdid] = (desc, value)

        return ret


    class ScanDelegateForScanner(DefaultDelegate):

        def __init__(self, queue):
            DefaultDelegate.__init__(self)
            self.queue = queue

        def handleDiscovery(self, dev):
            LOGGER.debug('discover device %s', dev.addr)
            info = _device_to_dict(dev)
            self.queue.put(BleaScannerResult(info.get('mac'), info))


    class BleaScanner(Scanner):

        def scan(self, timeout):
            scanner = _Scanner(get_option('ble_hci', 0)).withDelegate(ScanDelegateForScanner(self.results))
            scanner.scan(timeout=timeout)

else:

    BleaScanner = None



_registered_callbacks = list()
_t = None
_prev_devs = list()


def register(callback):
    """

    def handler(is_alive, info):
        if is_alive:
            print('new device discovered')

    register(handler)

    :param callback: a callable (is_alive, info)
    """
    _registered_callbacks.append(callback)
    _update()


def _update():
    global _t
    if _t is None and len(_registered_callbacks) > 0 and BleaScanner is not None:
        _t = threading.Thread(target=_run, daemon=True)
        _t.start()


def _call_handlers(is_alive, info):
    for cb in _registered_callbacks:
        try:
            cb(is_alive, info)
        except:
            LOGGER.exception('exception in callback %s', cb)


def _run():
    while True:
        scanner = BleaScanner()
        scanner.scan(3)

        results = [res.data for res in scanner.get_results()]

        mac_list = [res['mac'] for res in results]

        # check for diconnected devices
        for d in list(_prev_devs):
            if d.get('mac') not in mac_list:
                # not found
                LOGGER.debug('device disconnected %s', d)
                _call_handlers(False, d)
                _prev_devs.remove(d)

        for data in results:
            mac = data.get('mac')

            mac_list.append(mac)

            # just connected ?
            for d in _prev_devs:
                if d.get('mac') == mac:
                    d.update(data)
                    break
            else:
                # appear
                LOGGER.debug('device connected %s', data)
                _prev_devs.append(data)

        for d in _prev_devs:
            _call_handlers(True, d)


        time.sleep(SCAN_INTERVAL)
