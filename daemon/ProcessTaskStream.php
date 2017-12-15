<?php


class ProcessTaskStream extends Stream {
	
	private $task;
	
	public function __construct(ProcessTask $task){
		$this->task = $task;
		
		if(isset($this->task->process)){
			for($i=1; $i<3; $i++){
				if(isset($this->task->pipes[$i])){
					$this->registerStream($this->task->pipes[$i], $i);
				}
			}
		}
	}
	
	public function process($stream, $pipe){
		
		$chunk = $this->task->read(256, $pipe);
		
		if(is_string($chunk) && $chunk!==''){
			$this->task->data[$pipe] .= $chunk;
		} else {
			$this->unregister($pipe);
		}
	}
	
};
