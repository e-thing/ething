<?php


namespace Ething\Zigate;


use \Ething\Device\ZigateGateway;
use \Ething\Zigate\Message;
use \Ething\Zigate\Zigate;
use \Ething\Event;



abstract class Controller extends \Stream {
	
	const AUTOCONNECT_PERIOD = 15; // seconds
	const RESPONSE_TIMEOUT = 10;
	
	
	public $gateway = null;
	
	public $gatewayReady = false;
	public $gatewayLibVersion = false;
	
	// response management
	private $responseListeners = array();
	
	private $lastAutoconnectLoop = 0;
	private $preventFailConnectLog = 0;
	
	private $logMessage = false;
	
	protected $isOpened = false;
	
	public $options = array(
		'onMessage' => null // fired on every message (except ack)
	);
	
	public function __construct(ZigateGateway $gateway, array $options = array()){
		
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
	
	abstract public function write($str);
	
	public function close(){
		$this->isOpened = false;
		$this->gateway->setConnectState(false);
		
		foreach( $this->responseListeners as $i => $responseListener){
			if(is_callable($responseListener['callback'])) call_user_func($responseListener['callback'], 'closed', null);
		}
		$this->responseListeners = array();
		
		\Log::info("Zigate: closed");
		return true;
	}
	
	public function createDevice($addr, $model){
		$device = null;
		
		\Log::info("Zigate: create device addr: {$addr} , model: {$model}");
		// get the device class from the model
		
		$info = Zigate::modelToClassInfo($model);
		
		if(isset($info)){
			
			$fclass = '\\Ething\\Device\\'.$info['class'];
			
			if(class_exists($fclass)){
				
				$attr = $this->fetch($addr, array('model', 'manufacturer'));
				
				try {
					$device = $fclass::create($this->ething(), array_merge( array('name' => $info['name'], 'address' => $addr), $attr ), $this->gateway);
				} catch (\Exception $e) {
					\Log::warn("Zigate: unable to create the device reason: ".$e->getMessage());
				}
			}
			
		}
		
		if(!$device){
			\Log::warn("Zigate: unable to create the device addr: {$addr} , model: {$model}");
		}
		
		return $device;
	}
	
	protected function init(){
		
		\Log::info("Zigate: starting init ...");
		
		// ZiGate - set channel 11
		$this->send(new Message("0021", "00000800"), function($error, $response){
			if(!$error){
				// ZiGate - Set Type COORDINATOR
				$this->send(new Message("0023", "00"), function($error, $response){
					if(!$error){
						// ZiGate - start network
						$this->send(new Message("0024", ""), function($error, $response){
							if(!$error){
								\Log::info("Zigate: init succeed");
							} else {
								\Log::error("Zigate: init failed (start network)");
							}
						}, '8024');
					} else {
						\Log::error("Zigate: init failed (set type)");
					}
				});
			} else {
				\Log::error("Zigate: init failed (set channel)");
			}
		});
	}
	
	private $cache = array();
	
	public function store($addr, array $attr){
		// bind data to a device for later purpose
		// kind of a cache
		
		if(!isset($this->cache[$addr])){
			$this->cache[$addr] = array(
				'ts' => 0,
				'data' => array()
			);
		}
		
		$this->cache[$addr]['ts'] = microtime(true);
		$this->cache[$addr]['data'] = array_merge( $this->cache[$addr]['data'], $attr );
		
	}
	
	public function fetch($addr, array $attr){
		$data = array();
		
		if(isset($this->cache[$addr])){
			foreach($this->cache[$addr]['data'] as $key => $value){
				if(in_array($key, $attr)){
					$data[$key] = $value;
				}
			}
		}
		
		return $data;
	}
	
	public function processMessage(Message $packet) {
		
		\Log::debug("Zigate: packet received ".$packet->toHumanReadable());
		
		$type = $packet->getType();
		
		
		// handle response callback
		if( $type=="8000"){  // status
			
			$status = $packet->status;
			$sqn = $packet->sqn;
			$success = ($status === '00');
			
			foreach( $this->responseListeners as $i => &$responseListener){
				if($responseListener['sqn'] === false){
					
					$responseListener['sqn'] = $sqn;
					$responseListener['status'] = $status;
					
					if(!$responseListener['waitResponse'] || !$success){
						
						$statusStr = '';
						switch($status){
							case '00':
								$statusStr = 'Success';
								break;
							case '01':
								$statusStr = 'Incorrect Parameters';
								break;
							case '02':
								$statusStr = 'Unhandled Command';
								break;
							case '03':
								$statusStr = 'Command Failed';
								break;
							case '04':
								$statusStr = 'Busy';
								break;
							case '05':
								$statusStr = 'Stack Already Started';
								break;
							default:
								$statusStr = "ZigBee Error Code " . $status;
								break;
						}
						
						if(is_callable($responseListener['callback'])) call_user_func($responseListener['callback'], $success ? false : $statusStr, null);
						array_splice($this->responseListeners, $i, 1);
					}
					
					break;
				}
			}

		} else {
			
			$sqn = $packet->sqn;
			$type = $packet->getType();
			
			foreach( $this->responseListeners as $i => $responseListener){
				if($responseListener['sqn'] === $sqn || $responseListener['responseId'] === $type){
					if(is_callable($responseListener['callback'])) call_user_func($responseListener['callback'], false, $packet);
					array_splice($this->responseListeners, $i, 1);
					break;
				}
			}
			
		}
		
		if(isset($packet->srcAddr)){
			
			$addr = $packet->srcAddr;
			$device = $this->gateway->getDevice($addr);
			
			if(!$device){
				\Log::warn("Zigate: receive a message from an unknown device, addr: {$addr}");
			}
		}
		
		
		if( $type=="8010"){  // Version
			
			$this->gateway->set('appVersion', $packet->appVersion);
			$this->gateway->set('sdkVersion', $packet->sdkVersion);

		} else if( $type=="004d"){ // device announce
			
			/*
			6F 2F = Short address ( adresse utilisé dans le réseau)
			00 15 8D 00 01 29 15 C6 = Adresse MAC IEEE
			80 = Mac capability
			*/
			
			$this->store($packet->srcAddr, array(
				'address' => $packet->srcAddr
			));
			
			// send request 0x0043 -> Simple Descriptor request
			// in order to get some information about this device !
			
			
			
			
			
		} else if( $type=="8102"){  // Report Individual Attribute report
			
			$addr = $packet->srcAddr;
			
			if( $packet->clusterId==="0000" ){ // General: basic
				
				if ($packet->attrId==="0005"){ // model identifier
					$model = Massage::hex2str($packet->data);
					
					$this->store($packet->srcAddr, array('model' => $model));
					
					\Log::info("Zigate: ZigateRead - model : {$model}");
					
					if(!$device){
						$device = $this->createDevice($addr, $model);
					}
					
					
				} else if ($packet->attrId==="0004"){ // manufacturer name
					$manufacturer = Massage::hex2str($packet->data);
					
					$this->store($packet->srcAddr, array('manufacturer' => $manufacturer));
					
					\Log::info("Zigate: ZigateRead - manufacturer : {$manufacturer}");
					
				} else if ($packet->attrId==="0007"){ // power source
					$powerSource = hexdec(substr($packet->data, 0, 2));
					$powerSource = $powerSource & 0x7F;
					$powerSourceStr = '';
					switch($powerSource){
						case 0x01:
							$powerSourceStr = 'Mains (single phase)';
							break;
						case 0x02:
							$powerSourceStr = 'Mains (3 phase)';
							break;
						case 0x03:
							$powerSourceStr = 'Battery';
							break;
						case 0x04:
							$powerSourceStr = 'DC source';
							break;
						case 0x05:
							$powerSourceStr = 'Emergency mains constantly powered';
							break;
						case 0x06:
							$powerSourceStr = 'Emergency mains and transfer switch';
							break;
					}
					
					if(!empty($powerSourceStr)) $this->store($packet->srcAddr, array('powerSource' => $powerSourceStr));
					
					\Log::info("Zigate: ZigateRead - powerSource : {$powerSource} ({$powerSourceStr})");
				}
				
			} /*else if( $packet->clusterId==="0006" ){  // General: On/Off xiaomi

				//SetSwitch(MsgSrcAddr,MsgSrcEp,MsgClusterData,16)
				//MajDomoDevice(MsgSrcAddr,MsgSrcEp,"Switch",MsgClusterData)
				
			
			} else if( $packet->clusterId==="0402" ){  // Measurement: Temperature xiaomi
				$value = hexdec(substr($MsgClusterData, -8, 4));
				$value = $value / 100;
				//MajDomoDevice(MsgSrcAddr,MsgSrcEp,"Temperature",round(int(MsgValue,16)/100,1))
				
				\Log::debug("Zigate: ZigateRead - MsgType 8102 - reception temperature : " . $value );
						
			} else if( $packet->clusterId==="0403" ){  // Measurement: Pression atmospherique xiaomi   ////// a corriger/modifier http://zigate.fr/xiaomi-capteur-temperature-humidite-et-pression-atmospherique-clusters/
				if( str(Data[28:32])=="0028"){
					//MsgValue=Data[len(Data)-6:len(Data)-4] ////bug !!!!!!!!!!!!!!!!
					$value = hexdec(substr($MsgClusterData, -6, 2));
					//MajDomoDevice(MsgSrcAddr,MsgSrcEp,"Barometer",round(int(MsgValue,8))
					
					\Log::debug("Zigate: ZigateRead - MsgType 8102 - reception atm : " . $value );
				}	
				if( str(Data[26:32])=="000029"){
					//MsgValue=Data[len(Data)-8:len(Data)-4]
					$value = hexdec(substr($MsgClusterData, -8, 4));
					$value = $value / 100;
					//MajDomoDevice(MsgSrcAddr,MsgSrcEp,"Barometer",round(int(MsgValue,16),1))
					
					\Log::debug("Zigate: ZigateRead - MsgType 8102 - reception atm : " . $value);
				}	
				if( str(Data[26:32])=="100029"){
					//MsgValue=Data[len(Data)-8:len(Data)-4]
					$value = hexdec(substr($MsgClusterData, -8, 4));
					$value = $value / 10;
					//MajDomoDevice(MsgSrcAddr,MsgSrcEp,"Barometer",round(int(MsgValue,16)/10,1))
					
					\Log::debug("Zigate: ZigateRead - MsgType 8102 - reception atm : " . $value);
				}
			} else if( $packet->clusterId==="0405" ){  // Measurement: Humidity xiaomi
				//MsgValue=Data[len(Data)-8:len(Data)-4]
				$value = hexdec(substr($MsgClusterData, -8, 4));
				$value = $value / 100;
				//MajDomoDevice(MsgSrcAddr,MsgSrcEp,"Humidity",round(int(MsgValue,16)/100,1))
				
				\Log::debug("Zigate: ZigateRead - MsgType 8102 - reception hum : " . $value );
		
			} else if( $packet->clusterId==="0406" ){  // (Measurement: Occupancy Sensing) xiaomi
				//MajDomoDevice(MsgSrcAddr,MsgSrcEp,"Switch",MsgClusterData)
				
				\Log::debug("Zigate: ZigateRead - MsgType 8102 - reception Occupancy Sensor : " . $MsgClusterData );

			} else if( $packet->clusterId==="0400" ){  // (Measurement: LUX) xiaomi
				//MajDomoDevice(MsgSrcAddr,MsgSrcEp,"Lux",str(int(MsgClusterData,16) ))
				
				\Log::debug("Zigate: ZigateRead - MsgType 8102 - reception LUX Sensor : " . $MsgClusterData );
				
				
			} else if( $packet->clusterId==="0012" ){  // Magic Cube Xiaomi
				//MajDomoDevice(MsgSrcAddr,MsgSrcEp,"Switch",MsgClusterData)
				
				\Log::debug("Zigate: ZigateRead - MsgType 8102 - reception Xiaomi Magic Cube Value : " . $MsgClusterData );
				
			} else if( $packet->clusterId==="000c" ){  // Magic Cube Xiaomi rotation
				//MajDomoDevice(MsgSrcAddr,MsgSrcEp,"Vert Rot",MsgClusterData)
				
				\Log::debug("Zigate: ZigateRead - MsgType 8102 - reception Xiaomi Magic Cube Value Vert Rot : " . $MsgClusterData );
				
				
			}*/
			
		}
		
		if(isset($packet->srcAddr)){
			
			if($device){
				$device->onMessage($packet);
			}
			
		}
		
	}
	
	
	private $lastState_ = false;
	
	public function update(){
		// do some stuff regularly
		$now = microtime(true);
		
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
		if($this->isOpened != $this->lastState_){
			if(!$this->isOpened){
				\Log::info("Zigate: disconnected");
			} else {
				$this->init();
			}
		}
			
		$this->lastState_ = $this->isOpened;
		
		// autoconnect
		if(!$this->isOpened && ($now - $this->lastAutoconnectLoop) > self::AUTOCONNECT_PERIOD ){
			try{
				$this->open();
				$this->preventFailConnectLog = 0;
			} catch(\Exception $e){
				$this->gateway->setConnectState(false);
				
				if($this->preventFailConnectLog % 20 === 0) \Log::warn("Zigate: unable to connect : {$e->getMessage()}");
				$this->preventFailConnectLog += 1;
			}
		}
		
	}
	
	
	public function send(Message $message, $callback = null, $waitResponse = null){
		
		\Log::info("Zigate: send {$message}");
		
		$this->write($message->build());
		
		if($waitResponse){
			if(is_string($waitResponse)){
				$responseId = str_pad($waitResponse, 4, "0", STR_PAD_LEFT);
			} else {
				$responseId = sprintf("%04X",(hexdec( $message->getType() ) | 0x8000));
			}
		}
		
		$this->responseListeners[] = array(
			'callback' => $callback,
			'ts' => microtime(true),
			'message' => $message,
			'status' => false,
			'sqn' => false,
			'responseId' => isset($responseId) ? $responseId : false,
			'waitResponse' => boolval($waitResponse)
		);
		
	}
	
	
};


