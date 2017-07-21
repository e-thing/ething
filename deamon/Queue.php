<?php


require_once 'Task.php';

class Queue {
	
	public $queue = array();
	public $maxRunning = 2;
	
	public function __construct($maxRunning = 2){
		$this->maxRunning = function_exists('pcntl_fork') ? $maxRunning : 1;
	}
	
	public function add(Task $item){
		$this->queue[] = $item;
	}
	
	public function remove(Task $item){
		$i = array_search($item, $this->queue, true);
		if($i !== false)
			array_splice($this->queue, $i, 1);
	}
	
	public function length(){
		return count($this->queue);
	}
	
	public function runningTasks(){
		$tasks = array();
		foreach($this->queue as $item){
			if($item->isRunning()){
				$tasks[] = $item;
			}
		}
		return $tasks;
	}
	
	public function update(){
		
		$running = 0;
		
		foreach($this->queue as $item){
			
			if($item->isRunning()){
				$running++;
			} else if($item->state === 'terminated'){
				// auto remove
				$this->remove($item);
			}
			
		}
		
		//echo "running = $running , length {$this->length()}\n";
		
		$toLaunch = $this->maxRunning - $running;
		$launched = 0;
		if($toLaunch>0){
			
			foreach($this->queue as $item){
				if($item->state === 'pending'){
					
					//echo "run {$item->data}\n";
					$item->run();
					$launched++;
					
					if($launched>=$toLaunch) break;
				}
			}
			
		}
		
	}
	
};

