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
	
	if(ForkTask::getCurrentTask()) return; // do not go any further for forked process !
	
	// close all streams
	PoolStream::each(function($stream) {
		if(method_exists($stream, 'close')) $stream->close();
	});
	
	// kill all sub processes
	TaskManager::killAll();
	
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

$cli->add('process.list', function($args, $client) {
	
	$out = "name                           status    pid        duration return\n";
	$out .= "-------------------------------------------------------------------\n";
	
	foreach(TaskManager::getTasks() as $task){
		switch($task->state){
			case 'running':
				$status = 'R';
				break;
			case 'terminated':
				$status = 'T';
				break;
			case 'error':
				$status = 'E';
				break;
			case 'pending':
				$status = 'W';
				break;
			default:
				$status = '?';
				break;
		}
		$runCount = $task->getRunningCount();
		$out .= sprintf("%-30s %6s %6s %15s %6d\n",
			$task->getName(),
			$status,
			$task->state !== 'running' || empty($task->pid) ? '-' : (string)($task->pid),
			$task->state === 'running' ? (new DateTime())->diff((new DateTime())->setTimestamp($task->getStartTime()))->format('%dd%Hh%Im%Ss') : ($runCount ? (new DateInterval('PT'.$task->getDuration().'S'))->format('%dd%Hh%Im%Ss') : '-'),
			$runCount>1 ? $task->getLastExitCode() : '-'
		);
	}
	
	$client->success($out);
});

$cli->add('process.kill', function($args, $client) {
	if(count($args)>0 && is_numeric($args[0])){
		$pid = (int)$args[0];
		
		foreach(TaskManager::runningTasks() as $task){
			if($task->pid === $pid){
				$task->end();
				break;
			}
		}
		
		$client->success($out);
	}
	$client->error();
});


$cli->add('net.scan', function($args, $client) {
	if(count($args) != 0)
		throw new Exception('invalid arguments');
	else {
		
		TaskManager::add(new ProcessTask('php '.__DIR__.'/tasks/net.scan.php', 'net.scan', array(
				'enableStdout' => true
			)), function($task) use ($client){
			if($task->lastExitCode===0){
				$client->success($task->data[1]);
			} else {
				$client->error();
			}
		});
		
	}
});

$cli->add('net.wol', function($args, $client) {
	if(count($args) == 0)
		throw new Exception('invalid arguments');
	else {
		TaskManager::add(new ProcessTask('php '.__DIR__.'/tasks/net.wol.php '.implode(' ',$args), 'net.wol'), function($task) use ($client){
			if($task->lastExitCode===0){
				$client->success();
			} else {
				$client->error();
			}
		});
	}
});

$cli->add('net.ping', function($args, $client) {
	if(count($args) == 0)
		throw new Exception('invalid arguments');
	else {
		TaskManager::add(new ProcessTask('php '.__DIR__.'/tasks/net.ping.php '.implode(' ',$args), 'net.ping', array(
				'enableStdout' => true
			)), function($task) use ($client){
			if($task->lastExitCode===0){
				$client->success($task->data[1]);
			} else {
				$client->error();
			}
		});
	}
});

SignalManager::attachHandler(function($signal) use ($ething) {
	Log::debug("dispatchSignal=> {$signal->debugStr()}");
	TaskManager::add(new ForkTask(array($ething,'dispatchSignal'), array($signal, false)));
});

ForkTask::$forkInit = function($task) use($ething, $server, $cli) {
	
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
	TaskManager::add(new ForkTask('pingDevicesTask'));
}, 60);


Timer::setInterval(600, function(){
	TaskManager::add(new ForkTask('checkExpiredDataTask'));
}, 100);



