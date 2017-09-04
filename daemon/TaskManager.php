<?php


require_once 'Task.php';

class TaskManager {
	
	static private $queue = array();
	static private $maxRunning = 5;
	
	
	static public function add(Task $item){
		self::$queue[] = $item;
	}
	
	static public function remove(Task $item){
		$i = array_search($item, self::$queue, true);
		if($i !== false)
			array_splice(self::$queue, $i, 1);
	}
	
	static public function length(){
		return count(self::$queue);
	}
	
	static public function runningTasks(){
		$tasks = array();
		foreach(self::$queue as $item){
			if($item->isRunning()){
				$tasks[] = $item;
			}
		}
		return $tasks;
	}
	
	static public function update(){
		
		$running = 0;
		
		foreach(self::$queue as $item){
			
			if($item->isRunning()){
				$running++;
			} else if($item->state === 'terminated'){
				//Log::debug("Task {$item->getName()} end duration={$item->getDuration()}sec");
				// auto remove
				self::remove($item);
			}
			
		}
		
		$toLaunch = self::$maxRunning - $running;
		$launched = 0;
		if($toLaunch>0){
			
			foreach(self::$queue as $item){
				if($item->state === 'pending'){
					
					//Log::debug("Task {$item->getName()} start");
					$item->run();
					$launched++;
					
					if($launched>=$toLaunch) break;
				}
			}
			
		}
		
	}
	
};

