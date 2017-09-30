<?php


require_once __DIR__."/Client.php";


class MQTT {


	static public function getController($id){
		return \PoolStream::findOne(function($stream) use($id) {
			return ($stream instanceof \Ething\MQTT\Client) && $stream->device->id() === $id;
		});
	}
	
	// $id may also be a resource
	static public function startController($id) {
		global $ething;
		
		if(is_string($id)){
			$device = $ething->get($id);
			if(!($device instanceof \Ething\Device\MQTT))
				throw new \Exception("the device {$id} does not exist or has the wrong type");
		} else {
			$device = $id;
		}
		
		// remove any previous stream from this device
		static::stopController($device->id());
		
		\Log::info("starting MQTT controller '".$device->name()."' id=".$device->id()." type=".$device->type());
		$controller = new \Ething\MQTT\Client($device);
		\PoolStream::add($controller);
		
	}
	
	static public function stopController($id) {
		
		if($controller = static::getController($id)){
			$device = $controller->device;
			\Log::info("stopping MQTT controller '".$device->name()."' id=".$device->id()." type=".$device->type());
			$controller->close();
			\PoolStream::remove($controller);
		}
		
	}
	
	static public function init() {
		global $ething;
		
		$devices = $ething->find(array(
			'type' => 'Device\\MQTT'
		));

		foreach($devices as $device){
			static::startController($device);
		}
		
		// auto start/stop controller on device create/remove
		\SignalManager::attachHandler(function($signal) use ($ething) {
			
			if($signal->getName() === 'ResourceMetaUpdated'){
				if(strpos($signal->rType, 'MQTT') !== false){
					if(!empty(array_intersect(['port', 'host', 'auth', '_subscription'], $signal->attributes)))
						\MQTT::startController($signal->resource);
					else {
						if($controller = \MQTT::getController($signal->resource))
							$controller->device->refresh();
					}
				}
			} else if($signal->getName() === 'ResourceCreated'){
				if(strpos($signal->rType, 'MQTT') !== false) \MQTT::startController($signal->resource);
			} else if($signal->getName() === 'ResourceDeleted'){
				if(strpos($signal->rType, 'MQTT') !== false) \MQTT::stopController($signal->resource);
			}
			
		});
		
	}

}

// init
\MQTT::init();





$cli->add('device.mqtt.start', function($args, $client) {
	// start to listen to a stream to a MQTT server
	if(count($args) != 1)
		throw new Exception('invalid arguments');
	else {
		\MQTT::startController($args[0]);
		$client->success();
	}
});

$cli->add('device.mqtt.send', function($args, $client) {
	if(count($args) != 3)
		throw new Exception('invalid arguments');
	else {
		$deviceId = $args[0];
		$topic = $args[1];
		$payload = \base64_decode($args[2]); // the payload may be binary data or contains space 
		
		if($mqttClient = \MQTT::getController($deviceId)){
			if($mqttClient->publish($topic, $payload)) {
				$client->success();
			} else {
				$client->error('not connected');
			}
			
		} else {
			throw new Exception("unknown mqtt instance for device id {$deviceId}");
		}
	}
});

$cli->add('device.mqtt.end', function($args, $client) use($ething){
	if(count($args) != 1)
		throw new Exception('invalid arguments');
	else {
		\MQTT::stopController($args[0]);
		$client->success();
	}
});






require_once __DIR__.'/MqttListener.php';

try {
	$mqttListener = new MqttListener($ething);
} catch(\Exception $e) {
	$mqttListener = null;
	Log::warn($e);
}

$cli->add('mqtt.publish', function($args, $client) use ($mqttListener){
	if(count($args) != 2 && count($args) != 3)
		throw new Exception('invalid arguments');
	else {
		
		if($mqttListener){
			$client->success();
			
			$topic = $args[0];
			$message = \base64_decode($args[1]);
			$retain = isset($args[2]) ? boolval($args[2]) : false;
			
			$mqttListener->publish($topic, $message, $retain);
		} else {
			$client->error('mqtt feature disabled');
		}
	}
});

if($mqttListener){
	
	Log::info("mqtt enabled");
	
	PoolStream::add($mqttListener);

	$mqttListener->onMessage(function($topic,$message) use ($ething){
		
		//  resource/device/{id}/call/{operationId}
		if(preg_match('@^resource/device/([^/]+)/call/([^/]+)$@', $topic, $matches)){
			$id=$matches[1];
			$operationId=$matches[2];
			
			$device = $ething->get($id);
			if($device && ($device instanceof \Ething\Device\Device)){
				$data = \json_decode($message, true);
				if(\json_last_error() === JSON_ERROR_NONE){
					
					TaskManager::add(new ForkTask(function($device, $operationId, $data){
						$device->call($operationId, null, $data, array());
					}, array($device, $operationId, $data), "device.call"));
					
				}
			}
			
		}
		
		
	});
	
	
	SignalManager::attachHandler(function($signal) use ($ething, $mqttListener) {
		
		$mqttListener->publish("signal/{$signal->getName()}", $signal, false);
		
		if($signal->getName() === "TableDataAdded"){
			$mqttListener->publish("resource/table/{$signal->resource}/data", $signal->data, true);
		} else if($signal->getName() === "DeviceDataSet"){
			foreach($signal->data as $key => $value){
				$mqttListener->publish("resource/device/{$signal->resource}/data/{$key}", $value, true);
			}
		}
	});
}


