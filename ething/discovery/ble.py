# coding: utf-8
import logging
from future.utils import integer_types

LOGGER = logging.getLogger(__name__)

try:
    from bluepy.btle import Scanner as _Scanner, DefaultDelegate, BTLEException
except Exception as e:
    bluepy_imported = False
else:
    bluepy_imported = True


if bluepy_imported:

    from queue import Queue, Empty
    from .scanner import *
    from ..utils.bluetooth import list_bluetooth_interfaces
    import gevent


    def _device_to_dict(dev):
        ret = {
            'mac': dev.addr.upper(),
            'connectable': dev.connectable,
            'addrType': dev.addrType,
            'iface': dev.iface,
        }

        for (sdid, desc, value) in dev.getScanData():
            ret['data-0x%X' % sdid] = '%s = %s' % (desc, value)

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
            ifaces = set()
            for iface_info in list_bluetooth_interfaces():
                iface = iface_info['hci']
                if not isinstance(iface, integer_types):
                    if iface.startswith('hci'):
                        iface = iface[3:]
                    try:
                        iface = int(iface)
                    except ValueError:
                        continue
                ifaces.add(iface)

            if len(ifaces) > 0:
                LOGGER.debug('bluetooth interfaces detected: %s', ifaces)

                delegate = ScanDelegateForScanner(self.results)

                scanners = [_Scanner(iface).withDelegate(delegate) for iface in ifaces]

                jobs = [gevent.spawn(scanner.scan, timeout=timeout) for scanner in scanners]
                gevent.joinall(jobs)
            else:
                LOGGER.debug('no bluetooth interface detected')

else:
    BleaScanner = None