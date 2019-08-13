# coding: utf-8

import os
import time
import threading
import datetime
from collections import OrderedDict
try:
    from bluepy.btle import Scanner, DefaultDelegate, BTLEException
except Exception as e:
    bluepy_imported = False
    print("WARNING: unable to import the package 'bluepy' (https://github.com/IanHarvey/bluepy): %s" % str(e))
else:
    bluepy_imported = True


if bluepy_imported:

    _locks = {}
    _ifaces_initialized = []


    def get_lock(iface):
        if iface not in _locks:
            _locks[iface] = threading.Lock()
        return _locks[iface]


    def init_iface(iface, force=False):
        if force or (iface not in _ifaces_initialized):
            _ifaces_initialized.append(iface)
            os.system('hciconfig hci%d up' % iface)


    from ething.core.plugin import *
    from .BleaGateway import BleaGateway
    from .devices import devices


    @attr('scan_interval', label='scan interval', type=Integer(min=5), default=60, description="Seconds between each scan for new devices")
    class Blea(Plugin):

        def setup(self):
            self.core.scheduler.setInterval(self.scan_interval, self.scan, name="blea.scan")

        def scan(self):

            gateways = self.core.find(lambda r: r.isTypeof('resources/BleaGateway'))

            for gateway in gateways:

                iface = gateway.iface

                with get_lock(iface):

                    init_iface(iface)

                    self.log.debug("BLEA: start scan thread on hci%s" % iface)

                    scanner = Scanner(iface).withDelegate(ScanDelegate(gateway))

                    try:
                        scanner.clear()
                        scanner.start()
                        scanner.process(5)
                        gateway.refresh_connect_state(True)
                    except Exception:
                        gateway.refresh_connect_state(False)
                        self.log.exception("BLEA: scan exception")
                    finally:
                        try:
                            scanner.stop()
                        except:
                            pass


    class ScanDelegate(DefaultDelegate):

        def __init__(self, gateway):
            DefaultDelegate.__init__(self)
            self.gateway = gateway
            self.log = gateway.log


        def handleDiscovery(self, dev, isNewDev, isNewData):

            if isNewDev or isNewData:

                self.log.debug("[BLEA] device detected mac=%s rssi=%ddb connectable=%s data=%s", dev.addr, dev.rssi, str(dev.connectable), dev.getScanData())

                mac = dev.addr.upper()
                rssi = dev.rssi
                connectable = dev.connectable
                addrType = dev.addrType

                name = ''
                data =''
                manuf =''

                for (adtype, desc, value) in dev.getScanData():
                    if desc == 'Complete Local Name':
                        name = value.strip()
                    elif 'Service Data' in desc:
                        data = value.strip()
                    elif desc == 'Manufacturer':
                        manuf = value.strip()

                for cls in devices:
                    if hasattr(cls, 'isvalid') and cls.isvalid(name,mac,manuf):
                        cls.handleDiscovery(self.gateway, mac, data, name, rssi, connectable)
                        break
                else:
                    self.log.warning('[BLEA] unknown device: name=%s manuf=%s' % (name, manuf))

