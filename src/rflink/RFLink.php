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
	
	
	
	
};


