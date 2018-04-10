# coding: utf-8

from future.utils import text_type, binary_type
from .helpers import convertSwitchId, getSubType
from .RFLinkNode import RFLinkNode
import re
import time


class Controller(object):
    
    AUTOCONNECT_PERIOD = 60; # seconds    
    RESPONSE_TIMEOUT = 10; # seconds    
    
    reset_attr = ['port', 'baudrate']
    
    def __init__ (self, gateway, transport):
        
        self._gateway = gateway
        self._ething = gateway.ething
        self._isOpened = False
        
        self._log = gateway.ething.log
        
        self._lastState = False
        self._lastAutoconnectLoop = 0
        self._preventFailConnectLog = 0
        
        # response management
        self._responseListeners = []
        
        # refresh the gateway each time the gateway properties changes
        self.ething.signalManager.bind('ResourceMetaUpdated', self.onResourceMetaUpdated)
        
        self.ething.scheduler.tick(self.update)
        
        self._transport = transport(self)
    
    
    def __del__(self):
        self.destroy()
    
    
    @property
    def gateway (self):
        return self._gateway
    
    @property
    def ething (self):
        return self._ething
    
    @property
    def log (self):
        return self._log
    
    @property
    def isOpened (self):
        return self._isOpened
    
    @property
    def transport (self):
        return self._transport
    
    def onResourceMetaUpdated(self, signal):
        if signal['resource'] == self.gateway.id and signal['rModifiedDate'] > self.gateway.modifiedDate:
            self.gateway.refresh()
            
            for attr in signal['attributes']:
                if attr in Controller.reset_attr:
                    self.restart()
                    break
    
    
    def restart(self):
        if self.isOpened:
            self.close()
            self.open()
    
    
    def destroy(self):
        self.close()
        self.ething.signalManager.unbind('ResourceMetaUpdated', self.onResourceMetaUpdated);
    
    def open (self):
        
        try:
            self.transport.open()
        except Exception as e:
            self.log.error(e)
            return False
        
        self._lastAutoconnectLoop = 0
        self.gateway.setConnectState(True)
        self._isOpened = True
        return True
    
    def close (self):
        
        self.transport.close()
        
        self._isOpened = False
        self.gateway.setConnectState(False)
        
        for responseListener in self._responseListeners:
            responseListener['callback']('disconnected', None);
        self._responseListeners = []
        
        return True
    
    

    # exemple of messages :
    #     20;00;Nodo RadioFrequencyLink - RFLink Gateway V1.1 - R46;
    #     20;01;MySensors=OFF;NO NRF24L01;
    #     20;02;setGPIO=ON;
    #     20;03;Cresta;ID=8301;WINDIR=0005;WINSP=0000;WINGS=0000;WINTMP=00c3;WINCHL=00c3;BAT=LOW;
    #     20;04;Cresta;ID=3001;TEMP=00b4;HUM=50;BAT=OK;
    #     20;05;Cresta;ID=2801;TEMP=00af;HUM=53;BAT=OK;
    #     20;06;NewKaku;ID=008440e6;SWITCH=1;CMD=OFF;
    #     20;02;VER=1.1;REV=46;BUILD=0c;
    
    def processLine (self, line):
        
        if isinstance(line, binary_type):
            line = line.decode('utf8')
        
        self.log.debug("RFLink: message received = %s" % line)
        
        with self.gateway as gateway:
            
            gateway.setConnectState(True)
            
            words = line.rstrip(';').split(';')
            wordsCount = len(words)
            
            if wordsCount<3:
                self.log.warn("RFLink: invalid message received '%s'" % line)
                return
            
            # keep only messages destined to the gateway
            if words[0] != "20":
                return
            
            
            if wordsCount == 3 or words[2][0:4] == 'VER=':
                # system command/response
                
                # does a user request wait for a response
                for responseListener in self._responseListeners:
                    responseListener['callback'](False, line);
                self._responseListeners = []
                
                matches = re.search('Nodo RadioFrequencyLink - RFLink Gateway V([\d\.]+) - R([\d]+)', words[2])
                if matches:
                    gateway._version = matches.group(1)
                    gateway._revision = matches.group(2)
                    self.log.info("RFLink: ver:%s rev:%s" % (matches.group(1), matches.group(2)))
                else:
                    matches = re.search(';VER=([\d\.]+);REV=([\d]+);BUILD=([0-9a-fA-F]+);', line)
                    if matches:
                        gateway._version = matches.group(1)
                        gateway._revision = matches.group(2)
                        gateway._build = matches.group(3)
                        self.log.info("RFLink: ver:%s rev:%s build:%s" % (matches.group(1), matches.group(2), matches.group(3)))
                    
                
                
            else:
                
                protocol = words[2]
                args = {}
                
                for i in range(3, wordsCount):
                    sepi = words[i].find('=')
                    if sepi >= 0:
                        # key value pair
                        key = words[i][0:sepi]
                        value = words[i][sepi+1:]
                        args[key] = value
                
                if 'ID' in args:
                    
                    switchId = convertSwitchId(args['SWITCH']) if 'SWITCH' in args else None
                    
                    device = gateway.getNode({
                        'nodeId' : args['ID'],
                        'protocol' : protocol,
                        'switchId' : switchId
                    })
                    
                    if not device:
                        if gateway.data.get('inclusion', False):
                            # the device does not exist !
                            
                            subType = getSubType(protocol, args)
                            
                            # find the best subType suited from the protocol and args
                            if subType:
                                
                                # create it !
                                device = RFLinkNode.createDeviceFromMessage(subType, protocol, args, gateway)
                                
                                if device:
                                    self.log.info("RFLink: new node (%s) from %s" % (subType, line))
                                else:
                                    self.log.error("RFLink: fail to create the node (%s) from %s" % (subType, line))
                                
                            else:
                                self.log.warn("RFLink: unable to handle the message %s" % line)
                            
                        else:
                            self.log.warn("RFLink: new node from %s, rejected because inclusion=False" % line)
                    
                    if device:
                        with device:
                            device.setConnectState(True)
                            device.processMessage(protocol, args)
                    
                
                else:
                    self.log.warn("RFLink: unable to handle the message %s, no id." % line)
            
            
        
        
    
    
    
    def update (self):
        # do some stuff regularly
        now = time.time()
        
        # check for a deconnection
        if not self.isOpened and self.isOpened != self._lastState:
            self.log.info("RFLink: disconnected")
        self._lastState = self.isOpened
        
        # autoconnect
        if not self.isOpened and (now - self._lastAutoconnectLoop) > Controller.AUTOCONNECT_PERIOD:
            try:
                self._lastAutoconnectLoop = now
                self.open()
                self._preventFailConnectLog = 0
            except Exception as e:
                
                if self._preventFailConnectLog % 20 == 0:
                    self.log.warn("RFLink: unable to connect : %s" % str(e))
                self._preventFailConnectLog += 1
        
        # check for timeout !
        i = 0
        while i < len(self._responseListeners):
            responseListener = self._responseListeners[i]
            
            if now - responseListener['ts'] > Controller.RESPONSE_TIMEOUT:
                
                # remove this item
                self._responseListeners.pop(i)
                i -= 1
                
                responseListener['callback']('response timeout', None)
            
            i += 1
            
    
    
    
    
    # $message message to send
    # $callback (optional) function(error, messageSent, messageReceived = None)
    # $waitResponse (optional) true|false wait for a response or not
    def send (self, message, callback = None, waitResponse = False):
        
        if isinstance(message, text_type):
            message = message.encode('utf-8')
        
        self.log.debug("RFLink: send message '%s'" % message)
        
        if not self.isOpened:
            self.log.warn("RFLink: unable to send message : not connected")
            if callable(callback):
                callback('not connected', message, None)
            return 0
        
        
        
        wb =  self.transport.write(message+b"\r\n")
        
        if waitResponse:
            
            def cb(error, messageReceived):
                if callable(callback):
                    callback(error, message, messageReceived)
            
            # wait for a response
            self._responseListeners.append({
                'callback' : cb,
                'ts' : time.time(),
                'messageSent' : message
            })
            
        else:
            if callable(callback):
                callback(False, message, None)
        
        return wb
    
        
    



