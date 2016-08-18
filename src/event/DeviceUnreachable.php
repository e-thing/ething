<?php

namespace Ething\Event;



class DeviceUnreachable extends Event {
	
	
	public function description(){
		return "the device '{$this->target()->name()}' is unreachable";
	}
	
	static public function check($resourceTypeName){
		return $resourceTypeName == 'Device';
	}
}


