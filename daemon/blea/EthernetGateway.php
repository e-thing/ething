<?php


namespace Ething\Blea;


use \Ething\Blea\Gateway;
use \Ething\Device\BleaGateway;


class EthernetGateway extends Gateway {
	
	private $lastActivity = 0;
	private $buffer = "";
	
	
	public function open(){
		$this->lastAutoconnectLoop = microtime(true);
		
		if($this->isOpened){
			if(!$this->close())
				return false; // unable to close !
		}
		
		$gateway = $this->gateway;
		$address = $gateway->get('host').':'.$gateway->get('port');
		$stream = @stream_socket_client("tcp://".$address, $errno, $errstr, 5);
		if($stream === false)
			throw new \Exception("Blea[ethernet]: unable to connect to the gateway {$address} : {$errstr}");
		
		// make this stream non blocking !
		stream_set_blocking($stream, false);
		
		$this->registerStream($stream, 0);
		$this->lastActivity = time();
		$this->buffer = '';
		parent::open();
		
		\Log::info("Blea[ethernet]: opened at {$address}");
		
		return true;
	}
	
	public function process($stream, $id){
		if($this->isOpened){
			
			$chunk = fgets($stream);
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
			return @fwrite($this->getRegisteredStream(0), \json_encode($data)."\n");
		}
		return 0;
	}
	
	public function close(){
		if( $this->isOpened ){
			$this->closeAndUnregisterAll();
			parent::close();
		}
		return !$this->isOpened;
	}
	
	
	
	
};


