# coding: utf-8
from future.utils import string_types, integer_types, binary_type, text_type


from .helpers import *

class Message(object):
    
    
    def __init__ (self, nodeId, childSensorId, messageType, ack, subType, value = None, payload = None):
        
        self.nodeId = int(nodeId)
        self.childSensorId = int(childSensorId)
        self.messageType = int(messageType)
        self.ack = int(ack)
        self.payload = b''
        
        if isinstance(subType, integer_types):
            self.subType = subType
        else:
            
            if isinstance(subType, binary_type):
                subType = subType.decode('utf8')
            
            if isinstance(subType, string_types):
                
                try:
                    self.subType = int(subType)
                except ValueError:
                    if isSensorTypeStr(subType):
                        self.subType = sensorTypeInt(subType)
                    elif isValueTypeStr(subType):
                        self.subType = valueTypeInt(subType)
                    else:
                        raise Exception('invalid subType value : %s' % str(subType))
                
            else:
                raise Exception('invalid subType value : %s' % str(subType))
        
        if value is not None:
            self.setValue(value)
        elif payload is not None:
            
            if isinstance(payload, text_type):
                payload = payload.encode('utf8')
            
            if isinstance(payload, binary_type):
                self.payload = payload
            else:
                raise Exception('the payload must be a binary instance, got %s' % type(payload).__name__)
    
    
    @staticmethod
    def parse (message, encoding = 'utf8'):
        
        if isinstance(message, text_type):
            message = message.encode(encoding)
        
        # remove newline char
        message = message.strip()
        
        parts = message.split(b';')
        if len(parts)==6:
            return Message(
                parts[0],
                parts[1],
                parts[2],
                parts[3],
                parts[4],
                payload = parts[5]
            )
        else:
            raise Exception('invalid message')
    
    def raw (self):
        p = u"%d;%d;%d;%d;%d;" % (self.nodeId, self.childSensorId, self.messageType, self.ack, self.subType)
        p = p.encode('utf8')
        p += self.payload
        return p
    
    def stringify (self):
        return self.raw().decode('utf8')
    
    
    def toHumanReadable (self):
        
        messageTypeStr = None
        for t in messageTypes:
            if messageTypes[t] == self.messageType:
                messageTypeStr = t
                break;
        if not messageTypeStr:
            messageTypeStr = str(self.messageType)
        
        subTypeStr = None
        if self.messageType == PRESENTATION :
            subTypeStr = sensorTypeStr(self.subType)
        elif self.messageType == SET or self.messageType == REQ :
            subTypeStr = valueTypeStr(self.subType)
        elif self.messageType == INTERNAL :
            for t in internalTypes:
                if internalTypes[t] == self.subType:
                    subTypeStr = t
                    break;
        if not subTypeStr:
            subTypeStr = str(self.subType)
        
        return u"%d;%d;%s;%d;%s;%s" % (self.nodeId, self.childSensorId, messageTypeStr, self.ack, subTypeStr, self.payload.decode('utf8'))
    
    
    def __str__ (self):
        return self.stringify()
    
    def __expr__ (self):
        return self.stringify()
    
    
    def toJson (self):
        return {
            nodeId: self.nodeId,
            childSensorId: self.childSensorId,
            messageType: self.messageType,
            ack: self.ack,
            subType: self.subType,
            payload: self.payload
        }
    
    
    
    def getValue (self):
        if self.messageType == SET or self.messageType == REQ:
            
            datatype = valueTypeStr(self.subType)
            meta = valueTypes.get(datatype)
            
            if meta:
                codec = meta[2]
                
                if isinstance(codec, tuple):
                    return codec[1](self.payload)
                else:
                    if codec == 'float':
                        return float(self.payload)
                    elif codec == 'int':
                        return int(self.payload)
                    elif codec == 'bool':
                        return False if (self.payload == b'0' or len(self.payload)==0) else True
        
        return self.payload.decode('utf8') if len(self.payload) else None
    
    
    def setValue(self, value):
        if self.messageType == SET or self.messageType == REQ:
            
            datatype = valueTypeStr(self.subType)
            meta = valueTypes.get(datatype)
            
            if meta:
                codec = meta[2]
                
                if isinstance(codec, tuple):
                    value = codec[0](value)
                else:
                    if codec == 'bool':
                        value = bool(value)
        
        if isinstance(value, bool):
            self.payload = b'1' if value else b'0'
        else:
            self.payload = str(value).encode('utf8')
        


