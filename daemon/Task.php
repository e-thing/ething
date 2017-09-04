<?php



class Task {
	
	public $task = null;
	public $data = null;
	public $priority = 0;
	public $pid = null;
	public $state = 'pending';
	public $status = null;
	public $name = null;
	public $startTime = null;
	public $endTime = null;
	
	
	public static $forkInit = null;
	
	static private $currentTask = null;
	
	static public function getCurrentTask(){
		return self::$currentTask;
	}
	
	public function __construct($task, $data = null, $priority = 0, $name = null){
		$this->task = $task;
		$this->data = isset($data) ? (is_array($data) ? $data : array($data)) : array();
		$this->priority = $priority;
		$this->setName($name);
	}
	
	public function setName($name){
		$this->name = $name;
	}
	
	public function getName(){
		if(is_string($this->name)) return $this->name;
		else if(is_string($this->task)) return $this->task;
		else if(is_array($this->task) && is_string($this->task[1])){
			$n = is_string($this->task[0]) ? ($this->task[0].'::') : '';
			return $n.$this->task[1];
		} else return '?';
	}
	
	public function getDuration(){
		if(isset($this->startTime)){
			$end = isset($this->endTime) ? $this->endTime : microtime(true);
			return $end - $this->startTime;
		}
		return 0.;
	}
	
	public function run(){
		
		$this->startTime = microtime(true);
		$this->endTime = null;
		$this->state = 'running';
		
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
			return;
			
		} else {
			throw new RuntimeException('unable to fork');
		}
		
		// fork not possible, execute it in the current process
		/*$this->pid = -1;
		$r = call_user_func_array($this->task, $this->data);
		$this->endTime = microtime(true);
		$this->state = 'terminated';
		$this->status = $r === false ? 1 : 0;*/
		
	}
	
	public function isRunning(){
		
		if($this->state === 'running'){
			// still running ?
			
			if($this->pid){
				$res = pcntl_waitpid($this->pid, $status, WNOHANG);
				
				// If the process has already exited
				if($res == -1 || $res > 0){
					$this->endTime = microtime(true);
					$this->state = 'terminated';
					$this->status = pcntl_wexitstatus($status);
					
					//echo "stop {$this->data} with status = {$this->status}\n";
				}
			}
			
		}
		
		return $this->state === 'running';
	}
	
};



