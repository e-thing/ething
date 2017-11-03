<?php

require_once __DIR__."/Controller.php";


class Blea {
	
	static public $controller = null;
	
	static public function init() {
		global $ething;
		
		\Blea::$controller = new \Ething\Blea\Controller($ething);
		
		$devices = $ething->find(array(
			'type' => new \MongoDB\BSON\Regex('^Device\\\\Blea.*Gateway$')
		));

		foreach($devices as $device){
			\Blea::$controller->startGateway($device->id());
		}
		
		// auto start/stop controller on device create/remove
		\SignalManager::attachHandler(function($signal) use ($ething) {
			
			if($signal->getName() === 'ResourceMetaUpdated'){
				if(preg_match('/Blea.*Gateway/', $signal->rType)){
					if(!empty(array_intersect(['port', 'host'], $signal->attributes)))
						\Blea::$controller->startGateway($signal->resource);
				}
			} else if($signal->getName() === 'ResourceCreated'){
				if(preg_match('/Blea.*Gateway/', $signal->rType)) \Blea::$controller->startGateway($signal->resource);
			} else if($signal->getName() === 'ResourceDeleted'){
				if(preg_match('/Blea.*Gateway/', $signal->rType)) \Blea::$controller->stopGateway($signal->resource);
			}
			
		});
		
	}

}




// init
\Blea::init();


$cli->add('device.blea.send', function($args, $client) {
	if(count($args) != 2)
		throw new Exception('invalid arguments');
	else {
		$gatewayId = $args[0];
		$data = \json_decode(\base64_decode($args[1]), true);
		
		if(\Blea::$controller->sendData($gatewayId, $data)){
			$client->success();
		} else {
			$client->error('error');
		}
	}
});
