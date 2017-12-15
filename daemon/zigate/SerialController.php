<?php


namespace Ething\Zigate;


use \Ething\Zigate\Controller;
use \Ething\Device\ZigateGateway;
use \Ething\Zigate\Message;
use \Ething\Serial;

class SerialController extends Controller {
	
	private $serial = null;
	private $buffer = "";
	private $transcodage = false;
	
	public function open(){
		$this->lastAutoconnectLoop = microtime(true);
		
		if($this->isOpened){
			if(!$this->close())
				return false; // unable to close !
		}
		
		$gateway = $this->gateway;
		$port = $gateway->get('port');
		$baudrate = 115200;
		
		$this->serial = new Serial($port, $baudrate);
		
		// Then we need to open it
		if(!$this->serial->open())
			throw new \Exception("unable to connect to the gateway {$port}, baudrate={$baudrate}");
		
		$stream = $this->serial->pipes[1];
		$this->registerStream($stream, 0);
		$this->buffer = '';
		$this->transcodage = false;
		
		parent::open();
		
		\Log::info("Zigate[serial]: opened {$port} {$baudrate}");
		
		return true;
	}
	
	public function update(){
		
		// check if the serial port is still opened !
		if($this->isOpened && !$this->serial->isOpen()){
			$this->close();
		}
		
		parent::update();
	}
	
	public function process($stream, $id){
		if($this->isOpened){
			
			$chunk = '';
			while(($t = fread($stream, 1)) !== false && $t!==''){
				$t=bin2hex($t);
				
				if($t=="02"){
					$this->transcodage = true;
				} else {
					
					if ($this->transcodage) {
						$t.= sprintf("%02X",(hexdec($t) ^ 0x10));
						$this->transcodage = false;
					}
					
					$chunk .= $t;
					
				}
				
			}
			
			if($chunk===''){
				// connection closed
				\Log::debug("Zigate[serial]: empty string received... close");
				$this->close();
			}
			
			$this->buffer .= $chunk;
			
			if( false !== ($p = strrpos($this->buffer, "03")) ){
				
				$packets = explode("03", substr($this->buffer, 0, $p));
				$this->buffer = substr($this->buffer, $p+2);
				
				foreach($packets as $packet){
					
					if(empty($packet)) {
						continue;
					}
					
					try {
						
						$message = Message::parse($packet."03");
						$this->processMessage($message);
						
					} catch (\Exception $e) {
						// skip the packet
						\Log::warn("Zigate[serial]: unable to handle the packet {$packet} : ".$e->getMessage());
						continue;
					}
					
				}
				
			}
		}
	}
	
	public function write($str){
		if($this->isOpened){
			$this->serial->write($str);
		} else {
			return 0;
		}
	}
	
	public function close(){
		if( $this->isOpened ){
			$this->serial->close();
			$this->unregisterAll();
			parent::close();
			\Log::info("Zigate[serial]: closed");
		}
		return !$this->isOpened;
	}
	
	
	
	
};


