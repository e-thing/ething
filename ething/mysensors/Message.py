

import MySensors

class Message(object):
    
    
    def __init__ (self, nodeId, childSensorId, messageType, ack, subType, value = None, payload = None):
        
        self.nodeId = int(nodeId)
        self.childSensorId = int(childSensorId)
        self.messageType = int(messageType)
        self.ack = int(ack)
        
        if isinstance(subType, int):
            self.subType = subType
        elif isinstance(subType, basestring):
            if subType.decode('utf8').isnumeric():
                self.subType = int(subType)
            elif MySensors.isSensorTypeStr(subType):
                self.subType = MySensors.sensorTypeInt(subType)
            elif MySensors.isValueTypeStr(subType):
                self.subType = MySensors.valueTypeInt(subType)
            else:
                raise Exception('invalid subType value : %s' % str(subType))
        else:
            raise Exception('invalid subType value : %s' % str(subType))
        
        if value is not None:
            self.setValue(value)
        else:
            self.payload = str(payload) if payload else ''
    
    
    @staticmethod
    def parse (message):
        
        # remove newline char
        message = message.strip()
        
        parts = message.split(';')
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
    
    
    def stringify (self):
        return "%d;%d;%d;%d;%d;%s" % (self.nodeId, self.childSensorId, self.messageType, self.ack, self.subType, self.payload)
    
    
    def toHumanReadable (self):
        
        messageTypeStr = None
        for t in MySensors.messageTypes:
            if MySensors.messageTypes[t] == self.messageType:
                messageTypeStr = t
                break;
        if not messageTypeStr:
            messageTypeStr = str(self.messageType)
        
        subTypeStr = None
        if self.messageType == MySensors.PRESENTATION :
            subTypeStr = MySensors.sensorTypeStr(self.subType)
        elif self.messageType == MySensors.SET or self.messageType == MySensors.REQ :
            subTypeStr = MySensors.valueTypeStr(self.subType)
        elif self.messageType == MySensors.INTERNAL :
            for t in MySensors.internalTypes:
                if MySensors.internalTypes[t] == self.subType:
                    subTypeStr = t
                    break;
        if not subTypeStr:
            subTypeStr = str(self.subType)
        
        return "%d;%d;%s;%d;%s;%s" % (self.nodeId, self.childSensorId, messageTypeStr, self.ack, subTypeStr, self.payload)
    
    
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
    
    
    def fromHex (self):
        return str(binascii.unhexlify(self.payload))
    
    
    def getValue (self):
        if self.messageType == MySensors.SET or self.messageType == MySensors.REQ:
            
            datatype = MySensors.valueTypeStr(self.subType)
            meta = MySensors.valueTypes.get(datatype)
            
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
                        return False if (self.payload == '0' or len(self.payload)==0) else True
        
        return str(self.payload) if len(self.payload) else None
    
    
    def setValue(self, value):
        if self.messageType == MySensors.SET or self.messageType == MySensors.REQ:
            
            datatype = MySensors.valueTypeStr(self.subType)
            meta = MySensors.valueTypes.get(datatype)
            
            if meta:
                codec = meta[2]
                
                if isinstance(codec, tuple):
                    value = codec[0](value)
                else:
                    if codec == 'bool':
                        value = bool(value)
        
        if isinstance(value, bool):
            self.payload = '1' if value else '0'
        else:
            self.payload = str(value)
        


if __name__ == "__main__":
    
    m = Message(MySensors.GATEWAY_ADDRESS, MySensors.INTERNAL_CHILD, MySensors.INTERNAL, MySensors.NO_ACK, MySensors.I_VERSION)
    
    print str(m)
    
    print m.toHumanReadable()
    
    m = Message.parse(u'98;1;1;0;17;269')
    print m.subType, type(m.subType)
    print m.messageType, type(m.messageType)


