<?php


require_once "Client.php";



function mqttGetController($id){
	return PoolStream::findOne(function($stream) use($id) {
		return ($stream instanceof \Ething\MQTT\Client) && $stream->device->id() === $id;
	});
}


// init MQTT clients

$mqttdevices = $ething->find(array(
	'type' => 'Device\\MQTT'
));
foreach($mqttdevices as $mqttdevice){
	
	Log::info("starting mqtt client '".$mqttdevice->name()."' [id=".$mqttdevice->id()."]");
	PoolStream::add(new \Ething\MQTT\Client($mqttdevice));
	
}
unset($mqttdevices);




$cli->add('device.mqtt.start', function($args, $client) use($ething) {
	// start to listen to a stream to a MQTT server
	if(count($args) != 1)
		throw new Exception('invalid arguments');
	else {
		$deviceId = $args[0];
		$mqttdevice = $ething->get($deviceId);
		if(!($mqttdevice instanceof \Ething\Device\MQTT))
			throw new Exception("the device {$deviceId} does not exist or has the wrong type (not MQTT)");
		// remove any previous stream from this device
		if($mqttClient = mqttGetController($deviceId)){
			$mqttClient->close();
			PoolStream::remove($mqttClient);
		}
		if(PoolStream::add(new \Ething\MQTT\Client($mqttdevice)))
			Log::info("starting mqtt client '".$mqttdevice->name()."' [id=".$mqttdevice->id()."]");
		$client->success();
	}
});

$cli->add('device.mqtt.send', function($args, $client) use($ething){
	if(count($args) != 3)
		throw new Exception('invalid arguments');
	else {
		$deviceId = $args[0];
		$topic = $args[1];
		$payload = \base64_decode($args[2]); // the payload may be binary data or contains space 
		$mqttdevice = $ething->get($deviceId);
		if(!($mqttdevice instanceof \Ething\Device\MQTT))
			throw new Exception("the device {$deviceId} does not exist or has the wrong type (not MQTT)");
		
		if($mqttClient = mqttGetController($deviceId)){
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
		$client->success();
		$deviceId = $args[0];
		$mqttdevice = $ething->get($deviceId);
		if(!($mqttdevice instanceof \Ething\Device\MQTT))
			throw new Exception("the device {$deviceId} does not exist or has the wrong type (not MQTT)");
		if($mqttClient = mqttGetController($deviceId)){
			$mqttClient->close();
			PoolStream::remove($mqttClient);
		}
	}
});






require_once 'MqttListener.php';

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
					
					TaskManager::add(new Task(function($device, $operationId, $data){
						$device->call($operationId, null, $data, array());
					}, array($device, $operationId, $data), 0, "device.call"));
					
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


