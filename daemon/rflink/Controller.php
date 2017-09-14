<?php


namespace Ething\RFLink;


use \Ething\RFLink\RFLink;
use \Ething\Device\RFLinkGateway;
use \Ething\Event;

abstract class Controller extends \Stream {
	
	const AUTOCONNECT_PERIOD = 60; // seconds	
	const RESPONSE_TIMEOUT = 10; // seconds	
	
	public $gateway = null;
	
	public $gatewayLibVersion = false;
	
	protected $logger;
	
	private $lastAutoconnectLoop = 0;
	private $preventFailConnectLog = false;
	
	private $logMessage = false;
	
	protected $isOpened = false;
	
	// response management
	private $responseListeners = array();
	
	public $options = array();
	
	public function __construct(RFLinkGateway $gateway, array $options = array()){
		
		$this->gateway = $gateway;
		$this->options = array_replace_recursive($this->options, $options);
		$this->logger = $this->gateway->ething->logger();
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
		$this->isOpened = true;
		$this->logger->info("RFLink: opened");
		return true;
	}
	
	abstract public function read();
	abstract public function write($str);
	
	public function close(){
		$this->isOpened = false;
		$this->lastAutoconnectLoop = 0;
		$this->logger->info("RFLink: closed");
		return true;
	}
	
	/*
	exemple of messages :
		20;00;Nodo RadioFrequencyLink - RFLink Gateway V1.1 - R46;
		20;01;MySensors=OFF;NO NRF24L01;
		20;02;setGPIO=ON;
		20;03;Cresta;ID=8301;WINDIR=0005;WINSP=0000;WINGS=0000;WINTMP=00c3;WINCHL=00c3;BAT=LOW;
		20;04;Cresta;ID=3001;TEMP=00b4;HUM=50;BAT=OK;
		20;05;Cresta;ID=2801;TEMP=00af;HUM=53;BAT=OK;
		20;06;NewKaku;ID=008440e6;SWITCH=1;CMD=OFF;
		10;NewKaku;008440e6;1;OFF;
		10;REBOOT;
		10;PING;
		
	*/
	public function processMessage($message) {
		$r = true;
		
		$this->logger->debug("RFLink: message received = {$message}");
		
		$gateway = $this->gateway;
		
		if($this->logMessage) $gateway->log($message);
		
		$gateway->updateSeenDate();
		
		foreach($this->responseListeners as $i => $responseListener){
			
			// remove this item
			array_splice($this->responseListeners, $i, 1);
			
			if(is_callable($responseListener['callback']))
				call_user_func($responseListener['callback'], false, $message);
		}
		
		try {
			$messageInfo = RFLink::parseMessage($message);
		} catch(\Exception $e){
			return false;
		}
		
		if($messageInfo['type']==20){
			
			
			if(isset($messageInfo['protocol']) && isset($messageInfo['id'])){
				
				$protocol = $messageInfo['protocol'];
				$attr = $messageInfo['attr'];
				
				if(isset($attr['SWITCH']) && isset($attr['CMD']) && !isset($attr['RGBW']) && !isset($attr['RGB']) && in_array($attr['CMD'], array('ON', 'OFF', 'ALLON', 'ALLOFF'))){
					
					$this->switchMessageHandler($protocol, $attr);
					
				} else {
					$this->logger->warn("RFLink: unable to handle the message {$message}");
					$r = false;
				}
				
			} else if(isset($messageInfo['attr']['VER'])){
				$gateway->set('version', $messageInfo['attr']['VER']);
				$gateway->set('revision', $messageInfo['attr']['REV']);
				$gateway->set('build', $messageInfo['attr']['BUILD']);
				$this->logger->info("RFLink: ver:{$messageInfo['attr']['VER']} rev:{$messageInfo['attr']['REV']}  build:{$messageInfo['attr']['BUILD']}");
			} else {
				$this->logger->warn("RFLink: unable to handle the message {$message}");
			}
			
		}
		
		return $r;
	}
	
	//20;06;NewKaku;ID=008440e6;SWITCH=1;CMD=OFF;
	private function switchMessageHandler($protocol, $attributes){
		
		$gateway = $this->gateway;
		
		$node = $gateway->getNode(array(
			'nodeId' => $attributes['ID'],
			'switchId' => $attributes['SWITCH'],
			'protocol' => $protocol
		));
		
		if(!$node){
			// the node does not exist !
			if($gateway->inclusion){
				if(!($node = $gateway->addNode('Switch', array(
					'nodeId' => $attributes['ID'],
					'switchId' => $attributes['SWITCH'],
					'protocol' => $protocol,
					'name' => 'switch-'.$attributes['ID'].'-'.$attributes['SWITCH']
				))))
					throw new Exception("fail to create the node (Switch) nodeId={$attributes['ID']} switchId={$attributes['SWITCH']} protocol={$protocol}");
				$this->logger->info("RFLink: new node (Switch) nodeId={$attributes['ID']} switchId={$attributes['SWITCH']} protocol={$protocol}");
			}
		}
		
		if($node){
			
			$node->updateSeenDate();
			
			$node->storeData(array(
				'CMD' => $attributes['CMD']
			));
			
		}
		
		return $node;
	}
	
	private $lastState_ = false;
	
	public function update(){
		// do some stuff regularly
		$now = microtime(true);
		
		// check for a deconnection
		if(!$this->isOpened && $this->isOpened != $this->lastState_)
			$this->logger->info("RFLink: disconnected");
		$this->lastState_ = $this->isOpened;
		
		// autoconnect
		if(!$this->isOpened && ($now - $this->lastAutoconnectLoop) > self::AUTOCONNECT_PERIOD ){
			try{
				$this->open();
				$this->logger->info("RFLink: connected");
				$this->preventFailConnectLog = false;
			} catch(Exception $e){
				if(!$this->preventFailConnectLog) $this->logger->warn("RFLink: unable to connect : {$e->getMessage()}");
				$this->preventFailConnectLog = true;
			}
			$this->lastAutoconnectLoop = $now;
		}
		
		// check response timeout
		foreach($this->responseListeners as $i => $responseListener){
			if( ($now - $responseListener['ts']) > self::RESPONSE_TIMEOUT ){
				
				// remove this item
				array_splice($this->responseListeners, $i, 1);
				
				if(is_callable($responseListener['callback'])){
					call_user_func($responseListener['callback'], 'response timeout', null);
				}
			}
		}
	}
	
	
	/*
	*  $message message to send
	*  $callback (optional) function($error, $messageSent, $messageReceived = null)
	*  $waitResponse (optional) true|false wait for a response or not
	*/
	public function send($message, $callback = null, $waitResponse = null) {
		
		$this->logger->debug("RFLink: message send");
		
		if(!$this->isOpened){
			if(is_callable($callback)){
				call_user_func($callback, 'not connected', $message);
			}
			return 0;
		}
		
		
		$wb =  $this->write($message);
		
		if($waitResponse){
			// wait for a response
			$this->responseListeners[] = array(
				'callback' => function($error, $messageReceived) use($callback, $message) {
					if(is_callable($callback)) call_user_func($callback, $error, $message, $messageReceived);
				},
				'ts' => microtime(true),
				'messageSent' => $message
			);
		} else {
			if(is_callable($callback)) call_user_func($callback, false, $message);
		}
		
		return $wb;
	}
	
	protected $stream = null;
	
	public function getStream(){
		return $this->stream;
	}
	
	public function process(){
		$this->read();
	}
	
};


