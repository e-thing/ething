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
		'S_DOOR' => array(0 , "door"),
		'S_MOTION' => array(1 , "motion"),
		'S_SMOKE' => array(2 , "smoke"),
		'S_BINARY' => array(3 , "switch"),
		'S_LIGHT' => array(3 , "light"),
		'S_DIMMER' => array(4 , "dimmer"),
		'S_COVER' => array(5 , "window cover"),
		'S_TEMP' => array(6 , "thermometer"),
		'S_HUM' => array(7 , "humidity sensor"),
		'S_BARO' => array(8 , "barometer"),
		'S_WIND' => array(9 , "wind sensor"),
		'S_RAIN' => array(10, "rain sensor"),
		'S_UV' => array(11, "UV sensor"),
		'S_WEIGHT' => array(12, "weight sensor"),
		'S_POWER' => array(13, "power meter"),
		'S_HEATER' => array(14, "heater device"),
		'S_DISTANCE' => array(15, "distance sensor"),
		'S_LIGHT_LEVEL' => array(16, "light sensor"),
		'S_ARDUINO_NODE' => array(17, "arduino"),
		'S_ARDUINO_REPEATER_NODE' => array(18, "arduino repeater"),
		'S_LOCK' => array(19, "locker"),
		'S_IR' => array(20, "IR device"),
		'S_WATER' => array(21, "water meter"),
		'S_AIR_QUALITY' => array(22, "air quality sensor"),
		'S_CUSTOM' => array(23, "custom"),
		'S_DUST' => array(24, "dust sensor"),
		'S_SCENE_CONTROLLER' => array(25, "scene controller"),
		'S_RGB_LIGHT' => array(26, "RGB light"),
		'S_RGBW_LIGHT' => array(27, "RGBW light"),
		'S_COLOR_SENSOR' => array(28, "color sensor"),
		'S_HVAC' => array(29, "HVAC"),
		'S_MULTIMETER' => array(30, "multimeter"),
		'S_SPRINKLER' => array(31, "sprinkler"),
		'S_WATER_LEAK' => array(32, "water leak sensor"),
		'S_SOUND' => array(33, "sound sensor"),
		'S_VIBRATION' => array(34, "vibration sensor"),
		'S_MOISTURE' => array(35, "moisture sensor"),
		'S_INFO' => array(36, "LCD"),
		'S_GAS' => array(37, "gas meter"),
		'S_GPS' => array(38, "GPS"),
		'S_WATER_QUALITY' => array(39, "water quality sensor"),
		'S_CAM' => array(52, "camera"),
		'S_UNK' => array(9999, "unknown")
	);
	
	static public $valueTypes = array(
		'V_TEMP' => array(0 , "temperature"),
		'V_HUM' => array(1 , "humidity"),
		'V_STATUS' => array(2 , "status"),
		'V_LIGHT' => array(2 , "status"),
		'V_PERCENTAGE' => array(3 , "percentage"),
		'V_DIMMER' => array(3 , "percentage"),
		'V_PRESSURE' => array(4 , "pressure"),
		'V_FORECAST' => array(5 , "forecast"), // Whether forecast. One of "stable", "sunny", "cloudy", "unstable", "thunderstorm" or "unknown"
		'V_RAIN' => array(6 , "rain"),
		'V_RAINRATE' => array(7 , "rain rate"),
		'V_WIND' => array(8 , "wind"), // Windspeed
		'V_GUST' => array(9 , "gust"),
		'V_DIRECTION' => array(10, "wind direction"), // Wind direction 0-360 (degrees)	
		'V_UV' => array(11, "UV"),
		'V_WEIGHT' => array(12, "weight"),
		'V_DISTANCE' => array(13, "distance"),
		'V_IMPEDANCE' => array(14, "impedance"),
		'V_ARMED' => array(15, "armed"),
		'V_TRIPPED' => array(16, "tripped"),
		'V_WATT' => array(17, "watt"),
		'V_KWH' => array(18, "KWH"), // Accumulated number of KWH for a power meter
		'V_SCENE_ON' => array(19, "scene on"), // Turn on a scene
		'V_SCENE_OFF' => array(20, "scene off"), // Turn off a scene
		'V_HVAC_FLOW_STATE' => array(21, "HVAC flow state"), // Mode of header. One of "Off", "HeatOn", "CoolOn", or "AutoChangeOver"
		'V_HVAC_SPEED' => array(22, "HVAC speed"), // HVAC/Heater fan speed ("Min", "Normal", "Max", "Auto")
		'V_LIGHT_LEVEL' => array(23, "light percentage"), // Uncalibrated light level. 0-100%. Use V_LEVEL for light level in lux.
		'V_VAR1' => array(24, "var1"),
		'V_VAR2' => array(25, "var2"),
		'V_VAR3' => array(26, "var3"),
		'V_VAR4' => array(27, "var4"),
		'V_VAR5' => array(28, "var5"),
		'V_UP' => array(29, "shutter up"), // Window covering. Up.
		'V_DOWN' => array(30, "shutter down"), // Window covering. Down.
		'V_STOP' => array(31, "shutter stop"), // Window covering. Stop.
		'V_IR_SEND' => array(32, "sent IR"), // Send out an IR-command
		'V_IR_RECEIVE' => array(33, "received IR"), // This message contains a received IR-command	
		'V_FLOW' => array(34, "flow"), // Flow of water (in meter)	
		'V_VOLUME' => array(35, "volume"), // Water volume	
		'V_LOCK_STATUS' => array(36, "status"), // Set or get lock status. 1=Locked, 0=Unlocked	
		'V_LEVEL' => array(37, "level"),
		'V_VOLTAGE' => array(38, "voltage"),
		'V_CURRENT' => array(39, "current"),
		'V_RGB' => array(40, "RGB"), //RGB value transmitted as ASCII hex string (I.e "ff0000" for red)	
		'V_RGBW' => array(41, "RGBW"), // RGBW value transmitted as ASCII hex string (I.e "ff0000ff" for red + full white)	
		'V_ID' => array(42, "ID"),
		'V_UNIT_PREFIX' => array(43, "unit"), // Allows sensors to send in a string representing the unit prefix to be displayed in GUI. This is not parsed by controller! E.g. cm, m, km, inch.
		'V_HVAC_SETPOINT_COOL' => array(44, "HVAC cold setpoint"),
		'V_HVAC_SETPOINT_HEAT' => array(45, "HVAC setpoint"),
		'V_HVAC_FLOW_MODE' => array(46, "HVAC flow mode"), // Flow mode for HVAC ("Auto", "ContinuousOn", "PeriodicOn")	
		'V_TEXT' => array(47, "text"),
		'V_CUSTOM' => array(48, "custom"),
		'V_POSITION' => array(49, "position"), // GPS position and altitude. Payload: latitude;longitude;altitude(m). E.g. "55.722526;13.017972;18"	
		'V_IR_RECORD' => array(50, "IR record"),
		'V_PH' => array(51, "PH"),
		'V_ORP' => array(52, "ORP"), // Water ORP : redox potential in mV	
		'V_EC' => array(53, "electric conductivity"), // Water electric conductivity μS/cm (microSiemens/cm)	
		'V_VAR' => array(54, "reactive power"), // Reactive power: volt-ampere reactive (var)	
		'V_VA' => array(55, "apparent power"), // Apparent power: volt-ampere (VA)	
		'V_POWER_FACTOR' => array(56, "power factor") // Ratio of real power to apparent power: floating point value in the range [-1,..,1]
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
		if(is_int($sensorType)){
			foreach(static::$sensorTypes as $type => $item){
				if($item[0] === $sensorType) return $type;
			}
		} else if(is_string($sensorType) && array_key_exists($sensorType, static::$sensorTypes)){
			return $sensorType;
		}
	}
	
	static public function sensorTypeToName($sensorType){
		
		$sensorType = static::sensorTypeStr($sensorType);
		if(array_key_exists($sensorType, static::$sensorTypes)){
			return static::$sensorTypes[$sensorType][1];
		}
		
		return static::$sensorTypes['S_UNK'][1];
	}
	
	static public function valueTypeStr($valueType){
		if(is_int($valueType)){
			foreach(static::$valueTypes as $type => $item){
				if($item[0] === $valueType) return $type;
			}
		} else if(is_string($valueType) && array_key_exists($valueType, static::$valueTypes)){
			return $valueType;
		}
	}
	
	static public function valueTypeToName($valueType){
		
		$valueType = static::valueTypeStr($valueType);
		if(array_key_exists($valueType, static::$valueTypes)){
			return static::$valueTypes[$valueType][1];
		}
		
		return $valueType;
	}
	
	static public function streamTypeStr($streamType){
		if(is_int($streamType) && ($i = array_search($streamType, static::$streamTypes, true)) !== false){
			return $i;
		} else if(is_string($streamType) && array_key_exists($streamType, static::$streamTypes)){
			return $streamType;
		}
	}
	
	static public function sensorTypeInt($sensorType){
		if(is_int($valueType)) return $valueType;
		if(is_string($sensorType) && array_key_exists($sensorType, static::$sensorTypes)){
			return static::$sensorTypes[$sensorType][0];
		}
	}
	
	static public function valueTypeInt($valueType){
		if(is_int($valueType)) return $valueType;
		if(is_string($valueType) && array_key_exists($valueType, static::$valueTypes)){
			return static::$valueTypes[$valueType][0];
		}
	}
	
	
	
	
};


