<?php

require_once __DIR__."/Controller.php";
require_once __DIR__."/EthernetController.php";
require_once __DIR__."/SerialController.php";


class MySensors {

	
	static public function instanciateController($device){
		if($device instanceof \Ething\Device\MySensorsEthernetGateway){
			return new \Ething\MySensors\EthernetController($device);
		} else if ($device instanceof \Ething\Device\MySensorsSerialGateway){
			return new \Ething\MySensors\SerialController($device);
		} else {
			\Log::error("unable to instanciate the MySensors controller");
			return null;
		}
	}
	
	static public function getController($id){
		return \PoolStream::findOne(function($stream) use($id) {
			return ($stream instanceof \Ething\MySensors\Controller) && $stream->gateway->id() === $id;
		});
	}
	
	// $id may also be a resource
	static public function startController($id) {
		global $ething;
		
		if(is_string($id)){
			$device = $ething->get($id);
			if(!($device instanceof \Ething\Device\MySensorsGateway))
				throw new \Exception("the device {$id} does not exist or has the wrong type");
		} else {
			$device = $id;
		}
		
		// remove any previous stream from this device
		static::stopController($device->id());
		
		if($controller = static::instanciateController($device)){
			\Log::info("starting MySensors controller '".$device->name()."' id=".$device->id()." type=".$device->type());
			\PoolStream::add($controller);
		} else {
			throw new \Exception("unable to instanciate the MySensors controller");
		}
		
	}
	
	static public function stopController($id) {
		
		if($controller = static::getController($id)){
			$device = $controller->gateway;
			\Log::info("stopping MySensors controller '".$device->name()."' id=".$device->id()." type=".$device->type());
			$controller->close();
			\PoolStream::remove($controller);
		}
		
	}
	
	static public function init() {
		global $ething;
		
		$devices = $ething->find(array(
			'type' => new \MongoDB\BSON\Regex('^Device\\\\MySensors.*Gateway$')
		));

		foreach($devices as $device){
			static::startController($device);
		}
		
		// auto start/stop controller on device create/remove
		\SignalManager::attachHandler(function($signal) use ($ething) {
			
			if($signal->getName() === 'ResourceMetaUpdated'){
				if(preg_match('/MySensors.*Gateway/', $signal->rType)){
					if(!empty(array_intersect(['port', 'baudrate', 'address'], $signal->attributes)))
						\MySensors::startController($signal->resource);
					else {
						if($controller = \MySensors::getController($signal->resource))
							$controller->gateway->refresh();
					}
				}
			} else if($signal->getName() === 'ResourceCreated'){
				if(preg_match('/MySensors.*Gateway/', $signal->rType)) \MySensors::startController($signal->resource);
			} else if($signal->getName() === 'ResourceDeleted'){
				if(preg_match('/MySensors.*Gateway/', $signal->rType)) \MySensors::stopController($signal->resource);
			}
			
		});
		
	}

}




// init
\MySensors::init();





$cli->add('device.mysensors.start', function($args, $client) {
	// start to listen to a stream to a MySensors gateway
	if(count($args) != 1)
		throw new Exception('invalid arguments');
	else {
		\MySensors::startController($args[0]);
		$client->success();
	}
});

$cli->add('device.mysensors.send', function($args, $client) {
	if(count($args) != 2)
		throw new Exception('invalid arguments');
	else {
		$gatewayId = $args[0];
		$messageStr = \base64_decode($args[1]); // the payload may be binary data or contains space 
		
		if($mysensorsController = \MySensors::getController($gatewayId)){
			$message = \Ething\MySensors\Message::parse($messageStr);
			$mysensorsController->send($message, function($error) use ($client) {
				if($error)
					$client->error($error);
				else
					$client->success();
			});
			
		} else {
			throw new Exception("unknown mysensors instance for device id {$gatewayId}");
		}
	}
});

$cli->add('device.mysensors.sendWaitResponse', function($args, $client) {
	if(count($args) != 2)
		throw new Exception('invalid arguments');
	else {
		$gatewayId = $args[0];
		$messageStr = \base64_decode($args[1]); // the payload may be binary data or contains space 
		
		if($mysensorsController = \MySensors::getController($gatewayId)){
			$message = \Ething\MySensors\Message::parse($messageStr);
			$mysensorsController->send($message, function($error, $messageSent, $response) use ($client) {
				if($error)
					$client->error($error);
				else
					$client->success($response);
			}, true);
			
		} else {
			throw new Exception("unknown mysensors instance for device id {$gatewayId}");
		}
	}
});

$cli->add('device.mysensors.end', function($args, $client) {
	if(count($args) != 1)
		throw new Exception('invalid arguments');
	else {
		\MySensors::stopController($args[0]);
		$client->success();
	}
});

$cli->add('device.mysensors.updateFirmware', function($args, $client) use($ething){
	if(count($args) != 2)
		throw new Exception('invalid arguments');
	else {
		$nodeId = $args[0];
		$firmware = \base64_decode($args[1]);
		$node = $ething->get($nodeId);
		if(!($node instanceof \Ething\Device\MySensorsNode))
			throw new Exception("the device {$nodeId} does not exist or has the wrong type");
		$gateway = $node->gateway();
		
		if($mysensorsController = \MySensors::getController($gateway->id())){
			
			$mysensorsController->updateFirmware($node, $firmware, function($error) use ($client) {
				if($error)
					$client->error($error);
				else
					$client->success();
			});
			
		} else {
			throw new Exception("unknown mysensors instance for device id {$gateway->id()}");
		}
	}
});
