<?php



namespace Ething\RFLink;


class RFLink {
	
	static public $specialCtrlCmds = array('OK','REBOOT','PING','PONG','VERSION','RFDEBUG','RFUDEBUG','QRFDEBUG','TRISTATEINVERT','RTSCLEAN','RTSRECCLEAN','RTSSHOW','RTSINVERT','RTSLONGTX');
	
	
	public static $subTypes = array(
		'switch',
		'door',
		'motion',
		'thermometer',
		'weatherStation',
		'multimeter'
	);
	
	static public $switchProtocols = array(
		"X10",
		"Kaku",
		"AB400D",
		"Waveman",
		"EMW200",
		"Impuls",
		"RisingSun",
		"Philips",
		"Energenie",
		"Energenie5",
		"GDR2",
		"NewKaku",
		"HomeEasy",
		"Anslut",
		"Kambrook",
		"Ikea Koppla",
		"PT2262",
		"Lightwave",
		"EMW100",
		"BSB",
		"MDRemote",
		"Conrad",
		"Livolo",
		"TRC02RGB",
		"Aoke",
		"TRC022RGB",
		"Eurodomest",
		"Livolo App",
		"Blyss",
		"Byron",
		"Byron MP",
		"SelectPlus",
		"Doorbell",
		"FA20RF",
		"Chuango",
		"Plieger",
		"SilverCrest",
		"Mertik",
		"HomeConfort",
		"Powerfix",
		"TriState",
		"Deltronic",
		"FA500",
		"HT12E",
		"EV1527",
		"Elmes",
		"Aster",
		"Sartano",
		"Europe",
		"Avidsen",
		"BofuMotor",
		"BrelMotor",
		"RTS",
		"ElroDB",
		"Dooya",
		"Unitec",
		"Maclean",
		"R546",
		"Diya",
		"X10Secure",
		"Atlantic",
		"SilvercrestDB",
		"MedionDB",
		"VMC",
		"Keeloq",
		"CustomSwitch",
		"GeneralSwitch",
		"Koch",
		"Kingpin",
		"Funkbus",
		"Nice",
		"Forest",
		"MC145026",
		"Lobeco",
		"Friedland",
		"BFT",
		"Novatys",
		"Halemeier",
		"Gaposa",
		"MiLightv1",
		"MiLightv2",
		"HT6P20",
		"Doitrand",
		"Warema",
		"Ansluta",
		"Livcol",
		"Bosch",
		"Ningbo",
		"Ditec",
		"Steffen",
		"AlectoSA",
		"GPIOset",
		"KonigSec",
		"RM174RF",
		"Liwin",
		"YW_Secu",
		"Mertik_GV60",
		"Ningbo64",
		"X2D",
		"HRCMotor",
		"Velleman",
		"RFCustom",
		"YW_Sensor",
		"LEGRANDCAD",
		"SysfsGpio"
	);
	
	
	static public $switchCmds = array(
		"ON",
		"OFF",
		"ALLON",
		"ALLOFF",
		"DIM",
		"BRIGHT",
		"UP",
		"DOWN",
		"STOP",
		"COLOR",
		"DISCO+",
		"DISCO-"
	);
	
	static public $attrMap = array(
		'CMD' => array("status", "convertCmd"),
		'KWATT' => array("watt", "convertKWatt"),
		'WATT' => array("watt", "convertWatt"),
		'CURRENT' => array("current", "convertCurrent"),
		'CURRENT2' => array("current", "convertCurrent"),
		'CURRENT3' => array("current", "convertCurrent"),
		'VOLT' => array("voltage", "convertVoltage"),
		'FREQ' => array("frequency", "convertFreq"),
		'PF' => array("power factor", "convertPowerFactor"),
		'ENERGY' => array("energy", "convertEnergy"),
		'TEMP' => array("temperature", "convertTemperature"),
		'HUM' => array("humidity", "convertHum"),
		'BARO' => array("pressure", "convertBaro"),
		'UV' => array("UV", "convertUV"),
		'RAIN' => array("rain", "convertRain"),
		'RAINRATE' => array("rain rate", "convertRainRate"),
		'WINSP' => array("wind", "convertWindSpeed"),
		'AWINSP' => array("average wind", "convertWindSpeed"),
		'WINGS' => array("gust", "convertWindGust"),
		'WINDIR' => array("wind direction", "convertWindDirection"),
		'WINCHL' => array("wind chill", "convertTemperature"), // wind chill
		'WINTMP' => array("wind temperature", "convertTemperature"), // Wind meter temperature reading
		'LUX' => array("lux", "convertLux"),
		'HSTATUS' => array("status", "convertHygroStatus"), //  => array(0=Normal, 1=Comfortable, 2=Dry, 3=Wet
		'BFORECAST' => array("forecast", "convertForecast") // => array(0=No Info/Unknown, 1=Sunny, 2=Partly Cloudy, 3=Cloudy, 4=Rain
	);
	
	static public function getAttrName($attr){
		return array_key_exists($attr, static::$attrMap) ? static::$attrMap[$attr][0] : $attr;
	}
	
	static public function convertAttrValue($attr, $value){
		if(array_key_exists($attr, static::$attrMap)){
			if(!empty(static::$attrMap[$attr][1]))
				return call_user_func(__NAMESPACE__.'\\RFLink::'.static::$attrMap[$attr][1], $value);
		}
		return $value;
	}
	
	static public function getSubType($protocol, array $args){
		
		if($protocol === 'Debug') return;
		
		$keys = array_keys($args);
		
		if(empty($keys)) return;
		
		// 20;83;Oregon Rain2;ID=2a19;RAIN=002a;RAINTOT=0054;BAT=OK;
		if(!empty(array_intersect($keys, array('RAIN','RAINRATE','WINSP','AWINSP','WINGS','WINDIR','WINCHL','WINTMP','UV','LUX','HSTATUS','BFORECAST')))){
			// generic Weather Station
			return 'weatherStation';
		}
		
		// 20;1F;OregonV1;ID=000A;TEMP=00cd;BAT=LOW;
		if(isset($args['ID']) && isset($args['TEMP'])){
			// generic thermometer
			return 'thermometer';
		}
		
		// 20;12;NewKaku;ID=000002;SWITCH=2;CMD=OFF;
		if(empty(array_diff(array('ID', 'SWITCH', 'CMD'), $keys))){
			if(in_array($args['CMD'], array('ON', 'OFF', 'ALLON', 'ALLOFF'))){
				// generic switch
				return 'switch';
			}
		}
		
		if(!empty(array_intersect($keys, array('KWATT','WATT','CURRENT','CURRENT2','CURRENT3','VOLT','FREQ','PF','ENERGY')))){
			// generic Weather Station
			return 'multimeter';
		}
		
		return; // unknow !
	}
	
	
	
	static public function convertSwitchId($value){
		// remove leading 0
		$value = ltrim($value, '0');
		if(strlen($value)===0) $value = '0';
		return $value;
	}
	
	static public function convertCmd($value){
		return boolval(is_string($value) ? preg_match('/^on$/i', $value) : $value);
	}
	
	static public function convertTemperature($value){
		$value = hexdec($value);
		if($value & 0x8000){
			// negative value
			$value &= 0x7FFF;
			$value = -$value;
		}
		$value /= 10;
		return $value;
	}
	
	static public function convertBaro($value){
		return hexdec($value);
	}
	
	static public function convertHum($value){
		return intval($value);
	}
	
	static public function convertUV($value){
		return hexdec($value);
	}
	
	static public function convertLux($value){
		return hexdec($value);
	}
	
	static public function convertRain($value){
		$value = hexdec($value);
		$value /= 10;
		return $value; // in mm
	}
	
	static public function convertRainRate($value){
		$value = hexdec($value);
		$value /= 10;
		return $value; // in mm/h
	}
	
	static public function convertWindSpeed($value){
		$value = hexdec($value);
		$value /= 10;
		return $value; // in km. p/h
	}
	
	static public function convertWindGust($value){
		return hexdec($value); // km. p/h
	}
	
	static public function convertWindDirection($value){
		$value = intval($value);
		return $value * 22.5; // degrees 
	}
	
	static public function convertWatt($value){
		return hexdec($value) / 10; // watt
	}
	
	static public function convertKWatt($value){
		return static::convertWatt($value) * 1000; // watt
	}
	
	static public function convertCurrent($value){
		return hexdec($value) / 10; // A
	}
	
	static public function convertVoltage($value){
		return hexdec($value) / 10; // V
	}
	
	static public function convertFreq($value){
		return hexdec($value); // Hz
	}
	
	static public function convertPowerFactor($value){
		$value = hexdec($value);
		if($value & 0x8000){
			// negative value
			$value &= 0x7FFF;
			$value = -$value;
		}
		return $value / 100;
	}
	
	static public function convertEnergy($value){
		return hexdec($value) / 10; // units watt-hours
	}
	
	static public function convertForecast($value){
		switch($value){
			case '1':
				return 'sunny';
			case '2':
				return 'partly cloudy';
			case '3':
				return 'cloudy';
			case '4':
				return 'rain';
		}
		return 'unknown';
	}
	
	static public function convertHygroStatus($value){
		switch($value){
			case '0':
				return 'normal';
			case '1':
				return 'confortable';
			case '2':
				return 'dry';
			case '3':
				return 'wet';
		}
		return 'unknown';
	}
	
	static public function convertBattery($value){
		switch($value){
			case 'OK':
				return 90;
			case 'LOW':
				return 10;
		}
		return null;
	}
};


