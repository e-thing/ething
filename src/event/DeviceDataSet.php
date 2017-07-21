<?php

namespace Ething\Event;

class DeviceDataSet extends AbstractResourceEvent {
	
	static public function emit(\Ething\Device\Device $resource, \stdClass $data){
		return new Signal('DeviceDataSet', array(
			'resource' => $resource->id(),
			'data' => $data
		));
	}
	
	static public function validate(array &$attributes, array $context){
		$context['onlyTypes'] = array('Device\\Device');
		return parent::validate($attributes, $context);
	}
	
	
	
}
