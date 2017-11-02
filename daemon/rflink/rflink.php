<?php


require_once __DIR__."/Controller.php";
require_once __DIR__."/SerialController.php";



class RFLink {


	static public function getController($id){
		return \PoolStream::findOne(function($stream) use($id) {
			return ($stream instanceof \Ething\RFLink\Controller) && $stream->gateway->id() === $id;
		});
	}
	
	// $id may also be a resource
	static public function startController($id) {
		global $ething;
		
		if(is_string($id)){
			$device = $ething->get($id);
			if(!($device instanceof \Ething\Device\RFLinkGateway))
				throw new \Exception("the device {$id} does not exist or has the wrong type");
		} else {
			$device = $id;
		}
		
		// remove any previous stream from this device
		static::stopController($device->id());
		
		\Log::info("starting RFLink controller '".$device->name()."' id=".$device->id()." type=".$device->type());
		$controller = new \Ething\RFLink\SerialController($device);
		\PoolStream::add($controller);
		
	}
	
	static public function stopController($id) {
		
		if($controller = static::getController($id)){
			$device = $controller->gateway;
			\Log::info("stopping RFLink controller '".$device->name()."' id=".$device->id()." type=".$device->type());
			$controller->close();
			\PoolStream::remove($controller);
		}
		
	}
	
	static public function init() {
		global $ething;
		
		$devices = $ething->find(array(
			'type' => new \MongoDB\BSON\Regex('^Device\\\\RFLink.*Gateway$')
		));

		foreach($devices as $device){
			static::startController($device);
		}
		
		// auto start/stop controller on device create/remove
		\SignalManager::attachHandler(function($signal) use ($ething) {
			
			if($signal->getName() === 'ResourceMetaUpdated'){
				if(preg_match('/RFLink.*Gateway/', $signal->rType)){
					if(!empty(array_intersect(['port', 'baudrate'], $signal->attributes)))
						\RFLink::startController($signal->resource);
					else {
						if($controller = \RFLink::getController($signal->resource))
							$controller->gateway->refresh();
					}
				}
			} else if($signal->getName() === 'ResourceCreated'){
				if(preg_match('/RFLink.*Gateway/', $signal->rType)) \RFLink::startController($signal->resource);
			} else if($signal->getName() === 'ResourceDeleted'){
				if(preg_match('/RFLink.*Gateway/', $signal->rType)) \RFLink::stopController($signal->resource);
			}
			
		});
		
	}

}




// init
\RFLink::init();




$cli->add('device.rflink.start', function($args, $client) {
	// start to listen to a stream to a RFLink gateway
	if(count($args) != 1)
		throw new Exception('invalid arguments');
	else {
		\RFLink::startController($args[0]);
		$client->success();
	}
});

$cli->add('device.rflink.send', function($args, $client) {
	if(count($args) != 2)
		throw new Exception('invalid arguments');
	else {
		$gatewayId = $args[0];
		$messageStr = \base64_decode($args[1]); // the payload may be binary data or contains space 
		
		if($rflinkController = \RFLink::getController($gatewayId)){
			$rflinkController->send($messageStr, function($error) use ($client) {
				if($error)
					$client->error($error);
				else
					$client->success();
			});
			
		} else {
			throw new Exception("unknown RFLink instance for device id {$gatewayId}");
		}
	}
});

$cli->add('device.rflink.sendWaitResponse', function($args, $client) {
	if(count($args) != 2)
		throw new Exception('invalid arguments');
	else {
		$gatewayId = $args[0];
		$messageStr = \base64_decode($args[1]); // the payload may be binary data or contains space 
		
		if($rflinkController = \RFLink::getController($gatewayId)){
			$rflinkController->send($messageStr, function($error, $messageSent, $response) use ($client) {
				if($error)
					$client->error($error);
				else
					$client->success($response);
			}, true);
			
		} else {
			throw new Exception("unknown RFLink instance for device id {$gatewayId}");
		}
	}
});

$cli->add('device.rflink.end', function($args, $client) {
	if(count($args) != 1)
		throw new Exception('invalid arguments');
	else {
		\RFLink::stopController($args[0]);
		$client->success();
	}
});


