<?php

require_once __DIR__."/Controller.php";
require_once __DIR__."/SerialController.php";


class Zigate {

	
	static public function instanciateController($device){
		/*if($device instanceof \Ething\Device\ZigateEthernetGateway){
			return new \Ething\Zigate\EthernetController($device);
		} else */if ($device instanceof \Ething\Device\ZigateSerialGateway){
			return new \Ething\Zigate\SerialController($device);
		} else {
			\Log::error("unable to instanciate the Zigate controller");
			return null;
		}
	}
	
	static public function getController($id){
		return \PoolStream::findOne(function($stream) use($id) {
			return ($stream instanceof \Ething\Zigate\Controller) && $stream->gateway->id() === $id;
		});
	}
	
	// $id may also be a resource
	static public function startController($id) {
		global $ething;
		
		if(is_string($id)){
			$device = $ething->get($id);
			if(!($device instanceof \Ething\Device\ZigateGateway))
				throw new \Exception("the device {$id} does not exist or has the wrong type");
		} else {
			$device = $id;
		}
		
		// remove any previous stream from this device
		static::stopController($device->id());
		
		if($controller = static::instanciateController($device)){
			\Log::info("starting Zigate controller '".$device->name()."' id=".$device->id()." type=".$device->type());
			\PoolStream::add($controller);
		} else {
			throw new \Exception("unable to instanciate the Zigate controller");
		}
		
	}
	
	static public function stopController($id) {
		
		if($controller = static::getController($id)){
			$device = $controller->gateway;
			\Log::info("stopping Zigate controller '".$device->name()."' id=".$device->id()." type=".$device->type());
			$controller->close();
			\PoolStream::remove($controller);
		}
		
	}
	
	static public function init() {
		global $ething;
		
		$devices = $ething->find(array(
			'type' => new \MongoDB\BSON\Regex('^Device\\\\Zigate.*Gateway$')
		));

		foreach($devices as $device){
			static::startController($device);
		}
		
		// auto start/stop controller on device create/remove
		\SignalManager::attachHandler(function($signal) use ($ething) {
			
			if($signal->getName() === 'ResourceMetaUpdated'){
				if(preg_match('/Zigate.*Gateway/', $signal->rType)){
					if(!empty(array_intersect(['port', 'baudrate', 'address'], $signal->attributes)))
						\Zigate::startController($signal->resource);
					else {
						if($controller = \Zigate::getController($signal->resource))
							$controller->gateway->refresh();
					}
				}
			} else if($signal->getName() === 'ResourceCreated'){
				if(preg_match('/Zigate.*Gateway/', $signal->rType)) \Zigate::startController($signal->resource);
			} else if($signal->getName() === 'ResourceDeleted'){
				if(preg_match('/Zigate.*Gateway/', $signal->rType)) \Zigate::stopController($signal->resource);
			}
			
		});
		
	}

}




// init
\Zigate::init();





$cli->add('device.zigate.start', function($args, $client) {
	// start to listen to a stream to a Zigate gateway
	if(count($args) != 1)
		throw new Exception('invalid arguments');
	else {
		\Zigate::startController($args[0]);
		$client->success();
	}
});

$cli->add('device.zigate.send', function($args, $client) {
	if(count($args) != 3)
		throw new Exception('invalid arguments');
	else {
		$gatewayId = $args[0];
		$type = $args[1];
		$payload = $args[2];
		
		if($ontroller = \Zigate::getController($gatewayId)){
			$message = new \Ething\Zigate\Message($type, $payload);
			$ontroller->send($message, function($error) use ($client) {
				if($error)
					$client->error($error);
				else
					$client->success();
			});
			
		} else {
			throw new Exception("unknown zigate instance for device id {$gatewayId}");
		}
	}
});

$cli->add('device.zigate.sendWaitResponse', function($args, $client) {
	if(count($args) != 4)
		throw new Exception('invalid arguments');
	else {
		$gatewayId = $args[0];
		$type = $args[1];
		$payload = $args[2];
		$responseId = $args[3];
		
		if($ontroller = \Zigate::getController($gatewayId)){
			$message = new \Ething\Zigate\Message($type, $payload);
			$ontroller->send($message, function($error, $response) use ($client) {
				if($error)
					$client->error($error);
				else
					$client->success($response);
			}, empty($responseId) ? true : $responseId);
			
		} else {
			throw new Exception("unknown zigate instance for device id {$gatewayId}");
		}
	}
});

$cli->add('device.zigate.end', function($args, $client) {
	if(count($args) != 1)
		throw new Exception('invalid arguments');
	else {
		\Zigate::stopController($args[0]);
		$client->success();
	}
});


