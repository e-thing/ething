# coding: utf-8


import time
import threading
from bluepy.btle import Scanner, DefaultDelegate, BTLEException

from .devices import devices

class ScanDelegate(DefaultDelegate):

    def __init__(self, gateway):
        DefaultDelegate.__init__(self)
        self.gateway = gateway
        self.ething = gateway.ething
        self.log = gateway.ething.log
        
    
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
                    




class ScanThread(threading.Thread):

    def __init__(self, controller):
        super(ScanThread, self).__init__(name="ScanThread")
        self._stop_event = threading.Event()
        self.daemon = True
        self.controller = controller
        self.gateway = controller.gateway
        self.log = self.gateway.ething.log
    
    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()
    
    def terminate(self, timeout = 5):
        t0 = time.time()
        while self.is_alive() and (timeout==0 or time.time() < t0 + timeout):
            time.sleep(0.2)
        if self.is_alive():
            self.log.error("BLEA: unable to stop the thread '%s'" % self.name)
        return not self.is_alive()
    
    def run(self):
        
        self.log.info("BLEA: start scan thread")
        
        scanner = Scanner(self.gateway.iface).withDelegate(ScanDelegate(self.gateway))
        
        scanner.clear()
        
        errcount = 0
        
        while not self.stopped():
            self.controller.lock.acquire()
            self.log.info("BLEA: scanning...")
            try:
                scanner.start()
                scanner.process(3)
                errcount = 0
                scanner.stop()
            except BTLEException as e:
                errcount += 1
                self.log.exception("BLEA: scan thread exception")
                
                if errcount > 5:
                    break
            finally:
                self.controller.lock.release()
        
        self.log.info("BLEA: scan thread terminated")
        

class ReadThread(threading.Thread):

    def __init__(self, controller, device):
        super(ReadThread, self).__init__(name="ReadThread")
        self.daemon = True
        self.controller = controller
        self.device = device
        self.log = self.device.ething.log
    
    def run(self):
        
        self.controller.lock.acquire()
        
        try:
            self.log.info("BLEA: start read thread for device %s" % self.device)
            self.device.read()
            self.log.info("BLEA: read thread terminated for device %s" % self.device)
        finally:
            self.controller.lock.release()

class Controller(object):

    reset_attr = ['iface']

    def __init__(self, gateway):
        self._status = "closed"
        self._gateway = gateway
        self._ething = gateway.ething

        self._log = gateway.ething.log
        
        self._scan_thread = None
        
        self.tsread = None
        self.tsreadmap = {}
        
        self.lock = threading.Lock()

        # refresh the gateway each time the gateway properties changes
        self.ething.signalManager.bind('ResourceMetaUpdated', self.onResourceMetaUpdated)

        self.ething.scheduler.tick(self.update)

    @property
    def gateway(self):
        return self._gateway

    @property
    def ething(self):
        return self._ething

    @property
    def log(self):
        return self._log

    def onResourceMetaUpdated(self, signal):
        if signal['resource'] == self.gateway.id:

            self.gateway.refresh()

            for attr in signal['attributes']:
                if attr in self.reset_attr:
                    self.restart()
                    break
    
    def restart(self):
        self.close()
        self.open()
    
    def destroy(self):
        self.close()
        self.ething.signalManager.unbind(
            'ResourceMetaUpdated', self.onResourceMetaUpdated)

    def open(self):
        self.close()
        
        self._status = "opened"
        
        self.tsread = time.time() + 15
        
        self.log.info("BLEA: connecting to hci%d" % self.gateway.iface)
        
        self._scan_thread = ScanThread(self)
        
        self._scan_thread.start()
        
        return True

    def close(self):
        
        if self._scan_thread:
            self._scan_thread.terminate()
            self._scan_thread = None
        
        self._status = "closed"
        
    
    def read (self):
        
        self.tsread = time.time()
        
        if self._scan_thread and self._scan_thread.is_alive():
            
            devices = self.ething.find({
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
            
    
    def update(self):
        if self._status == "closed":
            self.open()
        
        elif self._status == 'opened':
            if time.time() > self.tsread + 5:
                self.read()
        
