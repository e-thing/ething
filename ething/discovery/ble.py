# coding: utf-8
import logging
import threading
import time


LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = 30 # sec

bluepy_imported = False


try:
    from bluepy.btle import Scanner as _Scanner, DefaultDelegate, BTLEException, BTLEManagementError
    bluepy_imported = True
except ImportError:
    LOGGER.error('BLE scanner is not available: bluepy is bot installed')


if bluepy_imported:

    from queue import Queue, Empty
    from .scanner import *
    from ..env import get_options


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
            self.mac_list = list()

        def reset(self):
            self.mac_list = list()

        def handleDiscovery(self, dev, isNewDev, isNewData):
            if dev.addr not in self.mac_list:
                self.mac_list.append(dev.addr)
                LOGGER.debug('discover device %s', dev.addr)
                info = _device_to_dict(dev)
                self.queue.put(BleaScannerResult(info.get('mac'), info))


    class BleaScanner(Scanner):

        def __init__(self):
            super(BleaScanner, self).__init__()
            self._scanner = _Scanner(int(get_options().get('ble_hci', 0))).withDelegate(ScanDelegateForScanner(self.results))

        def scan(self, timeout):
            self._scanner.delegate.reset()
            try:
                self._scanner.scan(timeout=timeout)
            except BTLEManagementError as e:
                LOGGER.exception(e)
                pass
            except BTLEException as e:
                LOGGER.exception(e)
                pass


    import psutil

    def check_bluepy_high_cpu_load():
        # at some moment, the process bluepy-helper get stuck in infinite loop causing high CPU load.
        # This bug is known, but no fix has been release now.
        # So this thread kill these process if necessary
        LOGGER.info('bluepy-helper high cpu load detection enabled')
        while True:
            for proc in psutil.process_iter(['name', 'cpu_percent']):
                if proc.name() == 'bluepy-helper':
                    if proc.cpu_percent(0.5) >= 60:
                        LOGGER.warning('bluepy-helper: high CPU load detected => kill')
                        proc.kill()
            time.sleep(60)

    _check_bluepy_high_cpu_load_thread = threading.Thread(target=check_bluepy_high_cpu_load, daemon=True)
    _check_bluepy_high_cpu_load_thread.start()

else:

    BleaScanner = None



_registered_callbacks = list()
_t = None
_t_pair = False
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
    # _update() # deprecated since pairing mode


# deprecated
# def _update():
#     global _t
#     if _t is None and len(_registered_callbacks) > 0 and BleaScanner is not None:
#         _t = threading.Thread(target=_run, daemon=True)
#         _t.start()


def start_pairing():
    global _t_pair
    if not _t_pair and BleaScanner is not None:
        _t_pair = True
        t = threading.Thread(target=_pair, daemon=True)
        t.start()


def stop_pairing():
    global _t_pair
    _t_pair = False


def _call_handlers(is_alive, info):
    for cb in _registered_callbacks:
        try:
            cb(is_alive, info)
        except:
            LOGGER.exception('exception in callback %s', cb)


def _pair():
    global _t_pair

    scanner = BleaScanner()
    devs = list()

    LOGGER.info('pairing... start')

    while _t_pair:
        scanner.scan(5)

        results = [res.data for res in scanner.get_results()]

        for data in results:
            mac = data.get('mac')

            # just connected ?
            for d in devs:
                if d.get('mac') == mac:
                    d.update(data)
                    break
            else:
                # appear
                LOGGER.info('device connected %s', data)
                devs.append(data)
                _call_handlers(True, data)

        time.sleep(5)

    LOGGER.info('pairing... stop')


# deprecated
def _run():
    scanner = BleaScanner()
    while True:
        scanner.scan(3)

        results = [res.data for res in scanner.get_results()]

        mac_list = [res['mac'] for res in results]

        # check for diconnected devices
        for d in list(_prev_devs):
            if d.get('mac') not in mac_list:
                # not found
                LOGGER.info('device disconnected %s', d)
                _call_handlers(False, d)
                _prev_devs.remove(d)

        for data in results:
            mac = data.get('mac')

            # just connected ?
            for d in _prev_devs:
                if d.get('mac') == mac:
                    d.update(data)
                    break
            else:
                # appear
                LOGGER.info('device connected %s', data)
                _prev_devs.append(data)

        for d in _prev_devs:
            _call_handlers(True, d)

        time.sleep(SCAN_INTERVAL)
