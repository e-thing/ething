<?php

namespace Ething\Event;


class DeviceReachable extends AbstractResourceEvent {
	
	static public function emit(\Ething\Device\Device $resource){
		return new Signal('DeviceReachable', array(
			'resource' => $resource->id()
		));
	}
	
	static public function validate(array &$attributes, array $context){
		$context['onlyTypes'] = array('Device\\Http', 'Device\\RTSP', 'Device\\Denon');
		return parent::validate($attributes, $context);
	}
	
}


