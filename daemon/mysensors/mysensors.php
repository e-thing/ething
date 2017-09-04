<?php

require_once "Controller.php";
require_once "EthernetController.php";
require_once "SerialController.php";



function mysensorsInstanciateController($device){
	if($device instanceof \Ething\Device\MySensorsEthernetGateway){
		return new \Ething\MySensors\EthernetController($device);
	} else if ($device instanceof \Ething\Device\MySensorsSerialGateway){
		return new \Ething\MySensors\SerialController($device);
	} else {
		Log::error("unable to instanciate the controller");
		return null;
	}
}

function mysensorsGetController($id){
	return PoolStream::findOne(function($stream) use($id) {
		return ($stream instanceof \Ething\MySensors\Controller) && $stream->gateway->id() === $id;
	});
}


// init MySensors
$mySensorsGateways = $ething->find(array(
	'type' => new \MongoDB\BSON\Regex('^Device\\\\MySensors.*Gateway$')
));


foreach($mySensorsGateways as $mySensorsGateway){
	
	Log::info("starting mysensors controller '".$mySensorsGateway->name()."' id=".$mySensorsGateway->id()." type=".$mySensorsGateway->type());
	
	if($controller = mysensorsInstanciateController($mySensorsGateway)){
		PoolStream::add($controller);
	}
}

unset($mySensorsGateways);




$cli->add('device.mysensors.start', function($args, $client) use($ething) {
	// start to listen to a stream to a MySensors gateway
	if(count($args) != 1)
		throw new Exception('invalid arguments');
	else {
		$gatewayId = $args[0];
		$gateway = $ething->get($gatewayId);
		if(!($gateway instanceof \Ething\Device\MySensorsGateway))
			throw new Exception("the device {$gatewayId} does not exist or has the wrong type");
		// remove any previous stream from this device
		if($mysensorsController = mysensorsGetController($gatewayId)){
			$mysensorsController->close();
			PoolStream::remove($mysensorsController);
		}
		Log::info("starting mysensors server '".$gateway->name()."' id=".$gateway->id()." type=".$gateway->type());
		if($mysensorsController = mysensorsInstanciateController($gateway)){
			PoolStream::add($mysensorsController);
			$client->success();
		} else {
			throw new Exception("unable to instanciate the controller");
		}
	}
});

$cli->add('device.mysensors.send', function($args, $client) use($ething){
	if(count($args) != 2)
		throw new Exception('invalid arguments');
	else {
		$gatewayId = $args[0];
		$messageStr = \base64_decode($args[1]); // the payload may be binary data or contains space 
		$gateway = $ething->get($gatewayId);
		if(!($gateway instanceof \Ething\Device\MySensorsGateway))
			throw new Exception("the device {$gatewayId} does not exist or has the wrong type");
		
		if($mysensorsController = mysensorsGetController($gatewayId)){
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

$cli->add('device.mysensors.sendWaitResponse', function($args, $client) use($ething){
	if(count($args) != 2)
		throw new Exception('invalid arguments');
	else {
		$gatewayId = $args[0];
		$messageStr = \base64_decode($args[1]); // the payload may be binary data or contains space 
		$gateway = $ething->get($gatewayId);
		if(!($gateway instanceof \Ething\Device\MySensorsGateway))
			throw new Exception("the device {$gatewayId} does not exist or has the wrong type");
		
		if($mysensorsController = mysensorsGetController($gatewayId)){
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

$cli->add('device.mysensors.end', function($args, $client) use($ething){
	if(count($args) != 1)
		throw new Exception('invalid arguments');
	else {
		$gatewayId = $args[0];
		$gateway = $ething->get($gatewayId);
		if(!($gateway instanceof \Ething\Device\MySensorsGateway))
			throw new Exception("the device {$gatewayId} does not exist or has the wrong type");
		if($mysensorsController = mysensorsGetController($gatewayId)){
			$mysensorsController->close();
			PoolStream::remove($mysensorsController);
		}
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
		
		if($mysensorsController = mysensorsGetController($gatewayId)){
			
			$mysensorsController->updateFirmware($node, $firmware, function($error) use ($client) {
				if($error)
					$client->error($error);
				else
					$client->success();
			});
			
		} else {
			throw new Exception("unknown mysensors instance for device id {$nodeId}");
		}
	}
});
