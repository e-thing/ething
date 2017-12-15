<?php

require_once __DIR__."/Controller.php";


class Mihome {
	
	static public $controller = null;
	
	static public function init() {
		global $ething;
		
		\Mihome::$controller = new \Ething\Mihome\Controller($ething);
		
		\PoolStream::add(\Mihome::$controller);
	}
	
}




// init
\Mihome::init();

$cli->add('device.mihome.send', function($args, $client) use($ething) {
	if(count($args) != 2)
		throw new Exception('invalid arguments');
	else {
		$gatewayId = $args[0];
		$cmd = \json_decode(\base64_decode($args[1]), true);
		
		if($gateway = $ething->get($gatewayId)){
			\Mihome::$controller->sendData($gateway, $cmd, function($error, $commandSent, $response) use ($client) {
				if($error)
					$client->error($error);
				else
					$client->success($response);
			});
			
		} else {
			throw new Exception("unknown Mihome gateway instance for device id {$gatewayId}");
		}
	}
});
