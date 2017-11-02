<?php


namespace Ething\RFLink;


use \Ething\RFLink\RFLink;
use \Ething\Device\RFLinkGateway;
use \Ething\Device\RFLinkNode;
use \Ething\Event;

abstract class Controller extends \Stream {
	
	const AUTOCONNECT_PERIOD = 60; // seconds	
	const RESPONSE_TIMEOUT = 10; // seconds	
	
	public $gateway = null;
	
	public $gatewayLibVersion = false;
	
	protected $lastAutoconnectLoop = 0;
	private $preventFailConnectLog = 0;
	
	private $logMessage = false;
	
	protected $isOpened = false;
	
	// response management
	private $responseListeners = array();
	
	public $options = array();
	
	public function __construct(RFLinkGateway $gateway, array $options = array()){
		
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
	abstract public function write($str);
	
	public function close(){
		$this->isOpened = false;
		$this->lastAutoconnectLoop = 0;
		$this->gateway->setConnectState(false);
		\Log::info("RFLink: closed");
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
		20;02;VER=1.1;REV=46;BUILD=0c;
	*/
	function processLine($line){
		
		\Log::debug("RFLink: message received = {$line}");
		
		$gateway = $this->gateway;
		if($this->logMessage) $gateway->log($line);
		$inclusion = $gateway->inclusion;
		$gateway->updateSeenDate();
		
		$words = explode(';', rtrim($line,";"));
		$wordsCount = count($words);
		
		if($wordsCount<3) return;
		
		// keep only messages destined to the gateway
		if($words[0]!=="20") return;
		
		if($wordsCount === 3 || substr($words[2], 0, 4)==='VER='){
			// system command/response
			
			// does a user request wait for a response
			foreach($this->responseListeners as $i => $responseListener){
				// remove this item
				array_splice($this->responseListeners, $i, 1);
				
				if(is_callable($responseListener['callback']))
					call_user_func($responseListener['callback'], false, $line);
			}
			
			if(preg_match('/Nodo RadioFrequencyLink - RFLink Gateway V([\d\.]+) - R([\d]+)/', $words[2], $matches)){
				$gateway->set('version', $matches[1]);
				$gateway->set('revision', $matches[2]);
				\Log::info("RFLink: ver:{$matches[1]} rev:{$matches[2]}");
			} else if(preg_match('/;VER=([\d\.]+);REV=([\d]+);BUILD=([0-9a-fA-F]+);/', $line, $matches)) {
				$gateway->set('version', $matches[1]);
				$gateway->set('revision', $matches[2]);
				$gateway->set('build', $matches[3]);
				\Log::info("RFLink: ver:{$matches[1]} rev:{$matches[2]} build:{$matches[3]}");
			}
			
		} else {
			
			$protocol = $words[2];
			$args = array();
			
			for($i=3; $i<$wordsCount; $i++){
				
				if( $sepi = strpos($words[$i], '=') ){
					// key value pair
					$key = substr($words[$i], 0, $sepi);
					$value = substr($words[$i], $sepi+1);
					
					$args[$key] = $value;
				}
			}
			
			if(isset($args['ID'])){
				
				$device = null;
				
				$switchId = isset($args['SWITCH']) ? RFLink::convertSwitchId($args['SWITCH']) : null;
				
				$device = $gateway->getNode(array(
					'nodeId' => $args['ID'],
					'protocol' => $protocol,
					'switchId' => $switchId
				));
				
				if(!$device){
					if($inclusion){
						// the device does not exist !
						
						// find the best subType suited from the protocol and args
						if($subType = RFLink::getSubType($protocol, $args)){
						
							// create it !
							if($device = RFLinkNode::createDeviceFromMessage($subType, $protocol, $args, $gateway)){
								\Log::info("RFLink: new node ({$subType}) from {$line}");
							} else {
								\Log::error("RFLink: fail to create the node ({$subType}) from {$line}");
							}
						} else {
							\Log::warn("RFLink: unable to handle the message {$line}");
						}
					} else {
						\Log::warn("RFLink: new node from {$line}, rejected because inclusion=false");
					}
				}
				
				if($device){
					$device->processMessage($protocol, $args);
				}
			
			} else {
				\Log::warn("RFLink: unable to handle the message {$line}, no id.");
			}
			
		}
		
	}
	
	
	private $lastState_ = false;
	
	public function update(){
		// do some stuff regularly
		$now = microtime(true);
		
		// check for a deconnection
		if(!$this->isOpened && $this->isOpened != $this->lastState_)
			\Log::info("RFLink: disconnected");
		$this->lastState_ = $this->isOpened;
		
		// autoconnect
		if(!$this->isOpened && ($now - $this->lastAutoconnectLoop) > self::AUTOCONNECT_PERIOD ){
			try{
				$this->open();
				$this->preventFailConnectLog = 0;
			} catch(\Exception $e){
				$this->gateway->setConnectState(false);
				
				if($this->preventFailConnectLog % 20 === 0) \Log::warn("RFLink: unable to connect : {$e->getMessage()}");
				$this->preventFailConnectLog += 1;
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
		
		\Log::debug("RFLink: message send");
		
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
	
	public function getStreams(){
		return array($this->stream);
	}
	
	public function process($stream){
		$this->read();
	}
	
};


