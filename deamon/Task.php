<?php



class Task {
	
	public $task = null;
	public $data = null;
	public $priority = 0;
	public $pid = null;
	public $state = 'pending';
	public $status = null;
	
	public static $preProcFn = null;
	
	public function __construct($task, $data = null, $priority = 0){
		$this->task = $task;
		$this->data = isset($data) ? (is_array($data) ? $data : array($data)) : array();
		$this->priority = $priority;
	}
	
	
	public function run(){
		
		$this->state = 'running';
		
		if(function_exists('pcntl_fork')){
			$this->pid = pcntl_fork();
			if($this->pid !== -1){
				
				if (!$this->pid) {
					try {
						if(is_callable(self::$preProcFn)) call_user_func_array(self::$preProcFn, array($this));
						$r = call_user_func_array($this->task, $this->data);
					} catch(\Exception $e){
						$r = false;
					}
					exit($r === false ? 1 : 0);
				}
			}
			return;
			
		}
		
		// fork not possible, execute it in the current process
		$this->pid = -1;
		if(is_callable(self::$preProcFn)) call_user_func_array(self::$preProcFn, array($this));
		$r = call_user_func_array($this->task, $this->data);
		$this->state = 'terminated';
		$this->status = $r === false ? 1 : 0;
		
	}
	
	public function isRunning(){
		
		if($this->state === 'running'){
			// still running ?
			
			if($this->pid){
				$res = pcntl_waitpid($this->pid, $status, WNOHANG);
				
				// If the process has already exited
				if($res == -1 || $res > 0){
					$this->state = 'terminated';
					$this->status = pcntl_wexitstatus($status);
					
					//echo "stop {$this->data} with status = {$this->status}\n";
				}
			}
			
		}
		
		return $this->state === 'running';
	}
	
};



