<?php

require_once __DIR__.'/ProcessTaskStream.php';

class ProcessTask extends Task {
	
	public $cmd = '';
	public $process = null;
	public $pipes;
	public $data = array('','','');
	public $stream = null;
	
	public $options = array(
		'enableStdout' => false,
		'enableStderr' => false,
		'enableStdin' => false
	);
	
	public function __construct($cmd, $name = null, array $options = array()){
		$this->cmd = $cmd;
		
		if(empty($this->cmd))
			throw new InvalidArgumentException('empty command.');
		
		if(empty($name)){
			if(is_string($this->cmd)) $name = explode(' ',trim($this->cmd))[0];
		}
		
		$this->options = array_merge($this->options, $options);
		
		parent::__construct($name);
	}
	
	protected function process(){
		if(isset($this->process)) return false;// already running!
		
		$this->pid = null;
		for($i=1; $i<3; $i++)
			$this->data[$i] = '';
		
		$descriptorspec = array();
		
		if($this->options['enableStdin'])
			$descriptorspec[0] = array("pipe", "r");
		if($this->options['enableStdout'])
			$descriptorspec[1] = array("pipe", "w");
		if($this->options['enableStderr'])
			$descriptorspec[2] = array("pipe", "w");
		
		Log::debug("Process: executing {$this->cmd}");
		
		$this->process = proc_open("exec {$this->cmd}", $descriptorspec, $this->pipes);
		
		if (is_resource($this->process)) {
			
			if($this->options['enableStdout']) stream_set_blocking($this->pipes[1], false);
			if($this->options['enableStderr']) stream_set_blocking($this->pipes[2], false);
			
			$this->pid = proc_get_status($this->process)['pid'];
			Log::info("Process: process {$this->name} pid = {$this->pid}");
			
			if($this->options['enableStdout'] || $this->options['enableStderr']){
				$this->stream = new ProcessTaskStream($this);
				PoolStream::add($this->stream);
			}
			
			return true;
		} else {
			$this->process = null;
			return false;
		}
		
	}
	
	public function write($data){
		if(isset($this->process) && !empty($data) && $this->options['enableStdin']){
			Log::debug("Process: process {$this->name} write data len=".strlen($data));
			return fwrite($this->pipes[0], $data);
		}
		return 0;
	}
	
	public function read($len = 1, $pipes = 1){
		return isset($this->process) ? fread($this->pipes[$pipes], $len) : false;
	}
	
	public function end(){
		$signal = SIGTERM;
		if(isset($this->process)){
			Log::info("Process: end process {$this->name}");
			if($this->options['enableStdin']) fclose($this->pipes[0]);
			if($this->options['enableStdout']) fclose($this->pipes[1]);
			if($this->options['enableStderr']) fclose($this->pipes[2]);
			proc_terminate($this->process, $signal);
			$exitcode = proc_close($this->process);
			if(isset($this->stream)) PoolStream::remove($this->stream);
			$this->stream = null;
			$this->setTerminateState();
			$this->lastExitCode = $exitcode;
			$this->process = null;
			Log::info("Process: process {$this->name} stop running after {$this->getDuration()} sec, exit code : {$this->lastExitCode}");
		}
	}
	
	public function isRunning(){
		
		if(isset($this->process)){
			$status = proc_get_status($this->process);
			
			if(!$status['running']){
				if($this->options['enableStdin']) fclose($this->pipes[0]);
				if($this->options['enableStdout']) fclose($this->pipes[1]);
				if($this->options['enableStderr']) fclose($this->pipes[2]);
				$this->process = null;
				if(isset($this->stream)) PoolStream::remove($this->stream);
				$this->stream = null;
				$this->lastExitCode = $status['exitcode'];
				$this->setTerminateState();
				
				Log::info("Process: process {$this->name} stop running after {$this->getDuration()} sec, exit code : {$this->lastExitCode}");
			}
			
		}
		
		return $this->state === 'running';
	}
	
	
	
};



