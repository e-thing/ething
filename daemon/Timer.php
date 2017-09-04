<?php


class Timer {
	
	static private $tasks = array();
	
	
	
	static public function setInterval($interval, $callback, $startInSec = 0){
		if(is_callable($callback) && $interval > 0){
			static::$tasks[] = array(
				'type' => 'interval',
				'interval' => $interval,
				'callback' => $callback,
				'startIn' => $startInSec,
				't0' => time(),
				'running' => false
			);
			return true;
		}
		return false;
	}
	
	static public function delay($delay, $callback){
		if(is_callable($callback) && $delay > 0){
			static::$tasks[] = array(
				'type' => 'delay',
				'delay' => $delay,
				'callback' => $callback,
				't0' => time()
			);
			return true;
		}
		return false;
	}
	
	static public function at($callback, $hour, $min = 0){
		if(is_callable($callback)){
			static::$tasks[] = array(
				'type' => 'at',
				'hour' => $hour,
				'min' => $min,
				'callback' => $callback,
				't0' => time()
			);
			return true;
		}
		return false;
	}
	
	
	static private function run(&$task){
		$task['lastRun'] = time();
		if(!isset($task['executedCount'])) $task['executedCount'] = 0;
		$task['executedCount']++;
		call_user_func($task['callback']);
	}
	
	
	static public function update(){
		
		foreach(static::$tasks as $i => &$task){
			
			switch($task['type']){
				
				case 'interval':
					if($task['running']){
						if(time() - $task['lastRun'] >= $task['interval']){
							static::run($task);
						}
					} else {
						if(time() - $task['t0'] >= $task['startIn']){
							$task['running'] = true;
							static::run($task);
						}
					}
					break;
				
				case 'delay':
					
					if(time() - $task['t0'] >= $task['delay']){
						static::run($task);
						unset(static::$tasks[$i]);
					}
					
					break;
				
				case 'at':
					
					$currentHour = (int)date('H');
					$currentMin = (int)date('i');
					if($task['hour']===$currentHour && $task['min']===$currentMin && (!isset($task['lastRun']) || (time() - $task['lastRun']) > 60 )){
						static::run($task);
					}
					
					break;
			}
			
		}
		
	}
	
	
}
