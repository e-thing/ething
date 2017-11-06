<?php


namespace Ething\Blea;


use \Ething\Blea\Gateway;
use \Ething\Device\BleaGateway;


class LocalGateway extends Gateway {
	
	static public $portMap = array();
	
	private $lastActivity = 0;
	private $buffer = "";
	public $process = null;
	public $pid = null;
	public $exitcode = null;
	public $startTime = null;
	public $endTime = null;
	public $port = null;
	
	private function startDaemon(){
		
		$this->pid = null;
		$this->port = null;
		$this->exitcode = null;
		$this->startTime = null;
		
		$path = __DIR__.'/../../resources/blead';
		
		for($i=5005; $i<5020; $i++){
			if(!isset(LocalGateway::$portMap[$i])){
				$this->port = $i;
				break;
			}
		}
		
		if($this->port===null){
			Log::error("Blea[local]: unable to find a free port");
			return false;
		}
		
		LocalGateway::$portMap[$this->port] = $this->gateway->id();
		
		$cmd = "python ".$path."/blead.py --device ".$this->gateway->device." --port ".$this->port." --daemonname gateway-".$this->gateway->id();
		
		$descriptorspec = array();
		
		Log::debug("Blea[local]: daemon exec = {$cmd}");
		
		$this->process = proc_open("exec {$cmd}", $descriptorspec, $pipes);
		
		if (is_resource($this->process)) {
			
			$this->startTime = microtime(true);
			$this->pid = proc_get_status($this->process)['pid'];
			Log::info("Blea[local]: daemon pid = {$this->pid}");
			
			return true;
		} else {
			Log::error("Blea[local]: unable to start the daemon process");
			$this->process = null;
			return false;
		}
		
	}
	
	private function endDaemon(){
		$signal = SIGTERM;
		if(isset($this->process)){
			Log::info("Blea[local]: end daemon");
			proc_terminate($this->process, $signal);
			$exitcode = proc_close($this->process);
			$this->endTime = microtime(true);
			$this->exitcode = $exitcode;
			$this->process = null;
			$duration = $this->endTime - $this->startTime;
			Log::info("Blea[local]: daemon stop running after {$duration} sec, exit code : {$this->exitcode}");
		}
	}
	
	
	public function update(){
		
		// check the daemon is still running !
		if(isset($this->process)){
			$status = proc_get_status($this->process);
			
			if(!$status['running']){
				$this->process = null;
				$this->endTime = microtime(true);
				$this->exitcode = $status['exitcode'];
				$duration = $this->endTime - $this->startTime;
				
				Log::info("Blea[local]: daemon unexpectedly stop running after {$duration} sec, exit code : {$this->exitcode}");
				
				$this->close();
			}
			
		}
		
		parent::update();
		
	}
	
	private function connect(){
		
		$address = 'localhost:'.$this->port;
		$stream = @stream_socket_client("tcp://".$address, $errno, $errstr, 5);
		if($stream === false)
			throw new \Exception("Blea[local]: unable to connect to the gateway {$address} : {$errstr}");
		
		// make this stream non blocking !
		stream_set_blocking($stream, false);
		
		$this->stream = $stream;
		$this->lastActivity = time();
		$this->buffer = '';
		parent::open();
		
		\Log::info("Blea[local]: opened at {$address}");
		
		return true;
	}
	
	public function open(){
		
		if($this->isOpened){
			if(!$this->close())
				return false; // unable to close !
		}
		
		if($this->startDaemon()){
			
			sleep(5); // wait for the daemon to be fully launched
			
			if($this->connect()){
				return true;
			}
		}
		
		
		return false;
	}
	
	public function read(){
		if($this->isOpened){
			
			$chunk = fgets($this->stream);
			if($chunk===false){
				// an error occurs
				$this->close();
				return;
			}
			$this->buffer .= $chunk;
			
			$this->lastActivity = time();
			
			if(strlen($chunk) === 0){
				// connection closed
				$this->close();
				
			} else if(false !== ($p = strrpos($this->buffer, "\n")) ){
				
				$lines = preg_split("/\r?\n/", substr($this->buffer, 0, $p+1));
				$this->buffer = substr($this->buffer, $p+1);
				
				foreach($lines as $line){
					
					$line = trim($line);
					if(empty($line)) continue;
					
					// each line represent json data
					
					$data = \json_decode($line, true);
					
					if(is_array($data))
						$this->processData($data);
					
				}
				
			}
		}
	}
	
	public function write(array $data){
		if($this->isOpened){
			$this->lastActivity = time();
			return @fwrite($this->stream, \json_encode($data)."\n");
		}
		return 0;
	}
	
	public function close(){
		if( $this->isOpened ){
			@fclose($this->stream);
			$this->stream = null;
		}
		
		$this->endDaemon();
		
		unset(LocalGateway::$portMap[$this->port]);
		
		parent::close();
		return !$this->isOpened;
	}
	
	
	
	
};


