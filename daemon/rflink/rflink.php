<?php


require_once "Controller.php";
require_once "SerialController.php";




function rflinkGetController($id){
	return PoolStream::findOne(function($stream) use($id) {
		return ($stream instanceof \Ething\RFLink\Controller) && $stream->gateway->id() === $id;
	});
}


// init RFLink

$rflinkGateways = $ething->find(array(
	'type' => new \MongoDB\BSON\Regex('^Device\\\\RFLink.*Gateway$')
));

foreach($rflinkGateways as $rflinkGateway){
	Log::info("starting RFLink controller '".$rflinkGateway->name()."' id=".$rflinkGateway->id()." type=".$rflinkGateway->type());
	PoolStream::add(new \Ething\RFLink\SerialController($rflinkGateway));
}

unset($rflinkGateways);




$cli->add('device.rflink.start', function($args, $client) use($ething) {
	// start to listen to a stream to a RFLink gateway
	if(count($args) != 1)
		throw new Exception('invalid arguments');
	else {
		$gatewayId = $args[0];
		$gateway = $ething->get($gatewayId);
		if(!($gateway instanceof \Ething\Device\RFLinkGateway))
			throw new Exception("the device {$gatewayId} does not exist or has the wrong type");
		// remove any previous stream from this device
		if($rflinkController = rflinkGetController($gatewayId)){
			$rflinkController->close();
			PoolStream::remove($rflinkController);
		}
		Log::info("starting RFLink server '".$gateway->name()."' id=".$gateway->id()." type=".$gateway->type());
		$rflinkController = new \Ething\RFLink\SerialController($gateway);
		PoolStream::add($rflinkController);
		$client->success();
	}
});

$cli->add('device.rflink.send', function($args, $client) use($ething){
	if(count($args) != 2)
		throw new Exception('invalid arguments');
	else {
		$gatewayId = $args[0];
		$messageStr = \base64_decode($args[1]); // the payload may be binary data or contains space 
		$gateway = $ething->get($gatewayId);
		if(!($gateway instanceof \Ething\Device\RFLinkGateway))
			throw new Exception("the device {$gatewayId} does not exist or has the wrong type");
		
		if($rflinkController = rflinkGetController($gatewayId)){
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

$cli->add('device.rflink.sendWaitResponse', function($args, $client) use($ething){
	if(count($args) != 2)
		throw new Exception('invalid arguments');
	else {
		$gatewayId = $args[0];
		$messageStr = \base64_decode($args[1]); // the payload may be binary data or contains space 
		$gateway = $ething->get($gatewayId);
		if(!($gateway instanceof \Ething\Device\RFLinkGateway))
			throw new Exception("the device {$gatewayId} does not exist or has the wrong type");
		
		if($rflinkController = rflinkGetController($gatewayId)){
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

$cli->add('device.rflink.end', function($args, $client) use($ething){
	if(count($args) != 1)
		throw new Exception('invalid arguments');
	else {
		$gatewayId = $args[0];
		$gateway = $ething->get($gatewayId);
		if(!($gateway instanceof \Ething\Device\RFLinkGateway))
			throw new Exception("the device {$gatewayId} does not exist or has the wrong type");
		
		if($rflinkController = rflinkGetController($gatewayId)){
			$rflinkController->close();
			PoolStream::remove($rflinkController);
		}
		$client->success();
	}
});


