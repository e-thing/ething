<?php

namespace Ething\Event;


class DeviceDisconnected extends AbstractResourceEvent {
	
	static public function emit(\Ething\Device\Device $resource){
		return new Signal('DeviceDisconnected', array(
			'resource' => $resource->id()
		));
	}
	
	static public function validate(array &$attributes, array $context){
		$context['onlyTypes'] = array('Device\\MySensorsEthernetGateway', 'Device\\MySensorsSerialGateway', 'Device\\RFLinkSerialGateway', 'Device\\MQTT', 'Device\\YeelightBulbRGBW');
		return parent::validate($attributes, $context);
	}
	
}


