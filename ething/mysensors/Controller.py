# coding: utf-8

from future.utils import string_types, bord, iteritems
from .helpers import *
from .Message import Message
from ething.Helpers import dict_recursive_update
from ething.utils import NullContextManager
import time
import re
import random
import math
import binascii



def unpack(data, length = None):
    
    out = []
    
    if not isinstance(data, bytearray):
        data = bytearray(data, 'utf-8')
    
    l = length if length is not None else int(len(data)/2)
    
    for i in range(0,l):
        
        first = data[2*i]
        second = data[2*i+1]
        
        value = (first << 8) | second
        
        out.append(value)
    
    return out

def pack(*args):
    
    o = []
    
    for v in args:
        
        first = (v & 0xFF00) >> 8
        second = (v & 0x00FF)
        
        o.append(first)
        o.append(second)
    
    return bytearray(o).decode("utf-8")

    

class Controller(object):
    
    ACK_TIMEOUT = 5; # seconds (maybe float number)
    AUTOCONNECT_PERIOD = 15; # seconds
    PENDING_MESSAGE_TIMEOUT = 120; # seconds (maybe float number)
    FIRMWARE_BLOCK_SIZE = 16; # in bytes
    FIRMWARE_UPDATE_TIMEOUT = 40; # in seconds, let the time for the node to restart and install the new firmware
    RESPONSE_TIMEOUT = 10
    STREAM_TIMEOUT = 10; # in seconds, max allowed time between 2 blocks of data
    
    
    reset_attr = ['port', 'baudrate', 'address']
    
    def __init__ (self, gateway, transport):
                
        self._gateway = gateway
        self._ething = gateway.ething
        self._isOpened = False
        
        self._log = gateway.ething.log
        
        self._lastState = False
        self._lastAutoconnectLoop = 0
        self._preventFailConnectLog = 0
        
        self.gatewayReady = False
        self.gatewayLibVersion = False
        
        # ack management
        self._ackWaitingMessages = []
        
        # used for smartSleep
        self._pendingMessages = []
        
        # firmware
        self._pendingFirmware = {}
        
        # streams
        self._pendingStreams = {}
        
        # response management
        self._responseListeners = []
        
        # refresh the gateway each time the gateway properties changes
        self.ething.signalManager.bind('ResourceMetaUpdated', self.onResourceMetaUpdated)
        
        self.ething.scheduler.tick(self.update)
        
        self._transport = transport(self)
    
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
        if signal['resource'] == self.gateway.id :
            
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
        self.gateway.refresh()
        
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
        self.gateway.refresh()
        
        self.transport.close()
        
        self._isOpened = False
        self.gateway.setConnectState(False)
        
        for responseListener in self._responseListeners:
            responseListener['callback']('disconnected', None);
        self._responseListeners = []
        
        self.log.info("MySensors: closed")
        
        return True
    
    
    def createNode(self, nodeId):
        gateway = self.gateway
        
        node = self.ething.create('MySensorsNode', {
            'nodeId' : nodeId,
            'name' : '%s/node-%d' % (gateway.name, nodeId),
            'createdBy': gateway
        })
        
        if not node:
            raise Exception("fail to create the node nodeId=%d" % nodeId)
        
        self.log.info("MySensors: new node nodeId=%d" % nodeId)
        
        return node
    
    
    def createSensor(self, node, sensorId, sensorType = S_UNK):
        
        sensor = self.ething.create('MySensorsSensor', {
            'name' : ('%s/sensor-%d' % (node.name, sensorId)) if sensorType == S_UNK else sensorTypeToName(sensorType),
            'sensorId' : sensorId,
            'sensorType' : sensorType,
            'createdBy': node
        })
        
        if not sensor:
            raise Exception("fail to create the sensor nodeId=%d sensorId=%d sensorType=%s" % (node.nodeId,sensorId,sensorType))
        
        self.log.info("MySensors: new sensor nodeId=%d sensorId=%d sensorType=%s" % (node.nodeId,sensorId,sensorType))
        return sensor
    
    
    def processMessage (self, message):
        
        if not isinstance(message, Message):
            message = Message.parse(message)
        
        r = True
        
        self.log.debug("MySensors: message received %s" % str(message))
        
        self.gateway.refresh()
        
        with self.gateway as gateway:
            
            gateway.setConnectState(True)
            
            nodeId = message.nodeId
            sensorId = message.childSensorId
            node = None
            sensor = None
            
            # automatically create unknown node and sensor
            if nodeId > 0 and nodeId != BROADCAST_ADDRESS:
                node = gateway.getNode(nodeId)
                if not node:
                    node = self.createNode(nodeId)
            
            if node and sensorId >= 0 and sensorId != INTERNAL_CHILD:
                sensor = node.getSensor(sensorId)
                if not sensor:
                    sensor = self.createSensor(node, sensorId, message.subType if  message.messageType==PRESENTATION else S_UNK)
            
            
            if not node:
                node = NullContextManager()
            if not sensor:
                sensor = NullContextManager()
            
            with node, sensor:
                
                if node:
                    node.setConnectState(True)
                if sensor:
                    sensor.setConnectState(True)
                
                # is ack ?
                if message.ack == NO_ACK:

                    try:
                        
                        if message.messageType == PRESENTATION:
                            sensorType = message.subType
                            
                            # get sensor
                            if sensor:
                                sensor.sensorType = sensorType # update type
                                sensor.description = message.getValue()
                                
                            elif node:
                                # node internal sensor (id=0xFF)
                                # library version (node device)
                                node._libVersion = message.getValue()
                            
                        
                        elif message.messageType == SET:
                            
                            if sensor:
                                
                                self.log.debug("MySensors: set value nodeId=%d sensorId=%d valueType=%d value=%s" % (nodeId,sensorId,message.subType,message.payload) )
                                
                                datatype = valueTypeStr(message.subType)
                                
                                if datatype:
                                    
                                    sensor.setData(datatype, message.payload) # save the raw data payload. used internally for REQ response (see below)
                                    
                                    sensor.storeData(datatype, message.getValue())
                                    
                                else:
                                    self.log.warn("MySensors: unknown value subtype %d" % message.subType)
                                
                        
                        elif message.messageType == REQ:
                            
                            if sensor:
                                
                                datatype = valueTypeStr(message.subType)
                                
                                if datatype:
                                    value = sensor.getData(datatype)
                                    if value is not None:
                                        response = Message(nodeId, sensorId, SET, NO_ACK, message.subType, payload = value)
                                        self.send(response)
                                    else:
                                        # no value stored ! No response
                                        pass
                                    
                                else:
                                    self.log.warn("MySensors: unknown value subtype %d" % message.subType)
                                
                        
                        elif message.messageType == INTERNAL:
                                
                            if message.subType == I_GATEWAY_READY :
                                self.gatewayReady = True
                                self.log.info("info: gateway ready")
                            
                            elif message.subType == I_VERSION :
                                self.gatewayLibVersion = message.getValue()
                                gateway._libVersion = message.getValue()
                                self.log.info("MySensors: gateway version = %s" % self.gatewayLibVersion)
                            
                            elif message.subType == I_TIME :
                                # return current time
                                response = Message(message.nodeId, message.childSensorId, INTERNAL, NO_ACK, I_TIME, int(time.time()))
                                self.send(response)
                                
                            elif message.subType == I_CONFIG :
                                # return M (metric) or I (Imperial)
                                response = Message(message.nodeId, message.childSensorId, INTERNAL, NO_ACK, I_CONFIG, 'M' if gateway.isMetric else 'I')
                                self.send(response)
                                
                            elif message.subType == I_ID_REQUEST :
                                # get a free node id
                                
                                f = None
                                for i in range(1,255):
                                    if not gateway.getNode(i):
                                        f = i
                                        break
                                
                                if f is not None:
                                    response = Message(BROADCAST_ADDRESS, INTERNAL_CHILD, INTERNAL, NO_ACK, I_ID_RESPONSE, f)
                                    self.send(response)
                                else:
                                    raise Exception('No free id available')
                            
                            elif message.subType == I_SKETCH_NAME :
                                if node:
                                    sketchName = message.getValue() or ''
                                    node._sketchName = sketchName
                                    # if the default name has not been changed by the user, overwrite it with the sketch name
                                    if re.search('^.+/node-[0-9]+$',node.name) and sketchName:
                                        node.name = sketchName
                            
                            elif message.subType == I_SKETCH_VERSION :
                                if node :
                                    node._sketchVersion = message.getValue()
                                
                                
                            elif message.subType == I_BATTERY_LEVEL :
                                if node :
                                    batteryLevel = int(message.payload)
                                    if batteryLevel<0:
                                        batteryLevel = 0
                                    if batteryLevel>100:
                                        batteryLevel = 100
                                    node.battery = batteryLevel
                                
                                
                            
                            elif message.subType == I_HEARTBEAT_RESPONSE :
                                
                                # check if there are some pending messages in queue (smartSleep)
                                i=0
                                while i < len(self._pendingMessages):
                                    pendingMessage = self._pendingMessages[i]
                                    
                                    originalMessage = pendingMessage['message']
                                    
                                    if originalMessage.nodeId == message.nodeId:
                                    
                                        # remove this item
                                        self._pendingMessages.pop(i)
                                        i-=1
                                        
                                        self.send(originalMessage, smartSleep=False, callback=pendingMessage['callback'])
                                    
                                    i+=1
                                
                                
                            elif message.subType == I_LOG_MESSAGE :
                                self.log.info("MySensors: nodeId=%d sensorId=%d %s" % (message.nodeId,message.childSensorId,message.getValue()))
                            
                            else:
                                self.log.warn("MySensors: message not processed : %s" % str(message))
                            
                            
                        
                        elif message.messageType == STREAM:
                            
                            
                            if message.subType == ST_FIRMWARE_CONFIG_REQUEST :
                                """
                                the payload contains the folowing (encoded in hexadecimal):
                                    uint16_t type;                                //!< Type of config
                                    uint16_t version;                            //!< Version of config
                                    uint16_t blocks;                            //!< Number of blocks
                                    uint16_t crc;                                //!< CRC of block data
                                    uint16_t BLVersion;                            //!< Bootloader version
                                """
                                
                                parts = unpack(message.payload)
                                if len(parts)>=4:
                                    type, version, nbBlocks, crc = parts
                                    
                                    bootloaderVersion = parts[4] if len(parts)>4 else 0
                                    
                                    self.log.info("MySensors: FW CONFIG : nodeId=%d type=%04X version=%04X blocks=%d crc=%04X BLVersion=%04X" % (nodeId, type, version, nbBlocks, crc, bootloaderVersion))
                                    
                                    if node :
                                        node._firmware = {
                                            'type' : type,
                                            'version' : version,
                                            'blocks' : nbBlocks,
                                            'crc' : crc,
                                            'BLVersion' : bootloaderVersion
                                        }
                                    
                                    
                                    
                                    if nodeId in self._pendingFirmware:
                                        # a firware has been updated
                                        # this message is received after reboot
                                        
                                        # check if the installed firmware was the one updated
                                        firmwareInfo = self._pendingFirmware[nodeId]
                                        ok = firmwareInfo['type'] == type and firmwareInfo['version'] == version and firmwareInfo['blocks'] == blocks and firmwareInfo['crc'] == crc
                                        
                                        if ok:
                                            self.log.info("MySensors: FW updated successfully : nodeId=%d type=%04X version=%04X blocks=%d crc=%04X" % (nodeId, type, version, nbBlocks, crc))
                                        else:
                                            self.log.warn("MySensors: FW update ERROR : nodeId=%d" % nodeId)
                                        
                                        
                                        if callable(firmwareInfo['callback']) :
                                            firmwareInfo['callback']( False if ok else 'error in firmware update')
                                        
                                        del self._pendingFirmware[nodeId]
                                    
                                    
                                
                                
                            elif message.subType == ST_FIRMWARE_CONFIG_RESPONSE :
                                pass
                            elif message.subType == ST_FIRMWARE_REQUEST :
                                """
                                return a peace of the FIRMWARE
                                
                                receive :
                                uint16_t type;        //!< Type of config
                                uint16_t version;    //!< Version of config
                                uint16_t block;        //!< Block index
                                
                                send:
                                uint16_t type;                        //!< Type of config
                                uint16_t version;                    //!< Version of config
                                uint16_t block;                        //!< Block index
                                uint8_t data[FIRMWARE_BLOCK_SIZE];    //!< Block data
                                """
                                
                                if len(message.payload)>=6:
                                    
                                    type, version, iBlock = unpack(message.payload, 3)
                                    
                                    self.log.warn("MySensors: FW GET : nodeId=%d type=%04X version=%04X block=%d" % (nodeId, type, version, iBlock))
                                    
                                    if nodeId in self._pendingFirmware:
                                        
                                        chunk = self._pendingFirmware[nodeId]['firmware'][iBlock*Controller.FIRMWARE_BLOCK_SIZE:(iBlock+1)*Controller.FIRMWARE_BLOCK_SIZE]
                                        response = Message(message.nodeId, INTERNAL_CHILD, STREAM, NO_ACK, ST_FIRMWARE_CONFIG_RESPONSE, pack(type, version, iBlock) + chunk)
                                        
                                        if self._pendingFirmware[nodeId]['lastBlockSent'] != iBlock:
                                            self._pendingFirmware[nodeId]['blockSent']+=1
                                            self._pendingFirmware[nodeId]['lastBlockSent'] = iBlock
                                        
                                        
                                        self._pendingFirmware[nodeId]['ts'] = time.time()
                                        
                                        self.send(response)
                                        
                                    else:
                                        self.log.warn("MySensors: FW GET : no firmware found")
                                    
                                
                                
                            elif message.subType == ST_FIRMWARE_RESPONSE :
                                pass
                            
                            elif message.subType == ST_SOUND or message.subType == ST_IMAGE:
                                
                                """
                                the payload contains a piece of an image or sound
                                
                                payload :
                                
                                | 1byte | next bytes |
                                |-------|------------|
                                | index | data       |
                                
                                """
                                payload = binascii.unhexlify(message.payload)
                                if payload:
                                    index = bord(payload[0])
                                    
                                    if nodeId not in self._pendingStreams:
                                        if index==1:
                                            # new stream
                                            self._pendingStreams[nodeId] = {
                                                't0' : time.time(),
                                                'ts' : 0,
                                                'lastIndex' : 255,
                                                'data' : '',
                                                'packetCount' : 0,
                                                'type' : message.subType
                                            }
                                        else:
                                            self.log.warn("MySensors: STREAM: first packet must start with index=1, got %s" % index)
                                        
                                    
                                    
                                    if nodeId in self._pendingStreams:
                                        
                                        stream = self._pendingStreams[nodeId]
                                        
                                        if stream['type']==message.subType:
                                            expectedIndex = 1 if stream['lastIndex']==255 else stream['lastIndex']+1
                                            
                                            if index==0 or expectedIndex == index:
                                                # append this chunk
                                                stream['data'] += payload[1:]
                                                stream['lastIndex'] = index
                                                stream['packetCount']+=1
                                                stream['ts'] = time.time()
                                                
                                                if index==0:
                                                    # end of the stream
                                                    
                                                    size = len(stream['data'])
                                                    timeElapsed = time.time() - stream['t0']
                                                    
                                                    sensor.storeStream(stream['type'], stream['data'])
                                                    
                                                    # remove stream from list
                                                    del self._pendingStreams[nodeId]
                                                    
                                                    
                                                    self.log.warn("MySensors: STREAM: end of stream, packetCount=%d , size(B)=%d , time(s)=%f" % (stream['packetCount'],size,timeElapsed))
                                                
                                            else:
                                                del self._pendingStreams[nodeId] # remove on first error
                                                self.log.warn("MySensors: STREAM: index mismatch")
                                            
                                        else:
                                            self.log.warn("MySensors: STREAM: type mismatch")
                                        
                            
                            else:
                                self.log.warn("MySensors: message not processed : %s" % str(message))
                                
                            
                        
                        else:
                            raise Exception("unknown message %s" % str(message))
                        
                    
                    except Exception as e:
                        self.log.exception(e)
                        r = False
                    
                    
                    i=0
                    while i < len(self._responseListeners):
                        responseListener = self._responseListeners[i]
                        
                        if ( ('nodeId' not in responseListener) or responseListener['nodeId'] == message.nodeId) and \
                            ( ('childSensorId' not in responseListener) or responseListener['childSensorId'] == message.childSensorId) and \
                            ( ('messageType' not in responseListener) or responseListener['messageType'] == message.messageType) and \
                            ( ('subType' not in responseListener) or responseListener['subType'] == message.subType):
                            
                            # remove this item
                            self._responseListeners.pop(i)
                            i-=1
                            
                            if callable(responseListener['callback']):
                                responseListener['callback'](False, message)
                        
                        i+=1
                    
                    
                else:
                    # ack message
                    
                    i=0
                    while i < len(self._ackWaitingMessages):
                        ackWaitingMessage = self._ackWaitingMessages[i]
                        originalMessage = ackWaitingMessage['message']
                        
                        if originalMessage.nodeId == message.nodeId and \
                            originalMessage.childSensorId == message.childSensorId and \
                            originalMessage.messageType == message.messageType and \
                            originalMessage.subType == message.subType:
                            
                            # remove this item
                            self._ackWaitingMessages.pop(i)
                            i-=1
                            
                            if callable(ackWaitingMessage['callback']):
                                ackWaitingMessage['callback'](False, originalMessage)
                            
                            break
                            
                        i+=1
        
        
        return r
    
    
    
    def update (self):
        # do some stuff regularly
        now = time.time()
        
        # check for timeout ack messages 
        i = 0
        while i < len(self._ackWaitingMessages):
            ackWaitingMessage = self._ackWaitingMessages[i]
            
            if now - ackWaitingMessage['ts'] > Controller.ACK_TIMEOUT:
                
                # remove this item
                self._ackWaitingMessages.pop(i)
                i -= 1
                
                if callable(ackWaitingMessage['callback']):
                    ackWaitingMessage['callback']('ack timeout', ackWaitingMessage['message'])
            
            i += 1
        
        
        
        # check for pending message timeout
        i = 0
        while i < len(self._pendingMessages):
            pendingMessage = self._pendingMessages[i]
            
            if now - pendingMessage['ts'] > Controller.PENDING_MESSAGE_TIMEOUT:
                
                # remove this item
                self._pendingMessages.pop(i)
                i -= 1
                
                if callable(pendingMessage['callback']):
                    pendingMessage['callback']('smartSleep timeout', pendingMessage['message'])
            
            i += 1
        
        
        # check firmware update timeout
        for nodeId, firmwareInfo in iteritems(self._pendingFirmware):
            if now - firmwareInfo['ts'] > Controller.FIRMWARE_UPDATE_TIMEOUT :
                
                # remove this item
                del self._pendingFirmware[nodeId]
                
                if callable(firmwareInfo['callback']):
                    firmwareInfo['callback']('firmware update timeout')
                
            
        
        
        # check stream timeout
        for nodeId, stream in iteritems(self._pendingStreams):
            if now - stream['ts'] > Controller.STREAM_TIMEOUT :
                
                # remove this item
                del self._pendingStreams[nodeId]
            
        
        
        
        # check response timeout
        i = 0
        while i < len(self._responseListeners):
            responseListener = self._responseListeners[i]
            
            if now - responseListener['ts'] > Controller.RESPONSE_TIMEOUT:
                
                # remove this item
                self._responseListeners.pop(i)
                i -= 1
                
                if callable(responseListener['callback']):
                    responseListener['callback']('response timeout', None)
            
            i += 1
                
            
        
        
        # check for a deconnection
        if not self.isOpened and self.isOpened != self._lastState:
            self.log.info("MySensors: disconnected")
        self._lastState = self.isOpened
        
        
        # autoconnect
        if not self.isOpened and (now - self._lastAutoconnectLoop) > Controller.AUTOCONNECT_PERIOD:
            try:
                self._lastAutoconnectLoop = now
                self.open()
                self._preventFailConnectLog = 0
            except Exception as e:
                
                if self._preventFailConnectLog % 20 == 0:
                    self.log.warn("MySensors: unable to connect : %s" % str(e))
                self._preventFailConnectLog += 1
        
        
        
    
    
    
    """
     $message message to send
     $smartSleep (optional) true|false|null if a boolean is given, force or not the smartSleep feature
     $callback (optional) function($error, $messageSent, $messageReceived = null)
     $waitResponse (optional) true|false wait for a response or not
    """
    def send (self, message, smartSleep = None, callback = None, waitResponse = None):
        
        cb = None
        
        if smartSleep is None:
            smartSleep = False
            if message.nodeId!=GATEWAY_ADDRESS and message.nodeId!=BROADCAST_ADDRESS:
                destinationNode = self.gateway.getNode(message.nodeId)
                if destinationNode:
                    smartSleep = destinationNode.smartSleep
        
        
        if callable(callback):
            if waitResponse:
                
                filter = {}
                    
                if message.messageType == REQ :
                    filter['messageType'] = SET
                    
                elif message.messageType == INTERNAL :
                    
                    if message.subType == I_ID_REQUEST :
                        filter['subType'] = I_ID_RESPONSE
                    elif message.subType == I_NONCE_REQUEST :
                        filter['subType'] = I_NONCE_RESPONSE
                    elif message.subType == I_HEARTBEAT_REQUEST :
                        filter['subType'] = I_HEARTBEAT_RESPONSE
                    elif message.subType == I_DISCOVER_REQUEST :
                        filter['subType'] = I_DISCOVER_RESPONSE
                    elif message.subType == I_PING :
                        filter['subType'] = I_PONG
                    elif message.subType == I_REGISTRATION_REQUEST :
                        filter['subType'] = I_REGISTRATION_RESPONSE
                    elif message.subType == I_PRESENTATION :
                        # todo
                        # multiple response
                        pass
                    elif message.subType == I_DEBUG or message.subType == I_VERSION :
                        filter['subType'] = message.subType
                    
                    if filter:
                        filter['messageType'] = INTERNAL
                
                
                def waitresp_cb(error, messageSent):
                    if error:
                        # an error occurs, the message could not have been sent
                        callback(error, messageSent, None)
                    else:
                        # wait for a response
                        
                        def cb(error, messageReceived):
                            callback(error, messageSent, messageReceived)
                        
                        self._responseListeners.append( dict_recursive_update({
                            'callback' : cb,
                            'ts' : time.time(),
                            'nodeId' : messageSent.nodeId,
                            'childSensorId' : messageSent.childSensorId,
                            'messageType' : messageSent.messageType,
                            'subType' : messageSent.subType
                        }, filter) )
                    
                cb = waitresp_cb
            
            else:
                
                def nowaitresp_cb(error, messageSent):
                    callback(error, messageSent, None)
                
                cb = nowaitresp_cb
        
        self.log.debug("MySensors: message send nodeId=%d sensorId=%d messageType=%d smartSleep=%s" % (message.nodeId,message.childSensorId,message.messageType,str(smartSleep)))
        
        ts = time.time()
        
        message.ts = ts
        
        if not self.isOpened:
            if cb:
                cb('not connected', message)
            
            return 0
        
        
        if smartSleep:
            # buffer this message
            # wait for a heartbeat message to send it !
            
            self._pendingMessages.append({
                'message' : message,
                'callback' : cb,
                'ts' : ts
            })
            
            return 0
        else:
            
            if message.ack == REQUEST_ACK:
                # ack requested 
                self._ackWaitingMessages.append({
                    'message' : message,
                    'callback' : cb,
                    'ts' : ts
                })
            
            
            wb =  self.transport.write(message)
            
            if message.ack != REQUEST_ACK and cb:
                cb(False, message)
            
            
            return wb
    
    
    
    
    def updateFirmware (self, node, firmware, callback = None):
        
        # tells the node, there is a new firmware
        type = random.randint(1,32767)
        version=256; # === 1.0 or 0100 in hex
        nbBlocks = int(math.ceil(len(firmware)/Controller.FIRMWARE_BLOCK_SIZE))
        crc = binascii.crc_hqx(firmware, 0)
        
        self._pendingFirmware[node.nodeId] = {
            'callback' : callback,
            'firmware' : firmware,
            'deviceId' : node.id,
            'ts' : time.time(),
            'lastBlockSent' : -1,
            'blockSent' : 0,
            'type' : type,
            'version' : version,
            'nbBlocks' : nbBlocks,
            'crc' : crc
        }
        
        message = Message(node.nodeId, INTERNAL_CHILD, STREAM, NO_ACK, ST_FIRMWARE_CONFIG_RESPONSE, pack('nnnn',type, version, nbBlocks, crc))
        
        def cb(error, messageSent, messageReceived):
            if error:
                # free memory
                del self._pendingFirmware[node.nodeId]
                
                if callable(callback):
                    callback(error)
        
        self.send(message, callback = cb)
        
    
    
    
    



