<?php


namespace Ething\MySensors;


class MySensors {
	
	const BROADCAST_ADDRESS				= 255;
	const GATEWAY_ADDRESS				= 0;
	const INTERNAL_CHILD				= 255; // 0xFF
	
	
	// type
	const PRESENTATION = 0;
	const SET = 1;
	const REQ = 2;
	const INTERNAL = 3;
	const STREAM = 4;
	
	// presentation subtype
	const S_DOOR =                  0 ;
    const S_MOTION =                1 ;
    const S_SMOKE =                 2 ;
    const S_LIGHT =                 3 ;
	const S_BINARY =                3 ;
    const S_DIMMER =                4 ;
    const S_COVER =                 5 ;
    const S_TEMP =                  6 ;
    const S_HUM =                   7 ;
    const S_BARO =                  8 ;
    const S_WIND =                  9 ;
    const S_RAIN =                  10;
    const S_UV =                    11;
    const S_WEIGHT =                12;
    const S_POWER =                 13;
    const S_HEATER =                14;
    const S_DISTANCE =              15;
    const S_LIGHT_LEVEL =           16;
    const S_ARDUINO_NODE =          17;
    const S_ARDUINO_REPEATER_NODE = 18;
    const S_LOCK =                  19;
    const S_IR =                    20;
    const S_WATER =                 21;
    const S_AIR_QUALITY =           22;
    const S_CUSTOM =                23;
    const S_DUST =                  24;
    const S_SCENE_CONTROLLER =      25;
    const S_RGB_LIGHT =             26;
    const S_RGBW_LIGHT =            27;
    const S_COLOR_SENSOR =          28;
    const S_HVAC =                  29;
    const S_MULTIMETER =            30;
    const S_SPRINKLER =             31;
    const S_WATER_LEAK =            32;
    const S_SOUND =                 33;
    const S_VIBRATION =             34;
    const S_MOISTURE =              35;
    const S_INFO =                  36;
    const S_GAS =                   37;
    const S_GPS =                   38;
    const S_WATER_QUALITY =         39;
	// extra
	const S_CAM =                   52;
	const S_UNK =                   9999 ;
	
	// set/req subtype
	const V_TEMP               = 0 ;
	const V_HUM                = 1 ;
	const V_STATUS             = 2 ;
	const V_LIGHT              = 2 ;
	const V_PERCENTAGE         = 3 ;
	const V_DIMMER             = 3 ;
	const V_PRESSURE           = 4 ;
	const V_FORECAST           = 5 ;
	const V_RAIN               = 6 ;
	const V_RAINRATE           = 7 ;
	const V_WIND               = 8 ;
	const V_GUST               = 9 ;
	const V_DIRECTION          = 10;
	const V_UV                 = 11;
	const V_WEIGHT             = 12;
	const V_DISTANCE           = 13;
	const V_IMPEDANCE          = 14;
	const V_ARMED              = 15;
	const V_TRIPPED            = 16;
	const V_WATT               = 17;
	const V_KWH                = 18;
	const V_SCENE_ON           = 19;
	const V_SCENE_OFF          = 20;
	const V_HVAC_FLOW_STATE    = 21;
	const V_HVAC_SPEED         = 22;
	const V_LIGHT_LEVEL        = 23;
	const V_VAR1               = 24;
	const V_VAR2               = 25;
	const V_VAR3               = 26;
	const V_VAR4               = 27;
	const V_VAR5               = 28;
	const V_UP                 = 29;
	const V_DOWN               = 30;
	const V_STOP               = 31;
	const V_IR_SEND            = 32;
	const V_IR_RECEIVE         = 33;
	const V_FLOW               = 34;
	const V_VOLUME             = 35;
	const V_LOCK_STATUS        = 36;
	const V_LEVEL              = 37;
	const V_VOLTAGE            = 38;
	const V_CURRENT            = 39;
	const V_RGB                = 40;
	const V_RGBW               = 41;
	const V_ID                 = 42;
	const V_UNIT_PREFIX        = 43;
	const V_HVAC_SETPOINT_COOL = 44;
	const V_HVAC_SETPOINT_HEAT = 45;
	const V_HVAC_FLOW_MODE     = 46;
	const V_TEXT               = 47;
	const V_CUSTOM             = 48;
	const V_POSITION           = 49;
	const V_IR_RECORD          = 50;
	const V_PH                 = 51;
	const V_ORP                = 52;
	const V_EC                 = 53;
	const V_VAR                = 54;
	const V_VA                 = 55;
	const V_POWER_FACTOR       = 56;
	
	// internal subtype
	const I_BATTERY_LEVEL         = 0 ;
	const I_TIME                  = 1 ;
	const I_VERSION               = 2 ;
	const I_ID_REQUEST            = 3 ;
	const I_ID_RESPONSE           = 4 ;
	const I_INCLUSION_MODE        = 5 ;
	const I_CONFIG                = 6 ;
	const I_FIND_PARENT           = 7 ;
	const I_FIND_PARENT_RESPONSE  = 8 ;
	const I_LOG_MESSAGE           = 9 ;
	const I_CHILDREN              = 10;
	const I_SKETCH_NAME           = 11;
	const I_SKETCH_VERSION        = 12;
	const I_REBOOT                = 13;
	const I_GATEWAY_READY         = 14;
	const I_SIGNING_PRESENTATION  = 15;
	const I_NONCE_REQUEST         = 16;
	const I_NONCE_RESPONSE        = 17;
	const I_HEARTBEAT_REQUEST     = 18;
	const I_PRESENTATION          = 19;
	const I_DISCOVER_REQUEST      = 20;
	const I_DISCOVER_RESPONSE     = 21;
	const I_HEARTBEAT_RESPONSE    = 22;
	const I_LOCKED                = 23;
	const I_PING                  = 24;
	const I_PONG                  = 25;
	const I_REGISTRATION_REQUEST  = 26;
	const I_REGISTRATION_RESPONSE = 27;
	const I_DEBUG                 = 28;
	
	// stream subtype
	const ST_FIRMWARE_CONFIG_REQUEST  = 0;  //!< Request new FW, payload contains current FW details
	const ST_FIRMWARE_CONFIG_RESPONSE = 1;  //!< New FW details to initiate OTA FW update
	const ST_FIRMWARE_REQUEST         = 2;  //!< Request FW block
	const ST_FIRMWARE_RESPONSE        = 3;  //!< Response FW block
	const ST_SOUND                    = 4;  //!< Sound
	const ST_IMAGE                    = 5;  //!< Image
	
	
	
	const NO_ACK                 = 0;
	const REQUEST_ACK            = 1;
	const IS_ACK                 = 1;
	
	static public $messageTypes = array(
		'PRESENTATION' => 0,
		'SET' => 1,
		'REQ' => 2,
		'INTERNAL' => 3,
		'STREAM' => 4
	);
	
	static public $sensorTypes = array(
		'S_DOOR' => 0 ,
		'S_MOTION' => 1 ,
		'S_SMOKE' => 2 ,
		'S_BINARY' => 3 ,
		'S_LIGHT' => 3 ,
		'S_DIMMER' => 4 ,
		'S_COVER' => 5 ,
		'S_TEMP' => 6 ,
		'S_HUM' => 7 ,
		'S_BARO' => 8 ,
		'S_WIND' => 9 ,
		'S_RAIN' => 10,
		'S_UV' => 11,
		'S_WEIGHT' => 12,
		'S_POWER' => 13,
		'S_HEATER' => 14,
		'S_DISTANCE' => 15,
		'S_LIGHT_LEVEL' => 16,
		'S_ARDUINO_NODE' => 17,
		'S_ARDUINO_REPEATER_NODE' => 18,
		'S_LOCK' => 19,
		'S_IR' => 20,
		'S_WATER' => 21,
		'S_AIR_QUALITY' => 22,
		'S_CUSTOM' => 23,
		'S_DUST' => 24,
		'S_SCENE_CONTROLLER' => 25,
		'S_RGB_LIGHT' => 26,
		'S_RGBW_LIGHT' => 27,
		'S_COLOR_SENSOR' => 28,
		'S_HVAC' => 29,
		'S_MULTIMETER' => 30,
		'S_SPRINKLER' => 31,
		'S_WATER_LEAK' => 32,
		'S_SOUND' => 33,
		'S_VIBRATION' => 34,
		'S_MOISTURE' => 35,
		'S_INFO' => 36,
		'S_GAS' => 37,
		'S_GPS' => 38,
		'S_WATER_QUALITY' => 39,
		'S_CAM' => 52,
		'S_UNK' => 9999
	);
	
	static public $sensorNames = array(
		'S_DOOR' => 'door' ,
		'S_MOTION' => 'motion' ,
		'S_SMOKE' => 'smoke' ,
		'S_BINARY' => 'switch' ,
		'S_LIGHT' => 'light' ,
		'S_DIMMER' => 'dimmer' ,
		'S_COVER' => 'cover' ,
		'S_TEMP' => 'thermometer' ,
		'S_HUM' => 'humidity sensor' ,
		'S_BARO' => 'barometer' ,
		'S_WIND' => 'wind sensor' ,
		'S_RAIN' => 'rain sensor',
		'S_UV' => 'UV sensor',
		'S_WEIGHT' => 'weight sensor',
		'S_POWER' => 'power meter',
		'S_HEATER' => 'heater',
		'S_DISTANCE' => 'distance sensor',
		'S_LIGHT_LEVEL' => 'light',
		'S_ARDUINO_NODE' => 'arduino',
		'S_ARDUINO_REPEATER_NODE' => 'repeater',
		'S_LOCK' => 'locker',
		'S_IR' => 'IR device',
		'S_WATER' => 'water meter',
		'S_AIR_QUALITY' => 'air quality sensor',
		'S_CUSTOM' => 'custom',
		'S_DUST' => 'dust sensor',
		'S_SCENE_CONTROLLER' => 'scene controller',
		'S_RGB_LIGHT' => 'RGB light',
		'S_RGBW_LIGHT' => 'RGBW light',
		'S_COLOR_SENSOR' => 'color sensor',
		'S_HVAC' => 'HVAC',
		'S_MULTIMETER' => 'multimeter',
		'S_SPRINKLER' => 'sprinkler',
		'S_WATER_LEAK' => 'water leak sensor',
		'S_SOUND' => 'sound sensor',
		'S_VIBRATION' => 'vibration sensor',
		'S_MOISTURE' => 'moisture sensor',
		'S_INFO' => 'LCD',
		'S_GAS' => 'gas meter',
		'S_GPS' => 'GPS',
		'S_WATER_QUALITY' => 'water quality sensor',
		'S_CAM' => 'camera',
		'S_UNK' => 'unknown'
	);
	
	static public $valueTypes = array(
		'V_TEMP' => 0 ,
		'V_HUM' => 1 ,
		'V_STATUS' => 2 ,
		'V_LIGHT' => 2 ,
		'V_PERCENTAGE' => 3 ,
		'V_DIMMER' => 3 ,
		'V_PRESSURE' => 4 ,
		'V_FORECAST' => 5 ,
		'V_RAIN' => 6 ,
		'V_RAINRATE' => 7 ,
		'V_WIND' => 8 ,
		'V_GUST' => 9 ,
		'V_DIRECTION' => 10,
		'V_UV' => 11,
		'V_WEIGHT' => 12,
		'V_DISTANCE' => 13,
		'V_IMPEDANCE' => 14,
		'V_ARMED' => 15,
		'V_TRIPPED' => 16,
		'V_WATT' => 17,
		'V_KWH' => 18,
		'V_SCENE_ON' => 19,
		'V_SCENE_OFF' => 20,
		'V_HVAC_FLOW_STATE' => 21,
		'V_HVAC_SPEED' => 22,
		'V_LIGHT_LEVEL' => 23,
		'V_VAR1' => 24,
		'V_VAR2' => 25,
		'V_VAR3' => 26,
		'V_VAR4' => 27,
		'V_VAR5' => 28,
		'V_UP' => 29,
		'V_DOWN' => 30,
		'V_STOP' => 31,
		'V_IR_SEND' => 32,
		'V_IR_RECEIVE' => 33,
		'V_FLOW' => 34,
		'V_VOLUME' => 35,
		'V_LOCK_STATUS' => 36,
		'V_LEVEL' => 37,
		'V_VOLTAGE' => 38,
		'V_CURRENT' => 39,
		'V_RGB' => 40,
		'V_RGBW' => 41,
		'V_ID' => 42,
		'V_UNIT_PREFIX' => 43,
		'V_HVAC_SETPOINT_COOL' => 44,
		'V_HVAC_SETPOINT_HEAT' => 45,
		'V_HVAC_FLOW_MODE' => 46,
		'V_TEXT' => 47,
		'V_CUSTOM' => 48,
		'V_POSITION' => 49,
		'V_IR_RECORD' => 50,
		'V_PH' => 51,
		'V_ORP' => 52,
		'V_EC' => 53,
		'V_VAR' => 54,
		'V_VA' => 55,
		'V_POWER_FACTOR' => 56
	);
	
	static public $internalTypes = array(
		'I_BATTERY_LEVEL' => 0,
		'I_TIME' => 1,
		'I_VERSION' => 2,
		'I_ID_REQUEST' => 3,
		'I_ID_RESPONSE' => 4,
		'I_INCLUSION_MODE' => 5,
		'I_CONFIG' => 6,
		'I_FIND_PARENT' => 7,
		'I_FIND_PARENT_RESPONSE' => 8,
		'I_LOG_MESSAGE' => 9,
		'I_CHILDREN' => 10,
		'I_SKETCH_NAME' => 11,
		'I_SKETCH_VERSION' => 12,
		'I_REBOOT' => 13,
		'I_GATEWAY_READY' => 14,
		'I_SIGNING_PRESENTATION' => 15,
		'I_NONCE_REQUEST' => 16,
		'I_NONCE_RESPONSE' => 17,
		'I_HEARTBEAT_REQUEST' => 18,
		'I_PRESENTATION' => 19,
		'I_DISCOVER_REQUEST' => 20,
		'I_DISCOVER_RESPONSE' => 21,
		'I_HEARTBEAT_RESPONSE' => 22,
		'I_LOCKED' => 23,
		'I_PING' => 24,
		'I_PONG' => 25,
		'I_REGISTRATION_REQUEST' => 26,
		'I_REGISTRATION_RESPONSE' => 27,
		'I_DEBUG' => 28
	);
	
	static public $streamTypes = array(
		'ST_FIRMWARE_CONFIG_REQUEST' => 0,
		'ST_FIRMWARE_CONFIG_RESPONSE' => 1,
		'ST_FIRMWARE_REQUEST' => 2,
		'ST_FIRMWARE_RESPONSE' => 3,
		'ST_SOUND' => 4,
		'ST_IMAGE' => 5
	);
	
	static public function isSensorTypeStr($sensorType){
		return array_key_exists($sensorType, static::$sensorTypes);
	}
	
	static public function isValueTypeStr($valueType){
		return array_key_exists($valueType, static::$valueTypes);
	}
	
	static public function sensorTypeStr($sensorType){
		if(is_int($sensorType) && ($i = array_search($sensorType, static::$sensorTypes, true)) !== false){
			return $i;
		} else if(is_string($sensorType) && array_key_exists($sensorType, static::$sensorTypes)){
			return $sensorType;
		}
	}
	
	static public function sensorTypeToName($sensorType){
		
		$sensorType = static::sensorTypeStr($sensorType);
		if(array_key_exists($sensorType, static::$sensorNames)){
			return static::$sensorNames[$sensorType];
		}
		
		return static::$sensorNames['S_UNK'];
	}
	
	static public function valueTypeStr($valueType){
		if(is_int($valueType) && ($i = array_search($valueType, static::$valueTypes, true)) !== false){
			return $i;
		} else if(is_string($valueType) && array_key_exists($valueType, static::$valueTypes)){
			return $valueType;
		}
	}
	
	static public function streamTypeStr($streamType){
		if(is_int($streamType) && ($i = array_search($streamType, static::$streamTypes, true)) !== false){
			return $i;
		} else if(is_string($streamType) && array_key_exists($streamType, static::$streamTypes)){
			return $streamType;
		}
	}
	
	static public function sensorTypeInt($sensorType){
		if(is_int($sensorType) && false !== array_search($sensorType, static::$sensorTypes, true)){
			return $sensorType;
		} else if(is_string($sensorType) && array_key_exists($sensorType, static::$sensorTypes)){
			return static::$sensorTypes[$sensorType];
		}
	}
	
	static public function valueTypeInt($valueType){
		if(is_int($valueType) && false !== array_search($valueType, static::$valueTypes, true)){
			return $valueType;
		} else if(is_string($valueType) && array_key_exists($valueType, static::$valueTypes)){
			return static::$valueTypes[$valueType];
		}
	}
	
	
	
	
};


