# coding: utf-8
from future.utils import string_types, integer_types, binary_type, text_type


from .helpers import *


class Message(object):

    def __init__(self, nodeId, childSensorId, messageType, subType, value=None, payload=None, ack = None):
        
        self.nodeId = nodeId
        self.childSensorId = childSensorId
        self.messageType = messageType
        self.subType = subType
        self.ack = ack if ack is not None else False
        self.ack_set = (ack is not None)
        
        self.payload = b''

        if value is not None:
            self.value = value
        elif payload is not None:
            self.payload = payload
    
    @property
    def nodeId(self):
        return self._nodeId
    
    @nodeId.setter
    def nodeId(self, value):
        self._nodeId = int(value)
    
    @property
    def childSensorId(self):
        return self._childSensorId
    
    @childSensorId.setter
    def childSensorId(self, value):
        self._childSensorId = int(value)
    
    @property
    def messageType(self):
        return self._messageType
    
    @messageType.setter
    def messageType(self, value):
        self._messageType = int(value)
    
    @property
    def subType(self):
        return self._subType
    
    @subType.setter
    def subType(self, value):
        if isinstance(value, integer_types):
            self._subType = value
        else:

            if isinstance(value, binary_type):
                value = value.decode('utf8')

            if isinstance(value, string_types):

                try:
                    self._subType = int(value)
                except ValueError:
                    if isSensorTypeStr(value):
                        self._subType = sensorTypeInt(value)
                    elif isValueTypeStr(value):
                        self._subType = valueTypeInt(value)
                    else:
                        raise Exception('invalid subType value : %s' % str(value))

            else:
                raise Exception('invalid subType value : %s' % str(value))
    
    @property
    def ack(self):
        return self._ack
    
    @ack.setter
    def ack(self, value):
        self._ack = int(value)
    
    @staticmethod
    def parse(message, encoding='utf8'):

        if isinstance(message, text_type):
            message = message.encode(encoding)

        # remove newline char
        message = message.strip()

        parts = message.split(b';')
        if len(parts) == 6:
            return Message(
                parts[0],
                parts[1],
                parts[2],
                parts[4],
                ack = parts[3],
                payload = parts[5]
            )
        else:
            raise Exception('invalid message')

    def raw(self):
        p = u"%d;%d;%d;%d;%d;" % (
            self.nodeId, self.childSensorId, self.messageType, self.ack, self.subType)
        p = p.encode('utf8')
        p += self.payload
        return p

    def stringify(self):
        return self.raw().decode('utf8')

    def toHumanReadable(self):

        messageTypeStr = None
        for t in messageTypes:
            if messageTypes[t] == self.messageType:
                messageTypeStr = t
                break
        if not messageTypeStr:
            messageTypeStr = str(self.messageType)

        subTypeStr = None
        if self.messageType == PRESENTATION:
            subTypeStr = sensorTypeStr(self.subType)
        elif self.messageType == SET or self.messageType == REQ:
            subTypeStr = valueTypeStr(self.subType)
        elif self.messageType == INTERNAL:
            for t in internalTypes:
                if internalTypes[t] == self.subType:
                    subTypeStr = t
                    break
        if not subTypeStr:
            subTypeStr = str(self.subType)

        return u"%d;%d;%s;%d;%s;%s" % (self.nodeId, self.childSensorId, messageTypeStr, self.ack, subTypeStr, self.payload.decode('utf8'))

    def __str__(self):
        return self.stringify()

    def __expr__(self):
        return self.stringify()

    def toJson(self):
        return {
            "nodeId": self.nodeId,
            "childSensorId": self.childSensorId,
            "messageType": self.messageType,
            "ack": self.ack,
            "subType": self.subType,
            "payload": self.payload
        }
    
    @property
    def value(self):
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
                        return False if (self.payload == b'0' or len(self.payload) == 0) else True

        return self.payload.decode('utf8') if len(self.payload) else None
    
    @value.setter
    def value(self, value):
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

    @property
    def payload(self):
        return self._payload

    @payload.setter
    def payload(self, data):

        if data is None:
            self._payload = b''
        elif isinstance(data, text_type):
            self._payload = data.encode('utf8')
        elif isinstance(data, binary_type):
            self._payload = data
        else:
            raise Exception('the payload must be a binary instance, got %s' % type(data).__name__)

    def copy(self):
        return type(self).parse(self.raw())
