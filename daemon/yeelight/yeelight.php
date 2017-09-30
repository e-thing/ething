<?php

require_once __DIR__."/Controller.php";

class Yeelight {


	static public function getController($id){
		return \PoolStream::findOne(function($stream) use($id) {
			return ($stream instanceof \Ething\Yeelight\Controller) && $stream->device->id() === $id;
		});
	}
	
	// $id may also be a resource
	static public function startController($id) {
		global $ething;
		
		if(is_string($id)){
			$device = $ething->get($id);
			if(!($device instanceof \Ething\Device\YeelightDevice))
				throw new \Exception("the device {$id} does not exist or has the wrong type");
		} else {
			$device = $id;
		}
		
		// remove any previous stream from this device
		static::stopController($device->id());
		
		\Log::info("starting Yeelight controller '".$device->name()."' id=".$device->id()." type=".$device->type());
		$controller = new \Ething\Yeelight\Controller($device);
		\PoolStream::add($controller);
		
	}
	
	static public function stopController($id) {
		
		if($controller = static::getController($id)){
			$device = $controller->device;
			\Log::info("stopping Yeelight controller '".$device->name()."' id=".$device->id()." type=".$device->type());
			$controller->close();
			\PoolStream::remove($controller);
		}
		
	}
	
	static public function init() {
		global $ething;
		
		$devices = $ething->find(array(
			'type' => new \MongoDB\BSON\Regex('^Device\\\\Yeelight.*$')
		));

		foreach($devices as $device){
			static::startController($device);
		}
		
		// auto start/stop controller on device create/remove
		\SignalManager::attachHandler(function($signal) use ($ething) {
			
			if($signal->getName() === 'ResourceMetaUpdated'){
				if(strpos($signal->rType, 'Yeelight') !== false){
					if(in_array('host', $signal->attributes))
						\Yeelight::startController($signal->resource);
					else {
						if($controller = \Yeelight::getController($signal->resource))
							$controller->device->refresh();
					}
				}
			} else if($signal->getName() === 'ResourceCreated'){
				if(strpos($signal->rType, 'Yeelight') !== false) \Yeelight::startController($signal->resource);
			} else if($signal->getName() === 'ResourceDeleted'){
				if(strpos($signal->rType, 'Yeelight') !== false) \Yeelight::stopController($signal->resource);
			}
			
		});
		
	}

}




// init
\Yeelight::init();




$cli->add('device.yeelight.start', function($args, $client) {
	// start to listen to a stream to a Yeelight device
	if(count($args) != 1)
		throw new Exception('invalid arguments');
	else {
		\Yeelight::startController($args[0]);
		$client->success();
	}
});

$cli->add('device.yeelight.send', function($args, $client) {
	if(count($args) != 2)
		throw new Exception('invalid arguments');
	else {
		$deviceId = $args[0];
		$message = \json_decode(\base64_decode($args[1]), true); // the payload may be binary data or contains space 
		
		if($yeelightController = \Yeelight::getController($deviceId)){
			$yeelightController->send($message, function($error) use ($client) {
				if($error)
					$client->error($error);
				else
					$client->success();
			});
			
		} else {
			throw new Exception("unknown Yeelight instance for device id {$deviceId}");
		}
	}
});

$cli->add('device.yeelight.sendWaitResponse', function($args, $client) {
	if(count($args) != 2)
		throw new Exception('invalid arguments');
	else {
		$deviceId = $args[0];
		$message = \json_decode(\base64_decode($args[1]), true); // the payload may be binary data or contains space 
		
		if($yeelightController = \Yeelight::getController($deviceId)){
			$yeelightController->send($message, function($error, $messageSent, $response) use ($client) {
				if($error)
					$client->error($error);
				else
					$client->success($response);
			}, true);
			
		} else {
			throw new Exception("unknown Yeelight instance for device id {$deviceId}");
		}
	}
});

$cli->add('device.yeelight.end', function($args, $client) {
	if(count($args) != 1)
		throw new Exception('invalid arguments');
	else {
		\Yeelight::stopController($args[0]);
		$client->success();
	}
});



