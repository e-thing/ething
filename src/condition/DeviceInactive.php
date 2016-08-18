<?php


namespace Ething\Condition;
	
class DeviceInactive extends Condition {
	
	public $duration;
	
	static public function check(array &$json, $eventName, $resourceTypeName){
		
		if(!(isset($json['duration']) && is_int($json['duration'])))
			throw new \Ething\Exception('invalid value for the field "duration"');
		
		return $resourceTypeName == 'Device';
	}
	
	public function test(\Ething\Event\Event $event){
		$device = $event->target();
		$lastSeenDate = $device->lastSeenDate();
		return $lastSeenDate && (time() - $lastSeenDate) > $this->duration;
	}
	
	public function description(){
		return "the device is inactive for more than {$this->duration} seconds";
	}
	
}


