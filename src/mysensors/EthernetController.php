<?php


namespace Ething\MySensors;


use \Ething\MySensors\MySensors;
use \Ething\MySensors\Message;
use \Ething\MySensors\Controller;
use \Ething\Device\MySensorsGateway;


class EthernetController extends Controller {
	
	public $stream = null;
	
	
	public function open(){
		
		if($this->isOpened){
			if(!$this->close())
				return false; // unable to close !
		}
		
		$gateway = $this->gateway;
		$address = $gateway->get('address');
		$stream = @stream_socket_client("tcp://".$address, $errno, $errstr, 10);
		if($stream === false)
			throw new Exception("unable to connect to the gateway {$address} : {$errstr}");
		
		// make this stream non blocking !
		stream_set_blocking($stream, false);
		
		$this->stream = $stream;
		
		parent::open();
		
		return true;
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
			
			if(strlen($chunk) === 0){
				// connection closed
				$this->close();
				
			} else if(false !== ($p = strrpos($this->buffer, "\n")) ){
				
				$lines = preg_split("/\r?\n/", substr($this->buffer, 0, $p+1));
				$this->buffer = substr($this->buffer, $p+1);
				
				foreach($lines as $line){
					
					$line = trim($line);
					if(empty($line)) continue;
					
					try {
						$message = Message::parse($line);
						$this->processMessage($message);
					} catch (\Exception $e) {
						// skip the line
						$this->log($e);
						continue;
					}
					
				}
				
			}
		}
	}
	
	public function write($str){
		return $this->isOpened ? @fwrite($this->stream, $str) : 0;
	}
	
	public function close(){
		if( $this->isOpened && @fclose($this->stream) ){
			$this->stream = null;
			parent::close();
		}
		return !$this->isOpened;
	}
	
	
	
	
};


