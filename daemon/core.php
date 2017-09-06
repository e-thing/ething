<?php



if(function_exists('pcntl_signal')){
	function sig_handler($sig) {
		Log::warn("daemon stopped by signal {$sig}");
		exit(1);
	}
	pcntl_signal(SIGINT,  "sig_handler");
	pcntl_signal(SIGTERM, "sig_handler");
	pcntl_signal(SIGHUP,  "sig_handler");
}

register_shutdown_function(function(){
	
	if(Task::getCurrentTask()) return; // do not go any further for forked process !
	
	// close all streams
	PoolStream::each(function($stream) {
		if(method_exists($stream, 'close')) $stream->close();
	});
	
	Log::info("daemon EXIT");
	
});


require_once 'SignalManager.php';
require_once 'CommandInterpreter.php';
require_once 'Server.php';
require_once __DIR__.'/../vendor/autoload.php';
require_once __DIR__.'/../src/Ething.php';


$ething = new \Ething\Ething();
$cli = new CommandInterpreter();
$server = new Server($cli, $ething->config('daemon.port'));


PoolStream::add($server);

Log::setName('daemon');

$ething->setName('daemon');
$ething->setSignalsDispatcher('SignalManager::dispatch');


$ething->logger()->info(" *** DAEMON START *** ");

$cli->add('info', function($args, $client) use($startTime) {
	$client->success('e-Thing '.\Ething\Ething::VERSION."\nuptime=".(time() - $startTime));
});

$cli->add('restart', function($args, $client) use ($ething) {
	$client->success();
	$ething->logger()->warn('daemon restart');
	Log::info("daemon restart");
	system('service ethingd restart &');
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
		$client->success();
		$serializedEvent = \base64_decode($args[0]);
		$signal = unserialize($serializedEvent);
		
		SignalManager::dispatch($signal);
	}
});


SignalManager::attachHandler(function($signal) use ($ething) {
	Log::debug("dispatchSignal=> {$signal->debugStr()}");
	TaskManager::add(new Task(array($ething,'dispatchSignal'), array($signal, false)));
});

Task::$forkInit = function($task) use($ething, $server, $cli) {
	
	$name = 'task:'.$task->getName();
	
	// reset the mongodb manager on forked children
	$ething->resetDbClient(); // cf. http://php.net/mongodb-driver-manager.construct and https://github.com/mongodb/mongo-php-driver/issues/174
	$ething->setName($name);
	$ething->setSignalsDispatcher(false);
	
	Log::setName($name);
	
	PoolStream::closeAll();
	
};



function pingDevicesTask(){
	global $ething;
			
	$devices = $ething->find(array(
		'type' => array( '$in' => array( 'Device\\Http', 'Device\\RTSP' ) ),
		'url' => array('$ne' => null)
	));
	
	foreach($devices as $device){
		$t = null;
		try {
			$t = $device->ping();
			Log::info("ping: {$device->name()} -> ".($t===false ? 'fail' : $t));
		}
		catch(Exception $e){}
	}
	
}

function checkExpiredDataTask(){
	global $ething;
	
	$rs = $ething->find(array(
		'expireAfter' => array( '$ne' => null )
	));
	
	foreach($rs as $r){
		if(method_exists($r,'checkExpiredData')){
			try {
				Log::debug("check if {$r->name()} has data expired");
				$r->checkExpiredData();
			}
			catch(Exception $e){}
		}
	}
	
}

if(!$server->start()){
	Log::fatal("unable to start the server at port {$server->getPort()}");
}


Timer::delay(1, function(){
	SignalManager::dispatch(\Ething\Event\DaemonRestarted::emit());
});

Timer::setInterval(60, function(){
	SignalManager::dispatch(\Ething\Event\Timer::emit());
});


Timer::setInterval(300, function(){
	TaskManager::add(new Task('pingDevicesTask'));
}, 60);


Timer::setInterval(600, function(){
	TaskManager::add(new Task('checkExpiredDataTask'));
}, 100);



