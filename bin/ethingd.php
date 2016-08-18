<?php
	
	$rootDir=__DIR__.'/..';
	
	require_once $rootDir.'/vendor/autoload.php';
	require_once $rootDir.'/src/Ething.php';
	
	// defaults
	$configFile = $rootDir.'/config.php';
	$verbose = 0;
	$silent = 0;
	$logFile = false;
	$config = array();
	
	
	
	function uecho($message = ''){
		global $silent;
		if(!$silent) echo $message.PHP_EOL;
	}
	
	function help(){
		uecho();
		uecho("usage: " . basename(__FILE__, '.php') . " [-s] [-v] [-c conf]");
		uecho();
		uecho(" -s : silent, no output or no log");
		uecho(" -v : verbose, shows more details");
		uecho(" -c <configuration file> : specify a configuration file");
		exit(1);
	}
	
	function ulog($e){
		global $silent, $logFile;
		if($silent) return;
		
		$message = '?';
			
		if($e instanceof \Exception){
			$message = "Exception[".get_class($e)."]: {$e->getMessage()} {$e->getFile()}[line:{$e->getLine()} code:{$e->getCode()}]";
		}
		else if(is_string($e)){
			$message = $e;
		}
		else {
			$message = print_r($e, true);
		}
		
		$message = date(\DateTime::RFC3339).' DEAMON '.$message;
		
		// stdout
		uecho($message);
		
		// log
		if(!empty($logFile))
			@file_put_contents($logFile, $message.PHP_EOL , FILE_APPEND);
		
	}
	
	
	function tick() {
		global $ething, $verbose;
		
		$resources = $ething->find(array(
			'rules.event' => 'TickTimer'
		));
		
		if($verbose)
			ulog("tick: ".count($resources)." resources");
		
		foreach($resources as $resource){
			$resource->dispatchEvent('TickTimer');
		}
	}
	
	function pingDevices(){
		global $ething, $verbose;
		
		$devices = $ething->find(array(
			'type' => 'Device',
			'rules.event' => 'DeviceUnreachable'
		));
		
		foreach($devices as $device){
			$t = null;
			try {
				$t = $device->ping();
				if($verbose) ulog("ping: {$device->name()} -> ".($t===false ? 'fail' : $t));
			}
			catch(Exception $e){
				ulog($e);
			}
			if($t===false)
				$device->dispatchEvent('DeviceUnreachable');
		}
		
	}
	
	function checkExpiredData(){
		global $ething, $verbose;
		
		$rs = $ething->find(array(
			'expireAfter' => array( '$ne' => null )
		));
		
		foreach($rs as $r){
			if(method_exists($r,'checkExpiredData')){
				try {
					if($verbose) ulog("check if {$r->name()} has data expired");
					$r->checkExpiredData();
				}
				catch(Exception $e){
					ulog($e);
				}
			}
		}
		
	}
	
	function sleepUntilNextMinute(){
		$now = time();
		$next_minute_timestamp = ceil(($now+1)/60)*60;
		
		sleep( $next_minute_timestamp - $now);
	}
	
	
	
	// command line arguments
	while($arg = next($argv)){
		switch($arg){
			case '-c':
				if(!($configFile = next($argv))) help();
				break;
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
	
	
	
	
	// load config
	if(is_string($configFile)){
		if(is_readable($configFile)){
			$config = include($configFile);
		} else {
			uecho("ERROR: unable to find the configuration file '{$config}'");
			help();
		}
	}
	
	$logFile = isset($config['log']) && is_string($config['log']) ? $config['log'] : false;
	
	
	ulog('starting daemon process');
	ulog('daemon pid : '.getmypid());
	
	
	register_shutdown_function(function(){
		ulog('stopping daemon process');
	});
	
	set_error_handler(function($errno, $errstr, $errfile, $errline){
		if (error_reporting() === 0) return;
		
		ulog(new ErrorException( $errstr, 0, $errno, $errfile, $errline ));
		return false;
	});
	
	set_exception_handler(function($e){
		ulog($e);
	});
	
	
	
	ulog('log file : '.(empty($logFile) ? 'none' : $logFile));
	ulog('conf file : '.(empty($configFile) ? 'none' : $configFile));
	
	ulog('options : '.print_r($config, true));
	
	$ething = new \Ething\Ething($config);
	
	$ething->setEventExceptionHandler(function($exception){
		ulog($exception);
	});
	
	$c=0;
	while(true){
		
		sleepUntilNextMinute();
   		
		tick();
		
		if(($c++)%5 == 0){
			// every 5 minutes
			pingDevices();
		}
		
		if(($c++)%15 == 0){
			// every 15 minutes
			checkExpiredData();
		}
		
	}
	

