<?php


class ProcessTaskStream extends Stream {
	
	private $task;
	private $enabled = array(true, true, true);
	
	public function __construct(ProcessTask $task){
		$this->task = $task;
	}
	
	public function getStreams(){
		if(isset($this->task->process)){
			$streams = array();
			for($i=1; $i<3; $i++){
				if($this->enabled[$i] && isset($this->task->pipes[$i])){
					$streams[] = $this->task->pipes[$i];
				}
			}
			return $streams;
		}
		return null;
	}
	
	public function process($stream){
		
		$pipe = array_search($stream, $this->task->pipes);
		
		$chunk = $this->task->read(256, $pipe);
		
		if(is_string($chunk) && $chunk!==''){
			$this->task->data[$pipe] .= $chunk;
		} else {
			$this->enabled[$pipe] = false;
		}
	}
	
};
