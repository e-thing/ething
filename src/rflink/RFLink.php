<?php



namespace Ething\RFLink;


class RFLink {
	
	static public $specialCtrlCmds = array('OK','REBOOT','PING','PONG','VERSION','RFDEBUG','RFUDEBUG','QRFDEBUG','TRISTATEINVERT','RTSCLEAN','RTSRECCLEAN','RTSSHOW','RTSINVERT','RTSLONGTX');
	
	
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
	
	
	static public function parseMessage($rawMessage){
		
		$items = array_filter( explode(';', $rawMessage), 'strlen' ); 
		$obj = array( 'raw' => $rawMessage );
		
		
		if(count($items)>0){
			
			$nodeNumber = $obj['type'] = intval(array_shift($items));
			
			if($nodeNumber===20 || $nodeNumber===11){
				// from the RFLink Gateway to the master
				// 20;04;Cresta;ID=3001;TEMP=00b4;HUM=50;BAT=OK;
				$obj['counter'] = intval(array_shift($items), 16);
				
				preg_match('/^([^=]*)(=(.*))?$/', $items[0], $matches);
				
				if(in_array($matches[1], static::$specialCtrlCmds) || isset($matches[2])){
					if(!isset($matches[2]))
						$obj['command'] = $matches[1];
				} else {
					$obj['protocol'] = array_shift($items);
				}
				
				$obj['attr'] = array();
				$i=0;
				foreach($items as $item){
					if( preg_match('/^(.*)=(.*)$/', $item, $matches) ){
						
						$key = $matches[1];
						$value = $matches[2];
						
						if($key==='ID'){
							$obj['id'] = $value;
						}
						
						if( in_array($key, array('TEMP','HUM','BARO','HSTATUS','BFORECAST','UV','LUX','RAIN','RAINRATE','RAINTOT','WINSP','AWINSP','WINGS','WINDIR','WINCHL','WINTMP','CHIME','CO2','SOUND','KWATT','WATT','CURRENT','CURRENT2','CURRENT3','DIST','METER','VOLT')) ){
							// number
							if( in_array($key, array('TEMP','BARO','UV','LUX','RAIN','RAINRATE','RAINTOT','WINSP','AWINSP','WINGS','WINCHL','WINTMP','KWATT','WATT')) ){
								$value = hexdec($value);
							} else {
								$value = intval($value);
							}
							
							if( in_array($key, array('TEMP','RAIN','RAINRATE','RAINTOT','WINSP','AWINSP','WINCHL','WINTMP','AWINSP')) ){
								$value = $value / 10;
							}
						}
						$obj['attr'][$key] = $value;
					} else if(!empty($item)) {
						$obj['attr']['_'.$i++] = $item;
					}
				}
				
			} else if($nodeNumber===10){
				// from the master to the RFLink Gateway
				
				if(in_array($items[0], static::$specialCtrlCmds)){
					// special command !
					$obj['command'] = array_shift($items);
				} else {
					$obj['protocol'] = array_shift($items);
					$obj['address'] = array_shift($items);
					if(count($items)==1){
						$obj['value'] = array_shift($items);
					} else if(count($items)>=2){
						$obj['buttonNumber'] = array_shift($items);
						$obj['value'] = array_shift($items);
					}
				}
				
			} else {
				throw new \Exception("invalid rflink message, bad node number {$nodeNumber}");
			}
			
		} else {
			throw new \Exception("invalid rflink message");
		}
		
		return $obj;
		
	}
	
	
	static public function getClass($protocol, array $args){
		
		if($protocol === 'Debug') return;
		
		$keys = array_keys($args);
		
		if(empty($keys)) return;
		
		// 20;83;Oregon Rain2;ID=2a19;RAIN=002a;RAINTOT=0054;BAT=OK;
		if(!empty(array_intersect($keys, array('RAIN','RAINRATE','WINSP','AWINSP','WINGS','WINDIR','WINCHL','WINTMP','UV','LUX','HSTATUS','BFORECAST')))){
			// generic Weather Station
			return 'Ething\\Device\\RFLinkWeatherStation';
		}
		
		// 20;1F;OregonV1;ID=000A;TEMP=00cd;BAT=LOW;
		if(isset($args['ID']) && isset($args['TEMP'])){
			// generic thermometer
			return 'Ething\\Device\\RFLinkThermometer';
		}
		
		// 20;12;NewKaku;ID=000002;SWITCH=2;CMD=OFF;
		if(empty(array_diff($keys, array('ID', 'SWITCH', 'CMD')))){
			if(in_array($args['CMD'], array('ON', 'OFF', 'ALLON', 'ALLOFF'))){
				// generic switch
				return 'Ething\\Device\\RFLinkSwitch';
			}
		}
		
		if(!empty(array_intersect($keys, array('KWATT','WATT','CURRENT','CURRENT2','CURRENT3','VOLT','FREQ','PF','ENERGY')))){
			// generic Weather Station
			return 'Ething\\Device\\RFLinkMultimeter';
		}
		
		return; // no class found !
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
		return hexdec($value) / 10; // km. p/h
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


