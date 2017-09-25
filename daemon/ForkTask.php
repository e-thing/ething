<?php



class ForkTask extends Task {
	
	public $task = null;
	public $data = null;
	
	
	static public $forkInit = null;
	
	static private $currentTask = null;
	
	static public function getCurrentTask(){
		return self::$currentTask;
	}
	
	public function __construct($task, $data = null, $name = null){
		$this->task = $task;
		$this->data = isset($data) ? (is_array($data) ? $data : array($data)) : array();
		
		if(empty($name)){
			if(is_string($this->name)) $name = $this->name;
			else if(is_string($this->task)) $name = $this->task;
			else if(is_array($this->task) && is_string($this->task[1])){
				$n = is_string($this->task[0]) ? ($this->task[0].'::') : '';
				$name = $n.$this->task[1];
			};
		}
		
		parent::__construct($name);
		
	}
	
	
	
	protected function process(){
		
		if(function_exists('pcntl_fork')){
			$this->pid = pcntl_fork();
			if($this->pid !== -1){
				
				if (!$this->pid) {
					
					self::$currentTask = $this;
					
					$startTime = microtime(true);
					
					Log::debug("start task {$this->getName()}");
					
					try {
						if(is_callable(self::$forkInit)) call_user_func_array(self::$forkInit, array($this));
						$r = call_user_func_array($this->task, $this->data);
					} catch(\Exception $e){
						$r = false;
					}
					
					$endTime = microtime(true);
					
					$exitCode= $r === false ? 1 : 0;
					
					Log::debug("end task {$this->getName()} exitCode={$exitCode} duration=".($endTime - $startTime)."sec");
					
					exit($exitCode);
				}
			}
			
			return true;
			
		} else {
			throw new RuntimeException('unable to fork');
		}
		
		return false;
	}
	
	public function isRunning(){
		
		if($this->state === 'running'){
			// still running ?
			
			if($this->pid){
				$res = pcntl_waitpid($this->pid, $status, WNOHANG);
				
				// If the process has already exited
				if($res == -1 || $res > 0){
					$this->setTerminateState();
					$this->lastExitCode = pcntl_wexitstatus($status);
					
					//echo "stop {$this->data} with status = {$this->lastExitCode}\n";
				}
			}
			
		}
		
		return $this->state === 'running';
	}
	
	public function end(){
		if($this->state === 'running'){
			posix_kill($this->pid,SIGTERM);
		}
	}
	
};



