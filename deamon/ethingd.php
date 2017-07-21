<?php
	
	$startTime = time();
	
	require_once 'Client.php';
	require_once 'Queue.php';
	require_once 'StreamCollection.php';
	
	$rootDir=__DIR__.'/..';
	
	require_once $rootDir.'/vendor/autoload.php';
	require_once $rootDir.'/src/Ething.php';
	
	// defaults
	$verbose = 0;
	$silent = 0;
	$run = true;
	
	
	function uecho($message = ''){
		global $silent;
		if(!$silent) echo $message.PHP_EOL;
	}
	
	function uechoerr($message = ''){
		global $silent;
		if(!$silent) echo 'ERROR: '.$message.PHP_EOL;
	}
	
	function help(){
		uecho();
		uecho("usage: " . basename(__FILE__, '.php') . " [-s] [-v] [-c conf]");
		uecho();
		uecho(" -s : silent, no output or no log");
		uecho(" -v : verbose, shows more details");
		exit(1);
	}
	
	function uexit($code = 0){
		global $streams, $server;
		
		// close all streams
		if(isset($streams)) $streams->each(function($stream) {
			if(method_exists($stream, 'close')) $stream->close();
		});
		
		// shutdown server
		if(isset($server)) fclose($server);
		
		uecho();
		uecho("--------------------------");
		uecho("Terminating e-Thing deamon");
		uecho("--------------------------");
		uecho(date("Y-m-d H:i:s"));
		uecho();
		uecho("exit code: {$code}");
		uecho();
		
		if(function_exists('ulog')){
			ulog("stoping deamon, exit code: {$code}");
		}
		
		exit($code);
	}
	
	
	if(function_exists('pcntl_signal')){
		declare(ticks = 1);
		
		function sig_handler($sig) {
			uexit(1);
		}

		pcntl_signal(SIGINT,  "sig_handler");
		pcntl_signal(SIGTERM, "sig_handler");
		pcntl_signal(SIGHUP,  "sig_handler");
	}
	
	
	
	// command line arguments
	while($arg = next($argv)){
		switch($arg){
			case '-v':
				$verbose=1;
				break;
			case '-s':
				$silent=1;
				break;
			default:
				uecho("ERROR: invalid argument '{$arg}'");
				help();
		}
	}
	
	
	
	
	uecho();
	uecho("-----------------------");
	uecho("Starting e-Thing deamon");
	uecho("-----------------------");
	uecho();
	uecho(date("Y-m-d H:i:s"));
	uecho();
	
	
	uecho("loading ething lib ({$rootDir}) ...");
	try{
		$ething = new \Ething\Ething();
	} catch (\Exception $e){
		uechoerr($e->getMessage());
		exit(1);
	}
	
	
	$cli = new CommandInterpreter();
	$streams = new StreamCollection();
	$eventQueue = new Queue(5);
	
	
	Task::$preProcFn = function() use($ething) {
		if(function_exists('pcntl_fork')){
			// reset the mongodb manager on forked children
			$ething->resetDbClient(); // cf. http://php.net/mongodb-driver-manager.construct and https://github.com/mongodb/mongo-php-driver/issues/174
		}
	};
	
	
	$ething->setSignalsDispatcher('dispatchSignal');
	
	
	function ulog($message){
		global $ething;
		
		$ething->log($message, 'DEAMON');
	}
	
	
	$cli->add('info', function($args, $client) use($startTime) {
		$client->success('e-Thing '.\Ething\Ething::VERSION."\nuptime=".(time() - $startTime));
	});
	
	$cli->add('device.mysensors.start', function($args, $client) use($ething, $streams) {
		// start to listen to a stream to a MySensors gateway
		if(count($args) != 1)
			throw new Exception('invalid arguments');
		else {
			$gatewayId = $args[0];
			$gateway = $ething->get($gatewayId);
			if(!($gateway instanceof \Ething\Device\MySensorsGateway))
				throw new Exception("the device {$gatewayId} does not exist or has the wrong type");
			// remove any previous stream from this device
			$mysensorsController = $streams->findOne(function($stream) use($gatewayId) {
				return ($stream instanceof \Ething\MySensors\Controller) && $stream->gateway->id() === $gatewayId;
			});
			if($mysensorsController){
				$mysensorsController->close();
				$streams->remove($mysensorsController);
			}
			uecho("starting mysensors server '".$gateway->name()."' [id=".$gateway->id()."] ...");
			$mysensorsController = $gateway->instanciateController();
			$streams->add($mysensorsController);
			$client->success();
		}
	});
	
	$cli->add('device.mysensors.send', function($args, $client) use($ething, $streams){
		if(count($args) != 2)
			throw new Exception('invalid arguments');
		else {
			$gatewayId = $args[0];
			$messageStr = \base64_decode($args[1]); // the payload may be binary data or contains space 
			$gateway = $ething->get($gatewayId);
			if(!($gateway instanceof \Ething\Device\MySensorsGateway))
				throw new Exception("the device {$gatewayId} does not exist or has the wrong type");
			$mysensorsController = $streams->findOne(function($stream) use($gatewayId) {
				return ($stream instanceof \Ething\MySensors\Controller) && $stream->gateway->id() === $gatewayId;
			});
			
			if($mysensorsController){
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
	
	$cli->add('device.mysensors.sendWaitResponse', function($args, $client) use($ething, $streams){
		if(count($args) != 2)
			throw new Exception('invalid arguments');
		else {
			$gatewayId = $args[0];
			$messageStr = \base64_decode($args[1]); // the payload may be binary data or contains space 
			$gateway = $ething->get($gatewayId);
			if(!($gateway instanceof \Ething\Device\MySensorsGateway))
				throw new Exception("the device {$gatewayId} does not exist or has the wrong type");
			$mysensorsController = $streams->findOne(function($stream) use($gatewayId) {
				return ($stream instanceof \Ething\MySensors\Controller) && $stream->gateway->id() === $gatewayId;
			});
			
			if($mysensorsController){
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
	
	$cli->add('device.mysensors.end', function($args, $client) use($ething, $streams){
		if(count($args) != 1)
			throw new Exception('invalid arguments');
		else {
			$gatewayId = $args[0];
			$gateway = $ething->get($gatewayId);
			if(!($gateway instanceof \Ething\Device\MySensorsGateway))
				throw new Exception("the device {$gatewayId} does not exist or has the wrong type");
			$mysensorsController = $streams->findOne(function($stream) use($gatewayId) {
				return ($stream instanceof \Ething\MySensors\Controller) && $stream->gateway->id() === $gatewayId;
			});
			if($mysensorsController){
				$mysensorsController->close();
				$streams->remove($mysensorsController);
			}
			$client->success();
		}
	});
	
	$cli->add('device.mysensors.updateFirmware', function($args, $client) use($ething, $streams){
		if(count($args) != 2)
			throw new Exception('invalid arguments');
		else {
			$nodeId = $args[0];
			$firmware = \base64_decode($args[1]);
			$node = $ething->get($nodeId);
			if(!($node instanceof \Ething\Device\MySensorsNode))
				throw new Exception("the device {$nodeId} does not exist or has the wrong type");
			$gateway = $node->gateway();
			// remove any previous stream from this device
			$mysensorsController = $streams->findOne(function($stream) use($gateway) {
				return ($stream instanceof \Ething\MySensors\Controller) && $stream->gateway->id() === $gateway->id();
			});
			
			if($mysensorsController){
				
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
	
	
	$cli->add('device.mqtt.start', function($args, $client) use($ething, $streams) {
		// start to listen to a stream to a MQTT server
		if(count($args) != 1)
			throw new Exception('invalid arguments');
		else {
			$deviceId = $args[0];
			$mqttdevice = $ething->get($deviceId);
			if(!($mqttdevice instanceof \Ething\Device\MQTT))
				throw new Exception("the device {$deviceId} does not exist or has the wrong type (not MQTT)");
			// remove any previous stream from this device
			$mqttClient = $streams->findOne(function($stream) use($deviceId) {
				return ($stream instanceof \Ething\MQTT\Client) && $stream->device->id() === $deviceId;
			});
			if($mqttClient){
				$mqttClient->close();
				$streams->remove($mqttClient);
			}
			if($streams->add($mqttdevice->instanciateMqttClient()))
				uecho("starting mqtt client '".$mqttdevice->name()."' [id=".$mqttdevice->id()."] ...");
			$client->success();
		}
	});
	
	$cli->add('device.mqtt.send', function($args, $client) use($ething, $streams){
		if(count($args) != 3)
			throw new Exception('invalid arguments');
		else {
			$deviceId = $args[0];
			$topic = $args[1];
			$payload = \base64_decode($args[2]); // the payload may be binary data or contains space 
			$mqttdevice = $ething->get($deviceId);
			if(!($mqttdevice instanceof \Ething\Device\MQTT))
				throw new Exception("the device {$deviceId} does not exist or has the wrong type (not MQTT)");
			$mqttClient = $streams->findOne(function($stream) use($deviceId) {
				return ($stream instanceof \Ething\MQTT\Client) && $stream->device->id() === $deviceId;
			});
			
			if($mqttClient){
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
	
	$cli->add('device.mqtt.end', function($args, $client) use($ething, $streams){
		if(count($args) != 1)
			throw new Exception('invalid arguments');
		else {
			$deviceId = $args[0];
			$mqttdevice = $ething->get($deviceId);
			if(!($mqttdevice instanceof \Ething\Device\MQTT))
				throw new Exception("the device {$deviceId} does not exist or has the wrong type (not MQTT)");
			$mqttClient = $streams->findOne(function($stream) use($deviceId) {
				return ($stream instanceof \Ething\MQTT\Client) && $stream->device->id() === $deviceId;
			});
			if($mqttClient){
				$mqttClient->close();
				$streams->remove($mqttClient);
			}
			$client->success();
		}
	});
	
	$cli->add('device.rflink.start', function($args, $client) use($ething, $streams) {
		// start to listen to a stream to a RFLink gateway
		if(count($args) != 1)
			throw new Exception('invalid arguments');
		else {
			$gatewayId = $args[0];
			$gateway = $ething->get($gatewayId);
			if(!($gateway instanceof \Ething\Device\RFLinkGateway))
				throw new Exception("the device {$gatewayId} does not exist or has the wrong type");
			// remove any previous stream from this device
			$rflinkController = $streams->findOne(function($stream) use($gatewayId) {
				return ($stream instanceof \Ething\RFLink\Controller) && $stream->gateway->id() === $gatewayId;
			});
			if($rflinkController){
				$rflinkController->close();
				$streams->remove($rflinkController);
			}
			uecho("starting RFLink server '".$gateway->name()."' [id=".$gateway->id()."] ...");
			$rflinkController = $gateway->instanciateController();
			$streams->add($rflinkController);
			$client->success();
		}
	});
	
	$cli->add('device.rflink.send', function($args, $client) use($ething, $streams){
		if(count($args) != 2)
			throw new Exception('invalid arguments');
		else {
			$gatewayId = $args[0];
			$messageStr = \base64_decode($args[1]); // the payload may be binary data or contains space 
			$gateway = $ething->get($gatewayId);
			if(!($gateway instanceof \Ething\Device\RFLinkGateway))
				throw new Exception("the device {$gatewayId} does not exist or has the wrong type");
			$rflinkController = $streams->findOne(function($stream) use($gatewayId) {
				return ($stream instanceof \Ething\RFLink\Controller) && $stream->gateway->id() === $gatewayId;
			});
			
			if($rflinkController){
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
	
	$cli->add('device.rflink.sendWaitResponse', function($args, $client) use($ething, $streams){
		if(count($args) != 2)
			throw new Exception('invalid arguments');
		else {
			$gatewayId = $args[0];
			$messageStr = \base64_decode($args[1]); // the payload may be binary data or contains space 
			$gateway = $ething->get($gatewayId);
			if(!($gateway instanceof \Ething\Device\RFLinkGateway))
				throw new Exception("the device {$gatewayId} does not exist or has the wrong type");
			$rflinkController = $streams->findOne(function($stream) use($gatewayId) {
				return ($stream instanceof \Ething\RFLink\Controller) && $stream->gateway->id() === $gatewayId;
			});
			
			if($rflinkController){
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
	
	$cli->add('device.rflink.end', function($args, $client) use($ething, $streams){
		if(count($args) != 1)
			throw new Exception('invalid arguments');
		else {
			$gatewayId = $args[0];
			$gateway = $ething->get($gatewayId);
			if(!($gateway instanceof \Ething\Device\RFLinkGateway))
				throw new Exception("the device {$gatewayId} does not exist or has the wrong type");
			$rflinkController = $streams->findOne(function($stream) use($gatewayId) {
				return ($stream instanceof \Ething\RFLink\Controller) && $stream->gateway->id() === $gatewayId;
			});
			if($rflinkController){
				$rflinkController->close();
				$streams->remove($rflinkController);
			}
			$client->success();
		}
	});
	
	$cli->add('quit', function($args, $client){
		$client->close();
	});
	
	$cli->add('stop', function($args, $client) use(&$run){
		$client->close();
		$run = false;
	});
	
	
	
	$cli->add('signal.dispatch', function($args, $client) {
		if(count($args) != 1)
			throw new Exception('invalid arguments');
		else {
			$serializedEvent = \base64_decode($args[0]);
			$signal = unserialize($serializedEvent);
			
			dispatchSignal($signal);
			
			$client->success();
		}
	});
	
	
	// event
	
	$next_minute_timestamp = 0;
	
	function dispatchSignal(\Ething\Event\Signal $signal){
		global $ething, $eventQueue, $verbose;
		if($verbose) {
			uecho("dispatchSignal= {$signal->debugStr()}");
		}
		$task = new Task(array($ething,'dispatchSignal'), array($signal, false));
		$eventQueue->add($task);
	}
	
	
	function pingDevicesTask(){
		global $ething, $verbose;
				
		$devices = $ething->find(array(
			'type' => array( '$in' => array( 'Device\\Http', 'Device\\RTSP' ) ),
			'url' => array('$ne' => null)
		));
		
		foreach($devices as $device){
			$t = null;
			try {
				$t = $device->ping();
				if($verbose) uecho("ping: {$device->name()} -> ".($t===false ? 'fail' : $t));
			}
			catch(Exception $e){}
		}
		
	}
	
	function checkExpiredDataTask(){
		global $ething, $verbose;
		
		$rs = $ething->find(array(
			'expireAfter' => array( '$ne' => null )
		));
		
		foreach($rs as $r){
			if(method_exists($r,'checkExpiredData')){
				try {
					if($verbose) uecho("check if {$r->name()} has data expired");
					$r->checkExpiredData();
				}
				catch(Exception $e){}
			}
		}
		
	}
	
	
	ulog('starting deamon');
	
	// init MySensors
	$mySensorsGateways = $ething->find(array(
		'type' => new \MongoDB\BSON\Regex('^Device\\\\MySensors.*Gateway$')
	));
	foreach($mySensorsGateways as $mySensorsGateway){
		uecho("starting mysensors server '".$mySensorsGateway->name()."' [id=".$mySensorsGateway->id()."] ...");
		$streams->add($mySensorsGateway->instanciateController());
	}
	unset($mySensorsGateways);
	
	// init RFLink
	$rflinkGateways = $ething->find(array(
		'type' => new \MongoDB\BSON\Regex('^Device\\\\RFLink.*Gateway$')
	));
	foreach($rflinkGateways as $rflinkGateway){
		uecho("starting RFLink server '".$rflinkGateway->name()."' [id=".$rflinkGateway->id()."] ...");
		$streams->add($rflinkGateway->instanciateController());
	}
	unset($rflinkGateways);
	
	// init MQTT clients
	$mqttdevices = $ething->find(array(
		'type' => 'Device\\MQTT'
	));
	foreach($mqttdevices as $mqttdevice){
		if($streams->add($mqttdevice->instanciateMqttClient()))
			uecho("starting mqtt client '".$mqttdevice->name()."' [id=".$mqttdevice->id()."] ...");
	}
	unset($mqttdevices);
	
	
	// start cli server
	$serverAddress = $ething->config('deamonServer.address');
	if(!$serverAddress) $serverAddress= "tcp://127.0.0.1:24934";
	uecho("starting deamon server ({$serverAddress}) ...");
	$server = stream_socket_server($serverAddress, $errno, $errstr);
	if(!$server){
		uechoerr('unable to start the server');
		ulog('ERR: unable to start the server');
		uexit(2);
	}
	
	
	
	while($run) {
		
		
		// incomming client
		while($stream = @stream_socket_accept($server, $streams->length() ? 0 : 1)) {
			$client = new Client($stream, $cli);
			$streams->add($client);
			if($verbose) uecho("new client {$client->id} connected");
		}
		
		// incomming data ?
		while($streams->available($streamsWithData)) {
			foreach($streamsWithData as $stream) {
				try{
					$stream->read();
				} catch (\Exception $e){
					uechoerr($e->getMessage());
				}
			}
		}
		
		// do non blocking stuff here
		
		$streams->each(function($stream) {
			if(method_exists($stream, 'update'))
				$stream->update(); // autoconnect, ack timeout, smartSleep timeout ... 
		});
		
		
		$eventQueue->update(); // execute queued event here
		
		
		// is fired every minutes
		$now = time();
		if($now >= $next_minute_timestamp){
			$next_minute_timestamp = ceil(($now+1)/60)*60;
			$currentMinutes = intval(date('i'));
			
			// timer event
			dispatchSignal(\Ething\Event\Timer::emit());
			
			if($currentMinutes%5 == 0){
				// every 5 minutes
				$eventQueue->add(new Task('pingDevicesTask'));
			}
			
			if($currentMinutes%15 == 0){
				// every 15 minutes
				$eventQueue->add(new Task('checkExpiredDataTask'));
			}
			
		}
		
		if($verbose){
			
			uecho("task running: ".count($eventQueue->runningTasks())."/".$eventQueue->length());
			
		}
		
		
		
		
	}
	
	fclose($server);
	
	
	uexit(0);
	
?>