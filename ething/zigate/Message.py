
from Zigate import clusterIdToName
import struct


def hex2str (self, hex):
    str = ''
    for i in range(0, len(hex), 2):
        str += chr(int(hex[i:i+2], 16))
    return str

def crc(str):
    crctmp = 0
    
    for i in range(0, str/2):
        crctmp = crctmp ** int(str[i*2:i*2+2], 16)
    
    return crctmp


class Message(object):
    
    packetNames = {
        "0010" : "Get Version",
        "0020" : "Set Expended PANID",
        "0021" : "Set Channel Mask",
        "0022" : "Set Security State + Key",
        "0023" : "Set device Type",
        "0024" : "Start Network",
        "0025" : "Start Network Scan",
        "0013" : "ZLO/ZLL ?Factory New? Reset",
        "0014" : "Permit Join",
        "0011" : "Reset",
        "0012" : "Erase Persistent Data",
        "0030" : "Bind",
        "0031" : "Unbind",
        "0040" : "Network Address request",
        "0041" : "IEEE Address request",
        "0042" : "Node Descriptor request",
        "0043" : "Simple Descriptor request",
        "0044" : "Power Descriptor request",
        "0045" : "Active Endpoint request",
        "0046" : "Match Descriptor request",
        "0026" : "Remove Device",
        "002B" : "User Descriptor Set",
        "002C" : "User Descritpor Request",
        "0034" : "Complex Descriptor request",
        "0047" : "Management Leave request",
        "0049" : "Permit Joining request",
        "004A" : "Management Network Update request",
        "004B" : "System Server Discovery request",
        "004E" : "Management LQI request",
        "0100" : "Read Attribute request",
        "0110" : "Write Attribute request",
        "0140" : "Attribute Discovery request",
        "0027" : "Enable Permissions Controlled Joins",
        "0028" : "Authenticate Device",
        "0120" : "Configure Reporting request",
        "0029" : "Out of Band Commissioning Data Request",
        "0060" : "Add Group",
        "0061" : "View Group",
        "0062" : "Get Group Membership",
        "0063" : "Remove Group",
        "0064" : "Remove All Groups",
        "0065" : "Add Group if identify",
        "0070" : "Identify Send",
        "0071" : "Identify Query",
        "0080" : "Move to Level",
        "0081" : "Move to level with/without on/off",
        "0082" : "Move Step",
        "0083" : "Move Stop Move",
        "0084" : "Move Stop with On Off",
        "0094" : "On / Off with effects Send",
        "0092" : "On/Off with no effects",
        "0093" : "On / Off Timed Send",
        "00A0" : "View Scene",
        "00A1" : "Add Scene",
        "00A2" : "Remove Scene",
        "00A3" : "Remove all scenes",
        "00A4" : "Store Scene",
        "00A5" : "Recall Scene",
        "00A6" : "Scene Membership request",
        "00B0" : "Move to Hue",
        "00B1" : "Move Hue",
        "00B2" : "Step Hue",
        "00B3" : "Move to saturation",
        "00B4" : "Move saturation",
        "00B5" : "Step saturation",
        "00B6" : "Move to hue and saturation",
        "00B7" : "Move to colour",
        "00B8" : "Move Colour",
        "00B9" : "Step Colour",
        "00D0" : "Initiate Touchlink",
        "00D2" : "Touch link factory reset target",
        "00E0" : "Identify Trigger Effect",
        "0092" : "On / Off with Effects",
        "0093" : "On / Off Timed",
        "00A7" : "Add Enhanced Scene",
        "00A8" : "View Enhanced Host.Node Scene",
        "00A9" : "Copy Scene",
        "00BA" : "Enhanced Move to Hue",
        "00BB" : "Enhanced Move Hue",
        "00BC" : "Enhanced Step Hue",
        "00BD" : "Enhanced Move to hue and saturation",
        "00BE" : "Colour Loop Set",
        "00BF" : "Stop Move Step",
        "00C0" : "Move to colour temperature",
        "00C1" : "Move colour temperature",
        "00C2" : "Step colour temperature",
        "00F0" : "Lock / Unlock Door",
        "0400" : "IAS Zone enroll response",
        "0530" : "Raw APS Data Request",
        '8000' : 'Statut',
        '8001' : 'Log message',
        '8002' : 'Data indication',
        '8003' : 'List clusters',
        '8004' : 'List attributs',
        '8005' : 'List commands',
        '8010' : 'Version list',
        '8024' : 'Network joined / formed',
        '8014' : 'Permit join status response',
        '8006' : 'Non Factory new Restart',
        '8007' : 'Factory New Restart',
        '8030' : 'Bind response',
        '8031' : 'Unbind response',
        '004D' : 'Device announce',
        '8040' : 'Network Address response',
        '8041' : 'IEEE Address response',
        '8042' : 'Node Descriptor response',
        '8043' : 'Simple Descriptor response',
        '8044' : 'Power Descriptor response',
        '8045' : 'ctive Endpoint response',
        '8046' : 'Match Descriptor response',
        '802C' : 'User Descriptor Response',
        '802B' : 'User Descriptor Notify',
        '8034' : 'Complex Descriptor response',
        '8047' : 'Management Leave response',
        '8048' : 'Leave indication',
        '804A' : 'Management Network Update response',
        '804B' : 'System Server Discovery response',
        '804E' : 'Management LQI response',
        '8140' : 'Attribute Discovery response',
        '8028' : 'Authenticate response',
        '8120' : 'Configure Reporting response',
        '8100' : 'Read individual Attribute Response',
        '8110' : 'Write Attribute Response',
        '8102' : 'Report Individual Attribute response',
        '8101' : 'Default response',
        '8029' : 'Out of Band Commissioning Data Response',
        '8060' : 'Add Group response',
        '8061' : 'View Group response',
        '8062' : 'Get Group Membership response',
        '8063' : 'Remove Group response',
        '80A0' : 'View Scene response',
        '80A1' : 'Add Scene response',
        '80A2' : 'Remove Scene response',
        '80A3' : 'Remove All Scene response',
        '80A4' : 'Store Scene response',
        '80A6' : 'Scene Membership response',
        '00D1' : 'Touchlink Status',
        '8401' : 'Zone status change notification',
        '8701' : 'Router Discovery Confirm',
        '8702' : 'APS Data Confirm Fail'
    }
    
    
    def __init__ (self, type, payload = '', rssi = '00'):
        self.attr = {}
        self.type = type
        self.payload = payload
        self.rssi = rssi
    
    @property
    def type (self):
        return self._type
    
    @type.setter
    def type (self, type):
        if isinstance(type, int):
            type = format('X', type)
        if len(type) > 4:
            raise Exception("invalid type")
        self._type = type.rjust(4, "0").upper()
    
    
    @property
    def payload (self):
        return self._payload
    
    @payload.setter
    def payload (self, payload):
        # must be hexadecimal
        if len(payload) % 2 != 0:
            raise Exception("invalid payload length")
        self._payload = payload.upper()
        
        self.decode()
    
    
    @property
    def rssi (self):
        return self._rssi
    
    @rssi.setter
    def rssi (self, rssi):
        if len(rssi) > 2:
            raise Exception("invalid rssi")
        self._rssi = rssi.rjust(2, "0")
    
    
    def __getitem__ (self,  name ):
        return self.attr.get(name)
    
    def __str__(self):
        return self.stringify()
    
    def __repr__(self):
        return self.stringify()
    
    def build (self):
        return struct.pack("H*",self.stringify())
    
    
    def computeLength (self):
        return len(self.payload)/2
    
    
    def computeCRC (self):
        return crc(self.type + format('4X', self.computeLength()) + self.payload + self.rssi)
    
    
    
    @staticmethod
    def transcode (datas):
        mess=""
        if len(datas)%2 !=0:
            return datas
        
        for i in range(0, len(datas), 2):
            hx = datas[i:i+2]
            byte = int(hx, 16)
            
            if byte>10 :
                 mess += hx
            else:
                 mess += "02" + format("02X", byte ** 0x10)
        
        return mess
    
    
    def decode (self):
        
        type = self.type
        payload = self.payload
        
        attr = {}
        
        if type=="004D":  # Device announce
            
            attr = {
                'srcAddr' : payload[0:0+4],
                'ieeeAddr' : payload[4:4+16],
                'macCapability' : payload[20:20+2]
            }
            
        elif type=="8000":  # Status
            # 01 80 00 00 05 95 00 00 00 10 00 03
            """
            Type: 0x8000 (Status)
            Length: 5
            Status: 0x00 (Success)
            SQN: 0x00
            Message: 
            """
            attr = {
                'status' : payload[0:0+2],
                'sqn' : payload[2:2+2],
                'type' : payload[4:4+4],
                'message' : hex2str(payload[8:]) if len(payload) > 8 else ''
            }
        
        elif type=="8001":  # Log
            
            attr = {
                'logLevel' : int(payload[0:0+2], 16),
                'message' : hex2str(payload[2:])
            }

        elif type=="8010":  # Version
            
            attr = {
                'appVersion' : int(payload[0:0+4], 16),
                'sdkVersion' : int(payload[4:4+4], 16)
            }

        elif type=="8024":  # Network joined / formed
            attr = {
                'status' : payload[0:0+2],
                'shortAddr' : payload[2:2+4],
                'extendedAddr' : payload[6:6+16],
                'channel' : payload[22:22+2]
            }
        elif type=="8043":  # Simple Descriptor Response
            
            attr = {
                'sqn' : payload[0:0+2],
                'status' : payload[2:2+2],
                'shortAddr' : payload[4:4+4],
                'length' : int(payload[8:8+2], 16),
                'endpoint' : payload[10:10+2],
                'profile' : payload[12:12+4],
                'deviceId' : payload[16:16+4],
                'bitFields' : payload[20:20+2]
            }
            
            inClusterCount = int(payload[22:22+2], 16)
            inClusterList = []
            for i in range(0, inClusterCount):
                j = 24 + i*4
                inClusterList.append( payload[j:j+4] )
            
            j = 24 + inClusterCount*4
            outClusterCount = int(payload[j:j+2], 16)
            outClusterList = []
            for i in range(0, outClusterCount):
                j = 26 + inClusterCount*4 + i*4
                outClusterList.append( payload[j:j+4] )
            
            
            attr['inClusterCount'] = inClusterCount
            attr['inClusterList'] = inClusterList
            attr['outClusterCount'] = outClusterCount
            attr['outClusterList'] = outClusterList
        
        elif type=="8045":  # Active Endpoints Response
            
            attr = {
                'sqn' : payload[0:0+2],
                'status' : payload[2:2+2],
                'shortAddr' : payload[4:4+4],
                'endpointCount' : int(payload[8:8+2], 16),
                'endpointList' : []
            }
            
            for i in range(0, attr['endpointCount']):
                j = 10+i*2
                attr['endpointList'].append( payload[j:j+2] )
        
        
        elif type=="8101":  # Default Response
            
            attr = {
                'sqn' : payload[0:0+2],
                'endpoint' : payload[2:2+2],
                'clusterId' : payload[4:4+4],
                'commandId' : payload[8:8+2],
                'statusCode' : payload[10:10+2]
            }
        
        elif type=="8102":  # Report Individual Attribute response
            
            attr = {
                'sqn' : payload[0:0+2],
                'srcAddr' : payload[2:2+4],
                'endpoint' : payload[6:6+2],
                'clusterId' : payload[8:8+4],
                'attrId' : payload[12:12+4],
                'attrStatus' : payload[16:16+2],
                'attrType' : payload[18:18+2],
                'attrSize' : int(payload[20:20+4], 16),
                'data' : payload[24:]
            }
            
            
            
        elif type=="8401":  #
            
            srcAddrMode = payload[8:8+2]
            
            d = 4 # depending on srcAddrMode, 4 or 8
            
            attr = {
                'sqn' : payload[0:0+2],
                'endpoint' : payload[2:2+2],
                'clusterId' : payload[4:4+4],
                'srcAddrMode' : srcAddrMode,
                'srcAddr' : payload[10:10+d],
                'zoneStatus' : payload[10+d:10+d+4],
                'extendedStatus' : payload[14+d:14+d+2],
                'zoneId' : payload[16+d:16+d+2]
            }
        
        elif type=="8702":  # APS Data Confirm Fail
            
            dstAddrMode = payload[6:6+2]
            
            d = len(payload) - 10 # depending on dstAddrMode
            
            attr = {
                'status' : payload[0:0+2],
                'srcEndpoint' : payload[2:2+2],
                'dstEndpoint' : payload[4:4+2],
                'dstAddrMode' : dstAddrMode,
                'dstAddr' : payload[8:8+d],
                'sqn' : payload[8+d:8+d+2]
            }
        
        
        
        self.attr = attr
        
    
    
    # packet must be an hexadecimal string
    # 01 80 00 00 05 95 00 00 00 10 00 03
    @staticmethod
    def parse (packet):

        if len(packet)<14:
            raise Exception("invalid packet len<7 [%s]" % packet)
        
        if packet[0:2] != '01':
            raise Exception("packet does not start with 0x01 [%s]" % packet)
        
        if packet[-2:] != '03':
            raise Exception("packet does not end with 0x03 [%s]" % packet)
        
        
        datas = packet[2:-2]
        
        #message type
        type=datas[0:4]
        
        #message length
        ln=int(datas[4:8], 16)
        if len(datas) != (5+ln)*2:
            raise Exception("invalid packet length mismatch, %d != %d [%s]" % (len(datas), (5+ln)*2, packet))
        

        #CRC
        crc_read=int(datas[8:10], 16)
        
        payload = datas[10:10+ln*2]
        
        crc_computed = crc(datas[0:8] + payload)
        
        rssi = payload[-2:] if len(payload)>1 else '00'
        
        payload = payload[0:-2]
        
        if crc_computed != crc_read:
            raise Exception("invalid packet CRC mismatch [%s]" % packet)
        
        
        return Message(type, payload, rssi)

    
    
    def stringify (self):
        msg = '01'
        
        msg += self.transcode(self.type)
        
        msg += self.transcode(format('04X',self.computeLength()))
        
        msg += format('02X',self.computeCRC())
        
        msg += self.transcode(self.payload)
        
        msg += '03'
        
        return msg
    
    
    def toJson (self):
        return {
            'type' : self.type,
            'rssi' : self.rssi,
            'payload' : self.payload,
            'attr' : self.attr
        }
    
    
    @staticmethod
    def decodeMacCapability (macCapability):
        if isinstance(macCapability, basestring):
            macCapability = int(macCapability[0:2], 16)
        
        return {
            'Alternate PAN Coordinator' :  bool(macCapability & 0b00000001),
            'Device Type' :  'FFD' if bool(macCapability & 0b00000010) else 'RFD',
            'Power Source' :  'main' if bool(macCapability & 0b00000100) else 'battery',
            'Receiver On When Idle' :  bool(macCapability & 0b00001000),
            'Security Capability' :  bool(macCapability & 0b01000000),
            'Allocate Address' :  bool(macCapability & 0b10000000)
        }
    
    
    def toHumanReadable (self):
        
        name = self.packetNames.get(self.type, '?')
        
        attrstr = ''
        for key in self.attr:
            value = self.attr[key]
            
            attrstr += ' %s: ' % key
            if isinstance(value, list):
                
                if key == "inClusterList" or key == "outClusterList":
                    f = []
                    for i in value:
                        f.append( '%s (%s)' % (value[i], clusterIdToName(value[i])) )
                    value = f
                
                attrstr += ";".join(value)
                
            else:
                attrstr += str(value)
                
                if key == "clusterId":
                    attrstr += ' (%s)' % clusterIdToName(value)
        
        if attrstr:
            attrstr = ','+attrstr
        
        return "type: 0x%s (%s) , payload: %s , rssi: 0x%s %s" % (self.type, name, self.payload, self.rssi, attrstr)
    
    
    
    



