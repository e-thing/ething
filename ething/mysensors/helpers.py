# coding: utf-8
from future.utils import string_types, integer_types



BROADCAST_ADDRESS                = 255
GATEWAY_ADDRESS                = 0
INTERNAL_CHILD                = 255; # 0xFF


# type
PRESENTATION = 0
SET = 1
REQ = 2
INTERNAL = 3
STREAM = 4

# presentation subtype
S_DOOR =                  0 
S_MOTION =                1 
S_SMOKE =                 2 
S_LIGHT =                 3 
S_BINARY =                3 
S_DIMMER =                4 
S_COVER =                 5 
S_TEMP =                  6 
S_HUM =                   7 
S_BARO =                  8 
S_WIND =                  9 
S_RAIN =                  10
S_UV =                    11
S_WEIGHT =                12
S_POWER =                 13
S_HEATER =                14
S_DISTANCE =              15
S_LIGHT_LEVEL =           16
S_ARDUINO_NODE =          17
S_ARDUINO_REPEATER_NODE = 18
S_LOCK =                  19
S_IR =                    20
S_WATER =                 21
S_AIR_QUALITY =           22
S_CUSTOM =                23
S_DUST =                  24
S_SCENE_CONTROLLER =      25
S_RGB_LIGHT =             26
S_RGBW_LIGHT =            27
S_COLOR_SENSOR =          28
S_HVAC =                  29
S_MULTIMETER =            30
S_SPRINKLER =             31
S_WATER_LEAK =            32
S_SOUND =                 33
S_VIBRATION =             34
S_MOISTURE =              35
S_INFO =                  36
S_GAS =                   37
S_GPS =                   38
S_WATER_QUALITY =         39
# extra
S_CAM =                   52
S_UNK =                   9999 

# set/req subtype
V_TEMP               = 0 
V_HUM                = 1 
V_STATUS             = 2 
V_LIGHT              = 2 
V_PERCENTAGE         = 3 
V_DIMMER             = 3 
V_PRESSURE           = 4 
V_FORECAST           = 5 
V_RAIN               = 6 
V_RAINRATE           = 7 
V_WIND               = 8 
V_GUST               = 9 
V_DIRECTION          = 10
V_UV                 = 11
V_WEIGHT             = 12
V_DISTANCE           = 13
V_IMPEDANCE          = 14
V_ARMED              = 15
V_TRIPPED            = 16
V_WATT               = 17
V_KWH                = 18
V_SCENE_ON           = 19
V_SCENE_OFF          = 20
V_HVAC_FLOW_STATE    = 21
V_HVAC_SPEED         = 22
V_LIGHT_LEVEL        = 23
V_VAR1               = 24
V_VAR2               = 25
V_VAR3               = 26
V_VAR4               = 27
V_VAR5               = 28
V_UP                 = 29
V_DOWN               = 30
V_STOP               = 31
V_IR_SEND            = 32
V_IR_RECEIVE         = 33
V_FLOW               = 34
V_VOLUME             = 35
V_LOCK_STATUS        = 36
V_LEVEL              = 37
V_VOLTAGE            = 38
V_CURRENT            = 39
V_RGB                = 40
V_RGBW               = 41
V_ID                 = 42
V_UNIT_PREFIX        = 43
V_HVAC_SETPOINT_COOL = 44
V_HVAC_SETPOINT_HEAT = 45
V_HVAC_FLOW_MODE     = 46
V_TEXT               = 47
V_CUSTOM             = 48
V_POSITION           = 49
V_IR_RECORD          = 50
V_PH                 = 51
V_ORP                = 52
V_EC                 = 53
V_VAR                = 54
V_VA                 = 55
V_POWER_FACTOR       = 56

# internal subtype
I_BATTERY_LEVEL         = 0 
I_TIME                  = 1 
I_VERSION               = 2 
I_ID_REQUEST            = 3 
I_ID_RESPONSE           = 4 
I_INCLUSION_MODE        = 5 
I_CONFIG                = 6 
I_FIND_PARENT           = 7 
I_FIND_PARENT_RESPONSE  = 8 
I_LOG_MESSAGE           = 9 
I_CHILDREN              = 10
I_SKETCH_NAME           = 11
I_SKETCH_VERSION        = 12
I_REBOOT                = 13
I_GATEWAY_READY         = 14
I_SIGNING_PRESENTATION  = 15
I_NONCE_REQUEST         = 16
I_NONCE_RESPONSE        = 17
I_HEARTBEAT_REQUEST     = 18
I_PRESENTATION          = 19
I_DISCOVER_REQUEST      = 20
I_DISCOVER_RESPONSE     = 21
I_HEARTBEAT_RESPONSE    = 22
I_LOCKED                = 23
I_PING                  = 24
I_PONG                  = 25
I_REGISTRATION_REQUEST  = 26
I_REGISTRATION_RESPONSE = 27
I_DEBUG                 = 28

# stream subtype
ST_FIRMWARE_CONFIG_REQUEST  = 0;  #!< Request new FW, payload contains current FW details
ST_FIRMWARE_CONFIG_RESPONSE = 1;  #!< New FW details to initiate OTA FW update
ST_FIRMWARE_REQUEST         = 2;  #!< Request FW block
ST_FIRMWARE_RESPONSE        = 3;  #!< Response FW block
ST_SOUND                    = 4;  #!< Sound
ST_IMAGE                    = 5;  #!< Image



NO_ACK                 = 0
REQUEST_ACK            = 1
IS_ACK                 = 1

messageTypes = {
    'PRESENTATION' : 0,
    'SET' : 1,
    'REQ' : 2,
    'INTERNAL' : 3,
    'STREAM' : 4
}


# id, name, read attributes, write attributes
sensorTypes = {
    'S_DOOR' : (0 , "door", True),
    'S_MOTION' : (1 , "motion", True),
    'S_SMOKE' : (2 , "smoke", True),
    'S_BINARY' : (3 , "switch", True),
    'S_LIGHT' : (3 , "light", True),
    'S_DIMMER' : (4 , "dimmer", True),
    'S_COVER' : (5 , "window cover", True),
    'S_TEMP' : (6 , "thermometer", True),
    'S_HUM' : (7 , "humidity sensor", True),
    'S_BARO' : (8 , "barometer", True),
    'S_WIND' : (9 , "wind sensor", True),
    'S_RAIN' : (10, "rain sensor", True),
    'S_UV' : (11, "UV sensor", True),
    'S_WEIGHT' : (12, "weight sensor", True),
    'S_POWER' : (13, "power meter", True),
    'S_HEATER' : (14, "heater device", True),
    'S_DISTANCE' : (15, "distance sensor", True),
    'S_LIGHT_LEVEL' : (16, "light sensor", True),
    'S_ARDUINO_NODE' : (17, "arduino", True),
    'S_ARDUINO_REPEATER_NODE' : (18, "arduino repeater", True),
    'S_LOCK' : (19, "locker", True),
    'S_IR' : (20, "IR device", True),
    'S_WATER' : (21, "water meter", True),
    'S_AIR_QUALITY' : (22, "air quality sensor", True),
    'S_CUSTOM' : (23, "custom", True),
    'S_DUST' : (24, "dust sensor", True),
    'S_SCENE_CONTROLLER' : (25, "scene controller", True),
    'S_RGB_LIGHT' : (26, "RGB light", True),
    'S_RGBW_LIGHT' : (27, "RGBW light", True),
    'S_COLOR_SENSOR' : (28, "color sensor", True),
    'S_HVAC' : (29, "HVAC", True),
    'S_MULTIMETER' : (30, "multimeter", True),
    'S_SPRINKLER' : (31, "sprinkler", True),
    'S_WATER_LEAK' : (32, "water leak sensor", True),
    'S_SOUND' : (33, "sound sensor", True),
    'S_VIBRATION' : (34, "vibration sensor", True),
    'S_MOISTURE' : (35, "moisture sensor", True),
    'S_INFO' : (36, "LCD", True),
    'S_GAS' : (37, "gas meter", True),
    'S_GPS' : (38, "GPS", True),
    'S_WATER_QUALITY' : (39, "water quality sensor", True),
    'S_CAM' : (52, "camera", True),
    'S_UNK' : (9999, "unknown")
}



def generate_cover_codec(value):
    
    def encoder(v):
        return None
    
    def decoder(p):
        return value
    
    return (encoder, decoder)


def RGB_encoder(value):
    return color.replace('#', '').replace('0x', '').lower()

def RGB_decoder(value):
    return "#" + value[0:6]
    


def RGBW_encoder(value):
    color, level = value
    return color.replace('#', '').replace('0x', '').lower() + format(min(int(level*2.55), 255), '2x')

def RGBW_decoder(value):
    color = "#" + value[0:6]
    level = int(value[6:8], 16) / 255.0
    return (color, level)
    



# id, name, type or codec (encoder, decoder, True), keep_history(ie store the value in a table)
valueTypes = {
    'V_TEMP' : (0 , "temperature", 'float', True),
    'V_HUM' : (1 , "humidity", 'float', True),
    'V_STATUS' : (2 , "state", 'bool', True),
    'V_LIGHT' : (2 , "state", 'bool', True),
    'V_PERCENTAGE' : (3 , "percentage", 'float', True),
    'V_DIMMER' : (3 , "percentage", 'float', True),
    'V_PRESSURE' : (4 , "pressure", 'float', True),
    'V_FORECAST' : (5 , "forecast", 'string', True), # Whether forecast. One of "stable", "sunny", "cloudy", "unstable", "thunderstorm" or "unknown"
    'V_RAIN' : (6 , "rain", 'float', True), # mm
    'V_RAINRATE' : (7 , "rain rate", 'float', True), # mm/h
    'V_WIND' : (8 , "wind", 'float', True), # Windspeed
    'V_GUST' : (9 , "gust", 'float', True), # Windspeed
    'V_DIRECTION' : (10, "wind direction", 'float', True), # Wind direction 0-360 (degrees)    
    'V_UV' : (11, "UV", 'float', True), # UV index
    'V_WEIGHT' : (12, "weight", 'float', True),
    'V_DISTANCE' : (13, "distance", 'float', True),
    'V_IMPEDANCE' : (14, "impedance", 'float', True),
    'V_ARMED' : (15, "armed", 'bool', True),
    'V_TRIPPED' : (16, "tripped", 'bool', True),
    'V_WATT' : (17, "watt", 'float', True),
    'V_KWH' : (18, "KWH", 'float', True), # Accumulated number of KWH for a power meter
    'V_SCENE_ON' : (19, None, 'int', True), # Turn on a scene, the payload contains the scene id
    'V_SCENE_OFF' : (20, None, 'int', True), # Turn off a scene, the payload contains the scene id
    'V_HVAC_FLOW_STATE' : (21, "flow state", 'string', True), # Mode of header. One of "Off", "HeatOn", "CoolOn", or "AutoChangeOver"
    'V_HVAC_SPEED' : (22, "speed", 'string', True), # HVAC/Heater fan speed ("Min", "Normal", "Max", "Auto")
    'V_LIGHT_LEVEL' : (23, "light", 'float', True), # Uncalibrated light level. 0-100%. Use V_LEVEL for light level in lux.
    'V_VAR1' : (24, "var1", '*', True),
    'V_VAR2' : (25, "var2", '*', True),
    'V_VAR3' : (26, "var3", '*', True),
    'V_VAR4' : (27, "var4", '*', True),
    'V_VAR5' : (28, "var5", '*', True),
    'V_UP' : (29, "state", "string", True), # Window covering. Up.
    'V_DOWN' : (30, "state", "string", True), # Window covering. Down.
    'V_STOP' : (31, "state", "string", True), # Window covering. Stop.
    'V_IR_SEND' : (32, None, 'int', True), # Send out an IR-command
    'V_IR_RECEIVE' : (33, "code", 'int', True), # This message contains a received IR-command
    'V_FLOW' : (34, "flow", 'float', True), # Flow of water (in meter)
    'V_VOLUME' : (35, "volume", 'float', True), # Water volume    
    'V_LOCK_STATUS' : (36, "status", 'bool', True), # Set or get lock status. 1=Locked, 0=Unlocked
    'V_LEVEL' : (37, "level", 'float', True),
    'V_VOLTAGE' : (38, "voltage", 'float', True),
    'V_CURRENT' : (39, "current", 'float', True),
    'V_RGB' : (40, "color", (RGB_encoder, RGB_decoder), True), #RGB value transmitted as ASCII hex string (I.e "ff0000" for red)    
    'V_RGBW' : (41, ("color", "level"), (RGBW_encoder, RGBW_decoder), True), # RGBW value transmitted as ASCII hex string (I.e "ff0000ff" for red + green + blue + full white)    
    'V_ID' : (42, "ID", 'string', False),
    'V_UNIT_PREFIX' : (43, "unit", 'string', False), # Allows sensors to send in a string representing the unit prefix to be displayed in GUI. This is not parsed by controller! E.g. cm, m, km, inch.
    'V_HVAC_SETPOINT_COOL' : (44, "cool setpoint", 'float', True),
    'V_HVAC_SETPOINT_HEAT' : (45, "setpoint", 'float', True),
    'V_HVAC_FLOW_MODE' : (46, "flow mode", 'string', True), # Flow mode for HVAC ("Auto", "ContinuousOn", "PeriodicOn")    
    'V_TEXT' : (47, "text", 'string', True),
    'V_CUSTOM' : (48, "custom", '*', True),
    'V_POSITION' : (49, "position", 'string', True), # GPS position and altitude. Payload: latitude;longitude;altitude(m). E.g. "55.722526;13.017972;18"    
    'V_IR_RECORD' : (50, None, 'bool', True),
    'V_PH' : (51, "PH", 'float', True),
    'V_ORP' : (52, "ORP", 'float', True), # Water ORP : redox potential in mV    
    'V_EC': (53, "electric conductivity", 'float', True), # Water electric conductivity uS/cm (microSiemens/cm)    
    'V_VAR' : (54, "reactive power", 'float', True), # Reactive power: volt-ampere reactive (var)    
    'V_VA' : (55, "apparent power", 'float', True), # Apparent power: volt-ampere (VA)    
    'V_POWER_FACTOR' : (56, "power factor", 'float', True) # Ratio of real power to apparent power: floating point value in the range [-1,..,1]
}

def decode_payload(value_type, payload):
    
    meta = valueTypes[value_type]
    codec = meta[5]
    
    if codec:
        return codec[1](payload)
    else:
        # default:
        type = meta[4]
        
        # number
        if type == 'float' :
            return float(payload)
        if type == 'int' :
            return int(payload)
        # bool
        if type == 'bool' :
            return payload == '1'
        
        return payload

def encode_payload(value_type, value):
    
    meta = valueTypes[value_type]
    codec = meta[5]
    
    if codec:
        return codec[0](value)
    else:
        # default:
        type = meta[4]
        
        # bool
        if type == 'bool' :
            return '1' if value else '0'
        
        if value is None:
            return ''
        
        return str(value)
    

internalTypes = {
    'I_BATTERY_LEVEL' : 0,
    'I_TIME' : 1,
    'I_VERSION' : 2,
    'I_ID_REQUEST' : 3,
    'I_ID_RESPONSE' : 4,
    'I_INCLUSION_MODE' : 5,
    'I_CONFIG' : 6,
    'I_FIND_PARENT' : 7,
    'I_FIND_PARENT_RESPONSE' : 8,
    'I_LOG_MESSAGE' : 9,
    'I_CHILDREN' : 10,
    'I_SKETCH_NAME' : 11,
    'I_SKETCH_VERSION' : 12,
    'I_REBOOT' : 13,
    'I_GATEWAY_READY' : 14,
    'I_SIGNING_PRESENTATION' : 15,
    'I_NONCE_REQUEST' : 16,
    'I_NONCE_RESPONSE' : 17,
    'I_HEARTBEAT_REQUEST' : 18,
    'I_PRESENTATION' : 19,
    'I_DISCOVER_REQUEST' : 20,
    'I_DISCOVER_RESPONSE' : 21,
    'I_HEARTBEAT_RESPONSE' : 22,
    'I_LOCKED' : 23,
    'I_PING' : 24,
    'I_PONG' : 25,
    'I_REGISTRATION_REQUEST' : 26,
    'I_REGISTRATION_RESPONSE' : 27,
    'I_DEBUG' : 28
}

streamTypes = {
    'ST_FIRMWARE_CONFIG_REQUEST' : 0,
    'ST_FIRMWARE_CONFIG_RESPONSE' : 1,
    'ST_FIRMWARE_REQUEST' : 2,
    'ST_FIRMWARE_RESPONSE' : 3,
    'ST_SOUND' : 4,
    'ST_IMAGE' : 5
}


def isSensorTypeStr (sensorType):
    return sensorType in sensorTypes



def isValueTypeStr (valueType):
    return valueType in valueTypes



def sensorTypeStr (sensorType):
    if isinstance(sensorType, integer_types):
        for t in sensorTypes:
            if sensorTypes[t][0] == sensorType:
                return t
    elif isinstance(sensorType, string_types) and sensorType in sensorTypes:
        return sensorType
    



def sensorTypeToName (sensorType):
    
    sensorType = sensorTypeStr(sensorType)
    if sensorType and sensorType in sensorTypes:
        return sensorTypes[sensorType][1]
    
    return sensorTypes['S_UNK'][1]



def valueTypeStr (valueType):
    if isinstance(valueType, integer_types):
        for t in valueTypes:
            if valueTypes[t][0] == valueType:
                return t
        raise ValueError('invalid mysensors value type %d' % valueType)
    else:
        return valueType



def valueTypeToName (valueType):
    
    valueType = valueTypeStr(valueType)
    if valueType and valueType in valueTypes:
        return valueTypes[valueType][1]
    
    return valueType



def streamTypeStr (streamType):
    if isinstance(streamType, integer_types):
        for t in streamTypes:
            if streamTypes[t] == streamType:
                return t
    elif isinstance(streamType, string_types) and streamType in streamTypes:
        return streamType
    



def sensorTypeInt (sensorType):
    if isinstance(sensorType, integer_types):
        return sensorType
    if isinstance(sensorType, string_types) and sensorType in sensorTypes:
        return sensorTypes[sensorType][0]



def valueTypeInt (valueType):
    if isinstance(valueType, integer_types):
        return valueType
    if isinstance(valueType, string_types) and valueType in valueTypes:
        return valueTypes[valueType][0]
    








