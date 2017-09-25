<?php



abstract class Task {
	
	public $state = 'pending';
	public $name = null;
	public $startTime = null;
	public $endTime = null;
	public $count = 0;
	public $pid = 0;
	public $lastExitCode = null;
	
	private $cb = array();
	
	public function __construct($name = null){
		$this->setName($name);
	}
	
	public function setName($name){
		$this->name = empty($name) ? '?' : $name;
	}
	
	public function getName(){
		return $this->name;
	}
	
	public function getStartTime(){
		return $this->startTime;
	}
	
	public function getDuration(){
		if(isset($this->startTime)){
			$end = isset($this->endTime) ? $this->endTime : microtime(true);
			return $end - $this->startTime;
		}
		return 0.;
	}
	
	public function getLastExitCode(){
		return $this->lastExitCode;
	}
	
	public function getRunningCount(){
		return $this->count;
	}
	
	public function run(){
		
		if($this->state === 'running') return false; // already running
		
		$this->startTime = microtime(true);
		$this->endTime = null;
		$this->state = 'running';
		$this->count++;
		
		$res = $this->process();
		
		if(!$res){
			$this->setTerminateState();
			$this->state = 'error';
		}
		
		return $res;
	}
	
	
	/* start abstract */
	
	abstract protected function process();
	
	abstract public function isRunning();
	
	abstract public function end();
	
	/* end abstract */
	
	
	public function setTerminateState(){
		$this->endTime = microtime(true);
		$this->state = 'terminated';
	}
	
	
	
	
	// callback register
	public function on($name, $cb){
		$this->cb[$name] = $cb;
	}
	
	protected function trigger($name, $args = array()){
		if(isset($this->cb[$name]) && is_callable($this->cb[$name])){
			array_unshift($args, $this);
			call_user_func_array($this->cb[$name], $args);
		}
	}
	
};



