<?php


require_once __DIR__."/Task.php";
require_once __DIR__."/ForkTask.php";
require_once __DIR__."/ProcessTask.php";

class TaskManager {
	
	static private $queue = array();
	static private $maxRunning = 5;
	
	
	static public function add(Task $task, $onEnd = null, $onStart = null, $onError = null){
		$id = uniqid();
		self::$queue[] = array(
			'id' => $id,
			'task' => $task,
			'onEnd' => $onEnd,
			'onStart' => $onStart,
			'onError' => $onStart
		);
		return $id;
	}
	
	static public function remove($task){
		foreach(self::$queue as $i => $item){
			$f = false;
			if(is_string($task)){
				$f = $item['id'] === $task;
			} else if($task instanceof Task){
				$f = $item['task'] === $task;
			}
			if($f){
				array_splice(self::$queue, $i, 1);
				break;
			}
		}
	}
	
	static public function length(){
		return count(self::$queue);
	}
	
	static public function runningTasks(){
		$tasks = array();
		foreach(self::$queue as $item){
			if($item['task']->isRunning()){
				$tasks[] = $item['task'];
			}
		}
		return $tasks;
	}
	
	static public function getTasks(){
		$tasks = array();
		foreach(self::$queue as $item){
			$tasks[] = $item['task'];
		}
		return $tasks;
	}
	
	public function killAll(){
		foreach(self::$queue as $item){
			$task = $item['task'];
			$task->end();
		};
	}
	
	static public function update(){
		
		$running = 0;
		$terminated = array();
		
		foreach(self::$queue as $item){
			
			$task = $item['task'];
			
			if($task->state !== 'running') continue;
			
			if($task->isRunning()){ // refresh the internal state
				$running++;
			} else if($task->state === 'terminated'){
				Log::debug("Task {$task->getName()} end duration={$task->getDuration()}sec");
				
				if(is_callable($item['onEnd']))
					call_user_func($item['onEnd'], $task);
				
				// auto remove
				$terminated[] = $item['id'];
			}
			
		}
		
		$toLaunch = self::$maxRunning - $running;
		$launched = 0;
		if($toLaunch>0){
			
			foreach(self::$queue as $item){
				
				$task = $item['task'];
				
				if($task->state === 'pending'){
					
					Log::debug("Task {$task->getName()} start");
					
					if(is_callable($item['onStart']))
						call_user_func($item['onStart'], $task);
					
					if($task->run()){
						$launched++;
					} else {
						// error
						Log::debug("Task {$task->getName()} error duration={$task->getDuration()}sec");
						
						if(is_callable($item['onError']))
							call_user_func($item['onError'], $task);
						
						$terminated[] = $item['id'];
					}
					
					if($launched>=$toLaunch) break;
				}
			}
			
		}
		
		foreach($terminated as $taskId){
			self::remove($taskId);
		}
		
	}
	
};

