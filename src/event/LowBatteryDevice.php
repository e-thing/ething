<?php

namespace Ething\Event;



class LowBatteryDevice extends Event {
	
	public function __construct(\Ething\Resource $target){
		parent::__construct($target, array(
			'batteryLevel' => $target->battery()
		));
	}
	
	public function description(){
		return "the battery level of the device '{$this->target()->name()}' is under ".\Ething\Device::BATTERY_LOW."% (current: {$this->batteryLevel}%)";
	}
	
	static public function check($resourceTypeName){
		return $resourceTypeName == 'Device';
	}
}


