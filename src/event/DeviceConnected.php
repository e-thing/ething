<?php

namespace Ething\Event;


class DeviceConnected extends AbstractResourceEvent {
	
	static public function emit(\Ething\Device\Device $resource){
		return new Signal('DeviceConnected', array(
			'resource' => $resource->id()
		));
	}
	
	static public function validate(array &$attributes, array $context){
		$context['onlyTypes'] = array('Device\\MySensorsEthernetGateway', 'Device\\MySensorsSerialGateway', 'Device\\RFLinkSerialGateway', 'Device\\MQTT', 'Device\\YeelightBulbRGBW');
		return parent::validate($attributes, $context);
	}
	
}


