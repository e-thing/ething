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

set_exception_handler(function($exception) use($ething) {
	Log::warn("daemon stopped by exception : ".$exception->getMessage());
	
	// notify the user
	if(isset($ething)){
		Log::info("send notification");
		$ething->notify('ething daemon stopped', "ething daemon stopped by exception : ".$exception->getMessage());
	}
	
	exit(2);
});

register_shutdown_function(function(){
	
	if(ForkTask::getCurrentTask()) return; // do not go any further for forked process !
	
	SignalManager::dispatch(\Ething\Event\DaemonStopped::emit());
	
	// close all streams
	PoolStream::each(function($stream) {
		if(method_exists($stream, 'close')) $stream->close();
	});
	
	// kill all sub processes
	TaskManager::killAll();
	
	Log::info("daemon EXIT");
	
});


require_once __DIR__.'/SignalManager.php';
require_once __DIR__.'/CommandInterpreter.php';
require_once __DIR__.'/Server.php';
require_once __DIR__.'/../vendor/autoload.php';
require_once __DIR__.'/../src/Ething.php';


$ething = new \Ething\Ething();
$cli = new CommandInterpreter();
$server = new Server($cli, $ething->config('daemon.port'));



PoolStream::add($server);

$ething->setName('daemon');
$ething->setSignalsDispatcher('SignalManager::dispatch');


Log::$ething = $ething;
Log::info(" *** DAEMON START *** ");



$cli->add('info', function($args, $client) use($startTime) {
	$client->success('e-Thing '.\Ething\Ething::VERSION."\nuptime=".(time() - $startTime));
});

$cli->add('restart', function($args, $client) use ($ething) {
	$client->success();
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


/* Signals */
$signalsQueue = array();

SignalManager::attachHandler(function($signal) use (&$signalsQueue) {
	Log::debug("dispatchSignal=> {$signal->debugStr()}");
	$signalsQueue[] = $signal;
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
	
	$devices = $ething->find(array( '$or' => array(
		array(
			'type' => 'Device\\Http',
			'url' => array('$ne' => null)
		),
		array( 'type' => 'Device\\RTSP' ),
		array( 'type' => 'Device\\SSH' )
	)));
	
	foreach($devices as $device){
		$t = null;
		try {
			$t = $device->ping();
			Log::debug("ping: {$device->name()} -> ".($t===false ? 'fail' : $t));
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

function repairDB(){
	global $ething;
	
	Log::info("repairing DB");
	$ething->repair();
	
	foreach ( $ething->find() as $r ) {
		if(method_exists($r, "repair")){
			Log::debug("repairing {$r}");
			
			try {
				$r->repair();
			} catch( \Exception $e ) {
				Log::error("repair failed for {$r} : {$e->getMessage()}");
			}
		}
	}
	
	// also clean the database
	Log::debug("cleaning DB");
	foreach( $ething->db()->listCollections() as $collInfo){
		$name = $collInfo->getName();
		
		if(preg_match('/^system\./', $name)) continue;
		
		Log::debug("compacting collection {$name}");
		
		$ething->db()->command(array(
			'compact' => $name
		));
		
	}
	
}


if(!$server->start()){
	Log::fatal("unable to start the server at port {$server->getPort()}");
}


Timer::delay(1, function(){
	SignalManager::dispatch(\Ething\Event\DaemonStarted::emit());
});

Timer::setInterval(60, function(){
	SignalManager::dispatch(\Ething\Event\Timer::emit());
});


Timer::setInterval(60, function(){
	TaskManager::add(new ForkTask('pingDevicesTask'));
}, 60);


Timer::setInterval(600, function(){
	TaskManager::add(new ForkTask('checkExpiredDataTask'));
}, 100);

Timer::at(function(){
	TaskManager::add(new ForkTask('repairDB'));
}, 4);

Timer::setInterval(5, function() use(&$signalsQueue, $ething) {
	if($l = count($signalsQueue)){
		
		// fuse ResourceMetaUpdated signals 
		$f = 0;
		while($l--){
			$signal = $signalsQueue[$l];
			if($signal->getName() === "ResourceMetaUpdated"){
				// merge with previous signal
				for($i=0; $i<$l; $i++){
					$s = $signalsQueue[$i];
					if($signal->getName() === $s->getName() && $signal->resource === $s->resource){
						// ok same signal describing the same resource -> merge the attributes
						$signal->attributes = array_unique (array_merge ($signal->attributes, $s->attributes));
						array_splice($signalsQueue, $i, 1);
						$i--;
						$l--;
						$f++;
					}
				}
			}
		}
		
		Log::debug("signal fuse number {$f}");
		
		foreach($signalsQueue as $signal){
			TaskManager::add(new ForkTask(array($ething,'dispatchSignal'), array($signal, false)));
		}
		
		$signalsQueue = array();
	}
});



