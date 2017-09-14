<?php
declare(ticks = 1);

require_once 'Log.php';
require_once 'PoolStream.php';
require_once 'TaskManager.php';
require_once 'Timer.php';

Log::setLevel(Log::INFO);
Log::info("daemon started");




/*
 * globals
 */
$run = true;
$startTime = time();


/*
 * applications
 */
include 'core.php';
include 'mysensors/mysensors.php';
include 'rflink/rflink.php';
include 'mqtt/mqtt.php';
include 'yeelight/yeelight.php';

while($run){
	
	PoolStream::process(1);
	
	TaskManager::update(); // execute queued event here
	
	Timer::update();
	
}

Log::info("daemon stopped");

exit(0);

