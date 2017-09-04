<?php


namespace Ething;


class Serial {
	
	const PROG = 'serial_driver.py';
	const PROG_DIR = 'python'; // relative path !
	
	public $port = null;
	public $baudrate = null;
	public $socket = null;
	
	private $process = null;
	public $pipes = null;
	
	private $pid = null;
	
	public function __construct($port, $baudrate) {
		$this->port = $port;
		$this->baudrate = $baudrate;
	}
	
	public function open(){
		
		$descriptorspec = array(
		   0 => array("pipe", "r"),  // // stdin
		   1 => array("pipe", "w")/*,  // stdout
		   2 => array("pipe", "w")*/ // stderr
		);
		
		$prog = __DIR__.'/'.self::PROG_DIR.'/'.self::PROG;
		if(!file_exists($prog)){
			//echo "proc not found {$prog}\n";
			return false;
		}
		
		$this->process = proc_open("exec python {$prog} {$this->port} {$this->baudrate}", $descriptorspec, $this->pipes);
		
		if (is_resource($this->process)) {
			
			stream_set_blocking($this->pipes[1], false);
			//stream_set_blocking($this->pipes[2], false);
			
			$this->pid = proc_get_status($this->process)['pid'];
			
			//echo "proc open pid={$this->pid} port={$this->port} baudrate={$this->baudrate}\n";
			
			return true;
			
		} else {
			//echo "proc unable opening\n";
			$this->process = null;
			return false;
		}
		
	}
	
	public function isOpen() {
		if(isset($this->process)){
			$status = proc_get_status($this->process);
			return $status['running'];
		}
		return false;
	}
	
	public function getPid(){
		return $this->pid;
	}
	
	public function write($str){
		
		if(isset($this->process) && !empty($str)){
			return fwrite($this->pipes[0], $str);
		}
		
		return 0;
	}
	
	public function read($len = 1){
		return fread($this->pipes[1], $len);
	}
	
	public function readline(){
		return fgets($this->pipes[1]);
	}
	
	public function close(){
		if(isset($this->process)){
			//echo "closing proc\n";
			fclose($this->pipes[0]);
			fclose($this->pipes[1]);
			//fclose($this->pipes[2]);
			proc_terminate($this->process, SIGTERM);
			$exitcode = proc_close($this->process);
			$this->process = null;
			//echo "proc closed\n";
		}
	}
	
	
};

