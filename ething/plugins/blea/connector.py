# coding: utf-8

from bluepy import btle
import time
import struct

class Connector():
    def __init__(self, instance, type='public'):
        self.instance = instance
        self.mac = instance.mac
        self.type = type
        self.p = None
        self.isconnected = False
        self.iface = 0
        self.log = instance.ething.log
    
    def __enter__(self):
        self.connect()
        return self
    
    def __exit__(self, type, value, traceback):
        self.disconnect()
    
    def connect(self, retry=3, timeout=15):
        if self.p is None:
            
            self.log.debug('CONNECTOR------Connecting : '+str(self.mac) + ' with bluetooth ' + str(self.iface))
            i=0
            t0 = time.time()
            while timeout==0 or time.time() < t0 + timeout:
                i = i + 1
                try:
                    if self.type == 'public':
                        connection = btle.Peripheral(self.mac, iface=self.iface)
                    else:
                        connection = btle.Peripheral(self.mac, addrType = btle.ADDR_TYPE_RANDOM, iface=self.iface)
                    self.isconnected = True
                    break
                except Exception as e:
                    self.log.debug('CONNECTOR------'+str(e) + ' attempt ' + str(i) )
                    if i >= retry:
                        self.isconnected = False
                        self.disconnect()
                        self.log.debug('CONNECTOR------Issue connecting to : '+str(self.mac) + ' with bluetooth ' + str(self.iface) + ' the device is busy or too far')
                        break
                    time.sleep(1)
            if self.isconnected:
                self.p = connection
                self.log.debug('CONNECTOR------Connected... ' + str(self.mac))
                
        else:
            self.log.debug('CONNECTOR------already connected... ' + str(self.mac))
        
        return self.isconnected
    
    
    def disconnect(self):
        self.log.debug('CONNECTOR------Disconnecting... ' + str(self.mac))
        i=0
        while self.p:
            i = i + 1
            try:
                self.log.debug('CONNECTOR------ attempt ' + str(i) )
                self.p.disconnect()
                break
            except Exception as e:
                if i >= 2 or ('str' in str(e) and 'has no attribute' in str(e)):
                    break
        
        self.isconnected = False
        self.p = None
        self.log.debug('CONNECTOR------Disconnected...'+ str(self.mac))
    
    
    def readCharacteristic(self,handle):
        self.log.debug('CONNECTOR------Reading Characteristic...'+ str(self.mac))
        
        result = None
        
        if self.p:
            try:
                result = self.p.readCharacteristic(int(handle,16))
            except Exception as e:
                self.log.debug(str(e))
        
        return result
    
    def writeCharacteristic(self,handle,value,response=False):
        self.log.debug('CONNECTOR------Writing Characteristic... ' + str(self.mac))
        
        result = None
        
        if self.p:
            try:
                arrayValue = [int('0x'+value[i:i+2],16) for i in range(0, len(value), 2)]
                result = self.p.writeCharacteristic(int(handle,16),struct.pack('<%dB' % (len(arrayValue)), *arrayValue),response)
                return True
            except Exception as e:
                self.log.debug(str(e))
        
        return False
    
    
    def getCharacteristics(self,handle=None,handleend=None):
        self.log.debug('CONNECTOR------Getting Characteristics... ' + str(self.mac))
        
        if handleend is None:
            handleend = handle
        
        
        if self.p:
            try:
                if handle is None:
                    list = self.p.getCharacteristics()
                else:
                    list = self.p.getCharacteristics(int(handle,16), int(handleend,16)+4)
                return list
            except Exception as e:
                self.log.debug(str(e))
        
    
    def waitForNotifications(self, timeout=0):
        
        if self.p:
            self.p.withDelegate(NotificationDelegate(self))
            return self.p.waitForNotifications(timeout)
        
        return False
        
        
    
    def helper(self):
        self.log.debug('CONNECTOR------Helper for : ' + str(self.mac))
        characteristics = self.getCharacteristics()
        listtype=['x','c','b','B','?','h','H','i','I','l','L','q','Q','f','d','s','p','P']
        
        if characteristics:
            for char in characteristics:
                handle = str(hex(char.getHandle()))
                if char.supportsRead():
                    self.log.debug('CONNECTOR------'+handle + ' readable')
                else:
                    self.log.debug('CONNECTOR------'+handle + ' not readable (probably only writable)')
                if char.supportsRead():
                    try:
                        value = char.read()
                        found = False
                        for type in listtype:
                            for i in range(1,256):
                                try:
                                    self.log.debug('CONNECTOR------value for handle (decrypted with ' + type + ' lenght ' + str(i) +') : ' + handle + ' is : ' + str(struct.unpack(str(i)+type,value)))
                                    found = True
                                except:
                                    continue
                        self.log.debug('CONNECTOR------value for handle (undecrypted) : ' + handle + ' is : ' + value)
                    except Exception as e:
                        self.log.debug('CONNECTOR------unable to read value for handle (probably not readable) '+handle+ ' : '+str(e))
                        continue
        return


class NotificationDelegate(btle.DefaultDelegate):
    def __init__(self,connector):
        btle.DefaultDelegate.__init__(self)
        self.connector = connector

    def handleNotification(self, cHandle, data):
        self.connector.log.debug('Received Notification for ' + (self.connector.mac) + ' ' + self.connector.instance.name +' from handle ' +hex(cHandle) )
        self.connector.instance.handleNotification(self.connector,cHandle,data)
