# coding: utf-8
from ething.plugin import Plugin
from ething.Process import Process
from ething.Scheduler import Scheduler
from .BleaGateway import BleaGateway

import os
import time
import threading
from bluepy.btle import Scanner, DefaultDelegate, BTLEException

from .devices import devices


class Blea(Plugin):

    def load(self):

        self.controllers = {}

        gateways = self.core.find({
            'type': 'BleaGateway'
        })

        for gateway in gateways:
            try:
                self._start_controller(gateway)
            except Exception as e:
                self.log.exception('unable to start the controller for the device %s' % gateway)

        self.core.signalDispatcher.bind('ResourceCreated', self._on_resource_created)
        self.core.signalDispatcher.bind('ResourceDeleted', self._on_resource_deleted)
        self.core.signalDispatcher.bind('ResourceMetaUpdated', self._on_resource_updated)

    def unload(self):
        self.core.signalDispatcher.unbind('ResourceCreated', self._on_resource_created)
        self.core.signalDispatcher.unbind('ResourceDeleted', self._on_resource_deleted)
        self.core.signalDispatcher.unbind('ResourceMetaUpdated', self._on_resource_updated)

        self.stop_all_controllers()

    def _on_resource_created(self, signal):
        device = self.core.get(signal['resource'])
        if isinstance(device, BleaGateway):
            self._start_controller(device)

    def _on_resource_deleted(self, signal):
        device = self.core.get(signal['resource'])
        if isinstance(device, BleaGateway):
            self._stop_controller(device.id)

    def _on_resource_updated(self, signal):
        id = signal['resource']
        if id in self.controllers:
            controller = self.controllers[id]
            gateway = controller.gateway
            if signal['rModifiedDate'] > gateway.modifiedDate:
                gateway.refresh()

            for attr in signal['attributes']:
                if attr in controller.RESET_ATTR:
                    self._stop_controller(id)
                    self._start_controller(gateway)
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


class ScanDelegate(DefaultDelegate):

    def __init__(self, controller):
        DefaultDelegate.__init__(self)
        self.gateway = controller.gateway
        self.log = controller.log
        
    
    def handleDiscovery(self, dev, isNewDev, isNewData):
        
        if isNewDev or isNewData:
            
            self.log.debug("BLEA: new device mac=%s rssi=%ddb connectable=%s data=%s", dev.addr, dev.rssi, str(dev.connectable), dev.getScanData())
            
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
                if cls.isvalid(name,manuf):
                    cls.handleDiscovery(self.gateway, mac, data, name, rssi, connectable)
                    break
                    
class ReadThread(threading.Thread):

    def __init__(self, controller, device):
        super(ReadThread, self).__init__(name="ReadThread")
        self.daemon = True
        self.controller = controller
        self.device = device
        self.log = controller.log
    
    def run(self):
        with self.controller._lock:
            self.log.info("BLEA: start read thread for device %s" % self.device)
            self.device.read()
            self.log.info("BLEA: read thread terminated for device %s" % self.device)

class Controller(Process):
    RESET_ATTR = ['iface']

    def __init__(self, gateway):
        super(Controller, self).__init__('blea')
        self.gateway = gateway
        self.core = gateway.ething
        self._lock = threading.Lock()
        self.scheduler = Scheduler()
        self.tsreadmap = {}
        self._lock = threading.Lock()
        self.errcount = 0
        self.connected = False
        
        self.scheduler.setInterval(5, self._read, startInSec=30)

    def main(self):
        
        self.log.info("BLEA: connecting to hci%d" % self.gateway.iface)
        
        os.system('hciconfig hci%d up' % self.gateway.iface)
        
        scanner = Scanner(self.gateway.iface).withDelegate(ScanDelegate(self))
        
        scanner.clear()
        
        while not self.stopped():
            self.scheduler.process()
            
            with self._lock:
                try:
                    scanner.start()
                    scanner.process(3)
                    self._set_connect_state(True)
                    self.errcount = 0
                except BTLEException as e:
                    self._set_connect_state(False)
                    self.errcount += 1
                    self.log.exception("BLEA: scan thread exception")
                    
                    if self.errcount > 5:
                        break
                finally:
                    try:
                        scanner.stop()
                    except:
                        pass
            
            time.sleep(0.1)
            
    
    def _set_connect_state(self, connected):
        if self.connected != connected:
            self.gateway.setConnectState(connected)
        self.connected = connected
    
    def _read(self):
        if self.connected:
            devices = self.core.find({
                'extends': 'BleaDevice'
            })
            
            now = time.time()
            
            for device in devices:
                if hasattr(device, 'read'):
                    if (device.id not in self.tsreadmap) or now > self.tsreadmap[device.id] + device.readPeriod:
                        self.tsreadmap[device.id] = now
                        # launch it in a new thread since it takes some time
                        read_thread = ReadThread(self, device)
                        read_thread.start()
    

