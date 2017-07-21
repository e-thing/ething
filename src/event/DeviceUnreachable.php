<?php

namespace Ething\Event;


class DeviceUnreachable extends AbstractResourceEvent {
	
	static public function emit(\Ething\Device\Device $resource){
		return new Signal('DeviceUnreachable', array(
			'resource' => $resource->id()
		));
	}
	
	static public function validate(array &$attributes, array $context){
		$context['onlyTypes'] = array('Device\\Http', 'Device\\RTSP');
		return parent::validate($attributes, $context);
	}
	
}


