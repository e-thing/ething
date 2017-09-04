<?php


namespace Ething\MySensors;


use \Ething\MySensors\MySensors;
use \Ething\MySensors\Message;
use \Ething\Device\MySensorsGateway;
use \Ething\Device\MySensorsNode;
use \Ething\Device\MySensorsSensor;
use \Ething\Event;

abstract class Controller extends \Stream {
	
	const ACK_TIMEOUT = 5; // seconds (maybe float number)
	const AUTOCONNECT_PERIOD = 15; // seconds
	const PENDING_MESSAGE_TIMEOUT = 120; // seconds (maybe float number)
	const FIRMWARE_BLOCK_SIZE = 16; // in bytes
	const FIRMWARE_UPDATE_TIMEOUT = 40; // in seconds, let the time for the node to restart and install the new firmware
	const RESPONSE_TIMEOUT = 10;
	const STREAM_TIMEOUT = 10; // in seconds, max allowed time between 2 blocks of data
	
	
	public $gateway = null;
	
	public $gatewayReady = false;
	public $gatewayLibVersion = false;
	
	// ack management
	private $ackWaitingMessages = array();
	
	// used for smartSleep
	private $pendingMessages = array();
	
	// firmware
	private $pendingFirmware = array();
	
	// streams
	private $pendingStreams = array();
	
	// response management
	private $responseListeners = array();
	
	private $lastAutoconnectLoop = 0;
	private $preventFailConnectLog = false;
	
	private $logMessage = false;
	
	protected $isOpened = false;
	
	protected $logger;
	
	public $options = array(
		'isMetric' => true, // Metric or Imperial
		'onMessage' => null // fired on every message (except ack)
	);
	
	public function __construct(MySensorsGateway $gateway, array $options = array()){
		
		$this->gateway = $gateway;
		$this->options = array_replace_recursive($this->options, $options);
		
		$this->options['isMetric'] = $gateway->isMetric();
		
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
		return true;
	}
	
	abstract public function read();
	abstract public function write($str);
	
	public function close(){
		$this->isOpened = false;
		$this->lastAutoconnectLoop = 0;
		$this->logger->info("MySensors: closed");
		return true;
	}
	
	protected function createNode($nodeId){
		$gateway = $this->gateway;
		if(!($node = $gateway->addNode(array(
			'nodeId' => $nodeId,
			'name' => $gateway->name().'/node-'.$nodeId
		))))
			throw new Exception("fail to create the node nodeId={$nodeId}");
		$this->logger->info("MySensors: new node nodeId={$nodeId}");
		return $node;
	}
	
	protected function createSensor(MySensorsNode $node, $sensorId, $sensorType = MySensors::S_UNK){
		
		if(!($sensor = $node->addSensor(array(
			'name' => $sensorType === MySensors::S_UNK ? $node->name().'/sensor-'.$sensorId : MySensors::sensorTypeToName($sensorType),
			'sensorId' => $sensorId,
			'sensorType' => $sensorType
		)))){
			throw new Exception("fail to create the sensor nodeId={$node->nodeId()} sensorId={$sensorId} sensorType={$sensorType}");
		}
		$this->logger->info("MySensors: new sensor nodeId={$node->nodeId()} sensorId={$sensorId} sensorType={$sensorType}");
		return $sensor;
	}
	
	public function processMessage(Message $message) {
		$r = true;
		
		$this->logger->debug("MySensors: message received {$message}");
		
		$gateway = $this->gateway;
		$nodeId = $message->nodeId;
		$sensorId = $message->childSensorId;
		$node = null;
		$sensor = null;
		
		if($this->logMessage) $gateway->log($message);
		
		// automatically create unknown node and sensor
		if($nodeId > 0 && $nodeId != MySensors::BROADCAST_ADDRESS){
			if(!($node = $gateway->getNode($nodeId)))
				$node = $this->createNode($nodeId);
		}
		
		if($node && $sensorId >= 0 && $sensorId != MySensors::INTERNAL_CHILD){
			if(!($sensor = $node->getSensor($sensorId))){
				$sensor = $this->createSensor($node, $sensorId, $message->messageType===MySensors::PRESENTATION ? $message->subType : MySensors::S_UNK);
			}
		}
		
		if($gateway) $gateway->updateSeenDate();
		if($node) $node->updateSeenDate();
		if($sensor) $sensor->updateSeenDate();
		
		// is ack ?
		if( $message->ack === MySensors::NO_ACK ){

			try {
								
				switch($message->messageType) {
					
					case MySensors::PRESENTATION:
						$sensorType = $message->subType;
						
						// get sensor
						if($sensor){
							$sensor->set('sensorType', $sensorType); // update type
							
							if($message->payload){ // description of the sensor
								$sensor->set('description', $message->payload);
							}
						} else {
							// node internal sensor (id=0xFF)
							if($message->payload){ // library version (node device)
								$node->set('libVersion', $message->payload);
							}
						}
						
						break;
					
					case MySensors::SET:
						
						if($sensor){
							
							$this->logger->debug("MySensors: set value nodeId={$nodeId} sensorId={$sensorId} valueType={$message->subType} value={$message->payload}");
							if(($datatype = MySensors::valueTypeStr($message->subType)) !== null){
								$value = $message->getValue();
								$sensor->storeData($datatype, $value);
							} else {
								$this->logger->warn("MySensors: unknown value subtype {$message->subType}");
							}
						}
						
						break;
					
					case MySensors::REQ:
						
						if($sensor){
							if(($datatype = MySensors::valueTypeStr($message->subType)) !== null){
								$value = $sensor->getData($datatype);
								if(isset($value)){
									$response = new Message($nodeId, $sensorId, MySensors::SET, MySensors::NO_ACK, $message->subType, $value);
									$this->send($response);
								} else {
									// no value stored ! No response
								}
							} else {
								$this->logger->warn("MySensors: unknown value subtype {$message->subType}");
							}
						}
						
						break;
					
					case MySensors::INTERNAL:
						
						switch($message->subType){
							
							case MySensors::I_GATEWAY_READY :
								$this->gatewayReady = true;
								$this->logger->info("info: gateway ready");
								break;
							
							case MySensors::I_VERSION :
								$this->gatewayLibVersion = $message->payload;
								$gateway->set('libVersion', $message->payload);
								$this->logger->info("MySensors: gateway version = {$this->gatewayLibVersion}");
								break;
							
							case MySensors::I_TIME :
								// return current time
								$response = new Message($message->nodeId, $message->childSensorId, MySensors::INTERNAL, MySensors::NO_ACK, MySensors::I_TIME, \time());
								$this->send($response);
								break;
								
							case MySensors::I_CONFIG :
								// return M (metric) or I (Imperial)
								$response = new Message($message->nodeId, $message->childSensorId, MySensors::INTERNAL, MySensors::NO_ACK, MySensors::I_CONFIG, $this->isMetric ? 'M' : 'I');
								$this->send($response);
								break;
								
							case MySensors::I_ID_REQUEST :
								// get a free node id
								for($i=1; $i<255; $i++){
									if(!$gateway->getNode($i))
										break;
								}
								if($i<255){
									$response = new Message(MySensors::BROADCAST_ADDRESS, MySensors::INTERNAL_CHILD, MySensors::INTERNAL, MySensors::NO_ACK, MySensors::I_ID_RESPONSE, $i);
									$this->send($response);
								} else {
									throw new Exception('No free id available');
								}
								break;
							
							case MySensors::I_SKETCH_NAME :
								if($node){
									$node->set('sketchName', $message->payload);
									// if the default name has not been changed by the user, overwrite it with the sketch name
									if(preg_match('@^.+/node-[0-9]+$@',$node->name())){
										$node->set('name', $message->payload);
									}
								}
								break;
								
							case MySensors::I_SKETCH_VERSION :
								if($node){
									$node->set('sketchVersion', $message->payload);
								}
								break;
								
							case MySensors::I_BATTERY_LEVEL :
								if($node){
									$batteryLevel = intval($message->payload);
									if($batteryLevel<0) $batteryLevel = 0;
									if($batteryLevel>100) $batteryLevel = 100;
									$node->set('battery', $batteryLevel);
								}
								
								break;
							
							case MySensors::I_HEARTBEAT_RESPONSE :
								
								// check if there are some pending messages in queue (smartSleep)
								foreach($this->pendingMessages as $i => $pendingMessage){
									$originalMessage = $pendingMessage['message'];
									
									if( 
										$originalMessage->nodeId === $message->nodeId
									) {
										// remove this item
										array_splice($this->pendingMessages, $i, 1);
										
										$this->send($originalMessage, false, $pendingMessage['callback']);
									}
									
								}
								
								break;
							case MySensors::I_LOG_MESSAGE :
								$this->logger->info("MySensors: nodeId={$message->nodeId} sensorId={$message->childSensorId} {$message->payload}");
								break;
							
							default:
								$this->logger->warn("MySensors: message not processed {$message->messageType} {$message->subType} nodeId={$message->nodeId} sensorId={$message->childSensorId} {$message->payload}");
								break;
								
						}
						
						break;
					
					case MySensors::STREAM:
						
						switch($message->subType){
							
							case MySensors::ST_FIRMWARE_CONFIG_REQUEST :
								/*
								the payload contains the folowing (encoded in hexadecimal):
									uint16_t type;								//!< Type of config
									uint16_t version;							//!< Version of config
									uint16_t blocks;							//!< Number of blocks
									uint16_t crc;								//!< CRC of block data
									uint16_t BLVersion;							//!< Bootloader version
								*/
								
								$parts = unpack("n*", $message->payload);
								if(count($parts)>=4){
									list($type, $version, $nbBlocks, $crc) = $parts;
									$bootloaderVersion = count($parts)>4 ? $parts[4] : 0;
									
									$this->logger->info(sprintf("MySensors: FW CONFIG : nodeId=%d type=%04X version=%04X blocks=%d crc=%04X BLVersion=%04X", $nodeId, $type, $version, $nbBlocks, $crc, $bootloaderVersion));
									
									if($node){
										$node->set('firmware', array(
											'type' => $type,
											'version' => $version,
											'blocks' => $nbBlocks,
											'crc' => $crc,
											'BLVersion' => $bootloaderVersion
										));
									}
									
									
									if(isset($this->pendingFirmware[$nodeId])){
										// a firware has been updated
										// this message is received after reboot
										
										// check if the installed firmware was the one updated
										$firmwareInfo = $this->pendingFirmware[$nodeId];
										$ok = $firmwareInfo['type'] === $type && $firmwareInfo['version'] === $version && $firmwareInfo['blocks'] === $blocks && $firmwareInfo['crc'] === $crc;
										
										if($ok){
											$this->logger->info(sprintf("MySensors: FW updated successfully : nodeId=%d type=%04X version=%04X blocks=%d crc=%04X", $nodeId, $type, $version, $nbBlocks, $crc));
										} else {
											$this->logger->warn(sprintf("MySensors: FW update ERROR : nodeId=%d", $nodeId));
										}
										
										if(is_callable($firmwareInfo['callback'])){
											call_user_func($firmwareInfo['callback'], $ok ? false : 'error in firmware update');
										}
										
										unset($this->pendingFirmware[$nodeId]);
									}
									
								}
								
								
								
								break;
							case MySensors::ST_FIRMWARE_CONFIG_RESPONSE :
								break;
							case MySensors::ST_FIRMWARE_REQUEST :
								/*
								return a peace of the FIRMWARE
								
								receive :
								uint16_t type;		//!< Type of config
								uint16_t version;	//!< Version of config
								uint16_t block;		//!< Block index
								
								send:
								uint16_t type;						//!< Type of config
								uint16_t version;					//!< Version of config
								uint16_t block;						//!< Block index
								uint8_t data[FIRMWARE_BLOCK_SIZE];	//!< Block data
								*/
								
								if(strlen($message->payload)>=6){
									
									list($type, $version, $iBlock) = unpack("n3", $message->payload);
									
									$this->logger->warn(sprintf("MySensors: FW GET : nodeId=%d type=%04X version=%04X block=%d", $nodeId, $type, $version, $iBlock));
									
									if(isset($this->pendingFirmware[$nodeId])){
										$chunk = substr($this->pendingFirmware[$nodeId]['firmware'], $iBlock*static::FIRMWARE_BLOCK_SIZE, static::FIRMWARE_BLOCK_SIZE);
										$response = new Message($message->nodeId, MySensors::INTERNAL_CHILD, MySensors::STREAM, MySensors::NO_ACK, MySensors::ST_FIRMWARE_CONFIG_RESPONSE, pack('nnn',$type, $version, $iBlock).$chunk);
										
										if($this->pendingFirmware[$nodeId]['lastBlockSent'] !== $iBlock){
											$this->pendingFirmware[$nodeId]['blockSent']++;
											$this->pendingFirmware[$nodeId]['lastBlockSent'] = $iBlock;
										}
										
										$this->pendingFirmware[$nodeId]['ts'] = microtime(true);
										
										$this->send($response);
										
									} else {
										$this->logger->warn("MySensors: FW GET : no firmware found");
									}
								}
								
								break;
							case MySensors::ST_FIRMWARE_RESPONSE :
								break;
							
							case MySensors::ST_SOUND :
							case MySensors::ST_IMAGE :
								
								/*
								the payload contains a piece of an image or sound
								
								payload :
								
								| 1byte | next bytes |
								|-------|------------|
								| index | data       |
								
								*/
								$payload = $message->fromHex();
								if(!empty($payload)){
									$index = ord($payload);
									
									if(!isset($this->pendingStreams[$nodeId])){
										if($index===1){
											// new stream
											$this->pendingStreams[$nodeId] = array(
												't0' => microtime(true),
												'ts' => 0,
												'lastIndex' => 255,
												'data' => '',
												'packetCount' => 0,
												'type' => $message->subType
											);
										} else {
											$this->logger->warn("MySensors: STREAM: first packet must start with index=1, got {$index}");
											break;
										}
									}
									
									if(isset($this->pendingStreams[$nodeId])){
										
										$stream = &$this->pendingStreams[$nodeId];
										
										if($stream['type']===$message->subType){
											$expectedIndex = $stream['lastIndex']===255 ? 1 : $stream['lastIndex']+1;
											
											if($index===0 || $expectedIndex === $index){
												// append this chunk
												$stream['data'] .= substr($payload, 1);
												$stream['lastIndex'] = $index;
												$stream['packetCount']++;
												$stream['ts'] = microtime(true);
												
												if($index===0){
													// end of the stream
													
													$size = strlen($stream['data']);
													$timeElapsed = microtime(true) - $stream['t0'];
													
													$sensor->storeStream($stream['type'], $stream['data']);
													
													// remove stream from list
													unset($this->pendingStreams[$nodeId]);
													
													
													$this->logger->warn("MySensors: STREAM: end of stream, packetCount={$stream['packetCount']}, size(B)={$size}, time(s)={$timeElapsed}");
												}
												
											} else {
												unset($this->pendingStreams[$nodeId]); // remove on first error
												$this->logger->warn("MySensors: STREAM: index mismatch");
											}
										} else {
											$this->logger->warn("MySensors: STREAM: type mismatch");
										}
									}
									
								}
								
								break;
							
							default:
								$this->logger->warn("MySensors: message not processed {$message->messageType} {$message->subType} nodeId={$message->nodeId} sensorId={$message->childSensorId} {$message->payload}");
								break;
							
						}
						
						break;
					
					default:
						throw new Exception("unknown message {$message}");
						break;
				}
			
			} catch(\Exception $e){
				$this->logger->error($e);
				$r = false;
			}
			
			
			foreach($this->responseListeners as $i => $responseListener){
				if( 
					(!isset($responseListener['nodeId']) || $responseListener['nodeId'] === $message->nodeId) &&
					(!isset($responseListener['childSensorId']) || $responseListener['childSensorId'] === $message->childSensorId) &&
					(!isset($responseListener['messageType']) || $responseListener['messageType'] === $message->messageType) &&
					(!isset($responseListener['subType']) || $responseListener['subType'] === $message->subType)
				) {
					// remove this item
					array_splice($this->responseListeners, $i, 1);
					
					if(is_callable($responseListener['callback']))
						call_user_func($responseListener['callback'], false, $message);
				}
			}
			
			
			if(is_callable($this->onMessage))
				call_user_func($this->onMessage, $message, $this);
			
		} else {
			// ack message
			
			foreach($this->ackWaitingMessages as $i => $ackWaitingMessage){
				$originalMessage = $ackWaitingMessage['message'];
				if( 
					$originalMessage->nodeId === $message->nodeId &&
					$originalMessage->childSensorId === $message->childSensorId &&
					$originalMessage->messageType === $message->messageType &&
					$originalMessage->subType === $message->subType
				) {
					// remove this item
					array_splice($this->ackWaitingMessages, $i, 1);
					
					$callback = $ackWaitingMessage['callback'];
					if(is_callable($callback)){
						call_user_func($callback, false, $originalMessage);
					}
					
					break;
				}
				
			}
			
		}
		
		return $r;
	}
	
	
	private $lastState_ = false;
	
	public function update(){
		// do some stuff regularly
		$now = microtime(true);
		
		// check for timeout ack messages 
		foreach($this->ackWaitingMessages as $i => $ackWaitingMessage){
			if( ($now - $ackWaitingMessage['ts']) > self::ACK_TIMEOUT ){
				
				// remove this item
				array_splice($this->ackWaitingMessages, $i, 1);
				
				if(is_callable($ackWaitingMessage['callback'])){
					call_user_func($ackWaitingMessage['callback'], 'ack timeout', $ackWaitingMessage['message']);
				}
			}
		}
		
		// check for pending message timeout
		foreach($this->pendingMessages as $i => $pendingMessage){
			if( ($now - $pendingMessage['ts']) > self::PENDING_MESSAGE_TIMEOUT ){

				// remove this item
				array_splice($this->pendingMessages, $i, 1);
				
				if(is_callable($pendingMessage['callback'])){
					call_user_func($pendingMessage['callback'], 'smartSleep timeout', $pendingMessage['message']);
				}
			}
		}
		
		// check firmware update timeout
		foreach($this->pendingFirmware as $nodeId => $firmwareInfo){
			if( ($now - $firmwareInfo['ts']) > self::FIRMWARE_UPDATE_TIMEOUT ){
				
				// remove this item
				unset($this->pendingFirmware[$nodeId]);
				
				if(is_callable($firmwareInfo['callback'])){
					call_user_func($firmwareInfo['callback'], 'firmware update timeout');
				}
			}
		}
		
		// check stream timeout
		foreach($this->pendingStreams as $nodeId => $stream){
			if( ($now - $stream['ts']) > self::STREAM_TIMEOUT ){
				
				// remove this item
				unset($this->pendingStreams[$nodeId]);
			}
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
		
		
		// check for a deconnection
		if(!$this->isOpened && $this->isOpened != $this->lastState_)
			$this->logger->info("MySensors: disconnected");
		$this->lastState_ = $this->isOpened;
		
		// autoconnect
		if(!$this->isOpened && ($now - $this->lastAutoconnectLoop) > self::AUTOCONNECT_PERIOD ){
			try{
				$this->open();
				$this->logger->info("MySensors: connected");
				$this->preventFailConnectLog = false;
			} catch(Exception $e){
				if(!$this->preventFailConnectLog) $this->logger->warn("MySensors: unable to connect : {$e->getMessage()}");
				$this->preventFailConnectLog = true;
			}
			$this->lastAutoconnectLoop = $now;
		}
		
	}
	
	
	/*
	*  $message message to send
	*  $smartSleep (optional) true|false|null if a boolean is given, force or not the smartSleep feature
	*  $callback (optional) function($error, $messageSent, $messageReceived = null)
	*  $waitResponse (optional) true|false wait for a response or not
	*/
	public function send(Message $message, $smartSleep = null, $callback = null, $waitResponse = null) {
		
		
		if(is_callable($smartSleep)){
			$waitResponse = $callback;
			$callback = $smartSleep;
			$smartSleep = null;
		}
		
		if($this->logMessage) $this->gateway->log($message, true);
		
		if($smartSleep===null){
			$smartSleep = false;
			if($message->nodeId!==MySensors::GATEWAY_ADDRESS && $message->nodeId!==MySensors::BROADCAST_ADDRESS){
				$destinationNode = $this->gateway->getNode($message->nodeId);
				if($destinationNode){
					$smartSleep = $destinationNode->smartSleep;
				}
			}
		}
		
		if($waitResponse){
			$self = $this;
			$userCallback = $callback;
			
			if($waitResponse===true){
				
				switch($message->messageType){
					
					case MySensors::REQ :
						$waitResponse = array(
							'messageType' => MySensors::SET
						);
						break;
						
					case MySensors::INTERNAL :
						
						switch($message->subType){
							
							case MySensors::I_ID_REQUEST :
								$waitResponse = array(
									'subType' => MySensors::I_ID_RESPONSE
								);
								break;
							case MySensors::I_NONCE_REQUEST :
								$waitResponse = array(
									'subType' => MySensors::I_NONCE_RESPONSE
								);
								break;
							case MySensors::I_HEARTBEAT_REQUEST :
								$waitResponse = array(
									'subType' => MySensors::I_HEARTBEAT_RESPONSE
								);
								break;
							case MySensors::I_DISCOVER_REQUEST :
								$waitResponse = array(
									'subType' => MySensors::I_DISCOVER_RESPONSE
								);
								break;
							case MySensors::I_PING :
								$waitResponse = array(
									'subType' => MySensors::I_PONG
								);
								break;
							case MySensors::I_REGISTRATION_REQUEST :
								$waitResponse = array(
									'subType' => MySensors::I_REGISTRATION_RESPONSE
								);
								break;
							case MySensors::I_PRESENTATION :
								// todo
								// multiple response
								break;
							case MySensors::I_DEBUG :
							case MySensors::I_VERSION :
								$waitResponse = array(
									'subType' => $message->subType
								);
								break;
						}
						
						break;
					
				}
				
				if(!is_array($waitResponse)){
					// no answer for this request
					$waitResponse = array();
				}
				
			}
			
			if(!is_array($waitResponse)){
				// no answer for this request
				$waitResponse = array();
			}
			
			$callback = function($error, $messageSent) use($userCallback, $waitResponse, $self) {
				if($error){
					// an error occurs, the message could not have been sent
					if(is_callable($userCallback)) call_user_func($userCallback, $error, $messageSent, null);
				} else {
					// wait for a response
					$self->responseListeners[] = array_merge(array(
						'callback' => function($error, $messageReceived) use($userCallback, $messageSent) {
							if(is_callable($userCallback)) call_user_func($userCallback, $error, $messageSent, $messageReceived);
						},
						'ts' => microtime(true),
						'nodeId' => $messageSent->nodeId,
						'childSensorId' => $messageSent->childSensorId,
						'messageType' => $messageSent->messageType,
						'subType' => $messageSent->subType
					), $waitResponse);
				}
			};
		}
		
		$this->logger->debug("MySensors: message send nodeId={$message->nodeId} sensorId={$message->childSensorId} messageType={$message->messageType} smartSleep=".($smartSleep?'1':'0'));
		
		$ts = microtime(true);
		
		$message->ts = $ts;
		
		if(!$this->isOpened){
			if(is_callable($callback)){
				call_user_func($callback, 'not connected', $message);
			}
			return 0;
		}
		
		if($smartSleep){
			// buffer this message
			// wait for a heartbeat message to send it !
			
			$this->pendingMessages[] = array(
				'message' => $message,
				'callback' => $callback,
				'ts' => $ts
			);
			
			return 0;
		} else {
			
			if($message->ack === MySensors::REQUEST_ACK){
				// ack requested 
				$this->ackWaitingMessages[] = array(
					'message' => $message,
					'callback' => $callback,
					'ts' => $ts
				);
			}
			
			$wb =  $this->write($message->stringify());
			
			if($message->ack !== MySensors::REQUEST_ACK && is_callable($callback)){
				call_user_func($callback, false, $message);
			}
			
			return $wb;
		}
		
	}
	
	public function updateFirmware($node, $firmware, $callback = null){
		
		$controller = $this;
		
		// tells the node, there is a new firmware
		$type = rand(1,32767);
		$version=256; // === 1.0 or 0100 in hex
		$nbBlocks = ceil(strlen($firmware)/static::FIRMWARE_BLOCK_SIZE);
		$crc = CRC16::calculate($firmware);
		
		$this->pendingFirmware[$node->nodeId()] = array(
			'callback' => $callback,
			'firmware' => $firmware,
			'deviceId' => $node->id(),
			'ts' => microtime(true),
			'lastBlockSent' => -1,
			'blockSent' => 0,
			'type' => $type,
			'version' => $version,
			'nbBlocks' => $nbBlocks,
			'crc' => $crc
		);
		
		$message = new Message($node->nodeId(), MySensors::INTERNAL_CHILD, MySensors::STREAM, MySensors::NO_ACK, MySensors::ST_FIRMWARE_CONFIG_RESPONSE, pack('nnnn',$type, $version, $nbBlocks, $crc));
		$this->send($message, function($error) use($controller, $node, $callback) {
			
			if($error){
				// free memory
				unset($controller->pendingFirmware[$node->nodeId()]);
				
				if(is_callable($callback))
					call_user_func($callback, $error);
				return;
			}
			
		});
		
	}
	
	protected $stream = null;
	
	public function getStream(){
		return $this->stream;
	}
	
	public function process(){
		$this->read();
	}
	
	
};


