<?php


namespace Ething\RFLink;


use \Ething\RFLink\RFLink;
use \Ething\RFLink\Controller;
use \Ething\Device\RFLinkGateway;
use \Ething\Serial;

class SerialController extends Controller {
	
	private $serial = null;
	private $buffer = "";
	
	public function open(){
		
		if($this->isOpened){
			if(!$this->close())
				return false; // unable to close !
		}
		
		$gateway = $this->gateway;
		$port = $gateway->get('port');
		$baudrate = $gateway->get('baudrate');
		
		$this->serial = new Serial($port, $baudrate);
		
		// Then we need to open it
		if(!$this->serial->open())
			throw new Exception("unable to connect to the gateway {$port}, baudrate={$baudrate}");
		
		$this->stream = $this->serial->pipes[1];
		$this->buffer = '';
		
		parent::open();
		
		$this->logger->info("RFLink[serial]: opened {$port} {$baudrate}");
		
		return true;
	}
	
	public function update(){
		
		// check if the serial port is still opened !
		if($this->isOpened && !$this->serial->isOpen()){
			$this->close();
		}
		
		parent::update();
	}
	
	public function read(){
		if($this->isOpened){
			
			$chunk = '';
			while(($t = fread($this->stream, 1)) !== false && $t!=='')
				$chunk .= $t;
			
			if($chunk===''){
				// connection closed
				$this->logger->debug("RFLink[serial]: empty string received... close");
				$this->close();
			}
			
			/*$chunk = fgets($this->stream);
			if($chunk===false){
				return;
			}*/
			
			$this->buffer .= $chunk;
			
			if( false !== ($p = strrpos($this->buffer, "\n")) ){
				
				$lines = preg_split("/\r?\n/", substr($this->buffer, 0, $p+1));
				$this->buffer = substr($this->buffer, $p+1);
				
				foreach($lines as $line){
					
					$line = trim($line);
					if(empty($line)) continue;
					
					try {
						$this->processMessage($line);
						
					} catch (\Exception $e) {
						// skip the line
						$this->logger->warn("RFLink[serial]: unable to handle the message {$line}");
						continue;
					}
					
				}
				
			}
		}
	}
	
	public function write($str){
		if($this->isOpened){
			$this->logger->debug("RFLink[serial]: send message = {$str}");
			$this->serial->write($str."\r\n");
		} else {
			return 0;
		}
	}
	
	public function close(){
		if( $this->isOpened ){
			$this->serial->close();
			$this->stream = null;
			parent::close();
			$this->logger->info("RFLink[serial]: closed");
		}
		return !$this->isOpened;
	}
	
	
	
	
};


