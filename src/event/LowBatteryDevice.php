<?php

namespace Ething\Event;

class LowBatteryDevice extends AbstractResourceEvent {
	
	static public function emit(\Ething\Device\Device $resource){
		return new Signal('LowBatteryDevice', array(
			'resource' => $resource->id()
		));
	}
	
	static public function validate(array &$attributes, array $context){
		$context['onlyTypes'] = array('Device\\Device');
		return parent::validate($attributes, $context);
	}
	
}



