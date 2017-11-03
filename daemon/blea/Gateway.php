<?php


namespace Ething\Blea;

use \Ething\Blea\Controller;
use \Ething\Device\BleaGateway;
use \Ething\Event;

abstract class Gateway extends \Stream {
	
	const AUTOCONNECT_PERIOD = 15; // seconds	
	
	public $controller = null;
	public $gateway = null;
	
	
	private $lastAutoconnectLoop = 0;
	private $preventFailConnectLog = 0;
	
	protected $isOpened = false;
	
	public $options = array(
		'onMessage' => null // fired on every message (except ack)
	);
	
	public function __construct(Controller $controller, BleaGateway $gateway, array $options = array()){
		
		$this->controller = $controller;
		$this->gateway = $gateway;
		$this->options = array_replace_recursive($this->options, $options);
		
	}
	
	public function ething(){
		return $this->gateway->ething;
	}
	
	public function name(){
		return $this->gateway->name();
	}
	
	public function __get($name){
		return isset($this->options[$name]) ? $this->options[$name] : null;
    }
	
	public function open(){
		$this->gateway->setConnectState(true);
		$this->isOpened = true;
		return true;
	}
	
	abstract public function read();
	abstract public function write(array $data);
	
	public function close(){
		$this->isOpened = false;
		$this->lastAutoconnectLoop = 0;
		$this->gateway->setConnectState(false);
		\Log::info("Blea: closed");
		return true;
	}
	
	protected function processData(array $data){
		if(!empty($data)) $this->controller->processData($this->gateway, $data);
	}
	
	private $lastState_ = false;
	
	public function update(){
		// do some stuff regularly
		$now = microtime(true);
		
		
		
		// check for a deconnection
		if(!$this->isOpened && $this->isOpened != $this->lastState_)
			\Log::info("Blea: disconnected");
		$this->lastState_ = $this->isOpened;
		
		// autoconnect
		if(!$this->isOpened && ($now - $this->lastAutoconnectLoop) > self::AUTOCONNECT_PERIOD ){
			try{
				$this->open();
				$this->preventFailConnectLog = 0;
			} catch(\Exception $e){
				$this->gateway->setConnectState(false);
				
				if($this->preventFailConnectLog % 20 === 0) \Log::warn("Blea: unable to connect : {$e->getMessage()}");
				$this->preventFailConnectLog += 1;
			}
			$this->lastAutoconnectLoop = $now;
		}
		
	}
	
	
	
	
	
	protected $stream = null;
	
	public function getStreams(){
		return array($this->stream);
	}
	
	public function process($stream){
		$data = $this->read();
	}
	
	
};


