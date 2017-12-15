<?php


namespace Ething\Zigate;


class Zigate {
	
	
	static public $clusterNames = array(
		"0000" => "General: Basic",
		"0001" => "General: Power Config",
		"0002" => "General: Temperature Config",
		"0003" => "General: Identify",
		"0004" => "General: Groups",
		"0005" => "General: Scenes",
		"0006" => "General: On/Off",
		"0007" => "General: On/Off Config",
		"0008" => "General: Level Control",
		"0009" => "General: Alarms",
		"000A" => "General: Time",
		"000F" => "General: Binary Input Basic",
		"0020" => "General: Poll Control",
		"0019" => "General: OTA",
		"0101" => "General: Door Lock",
		"0201" => "HVAC: Thermostat",
		"0202" => "HVAC: Fan Control",
		"0300" => "Lighting: Color Control",
		"0400" => "Measurement: Illuminance",
		"0402" => "Measurement: Temperature",
		"0406" => "Measurement: Occupancy Sensing",
		"0500" => "Security & Safety: IAS Zone",
		"0702" => "Smart Energy: Metering",
		"0B05" => "Misc: Diagnostics",
		"1000" => "ZLL: Commissioning"
	);
	
	static public function clusterIdToName($cluster) {
		return isset(Zigate::$clusterNames[$cluster]) ? Zigate::$clusterNames[$cluster] : '';
	}
	
	static public function modelToClassInfo($model) {
		
		if($model === 'lumi.weather'){
			return array(
				'class' => 'ZigateAqaraTHP',
				'name' => 'thermometer himidity pressure sensor'
			);
		}
		
		return null;
	}
	
	
	
};


