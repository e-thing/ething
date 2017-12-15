<?php


namespace Ething\Mihome;

use \Ething\Ething;
use \Ething\Mihome\Mihome;
use \Ething\Device\MihomeGateway;


class Controller extends \Stream {
	
	const AUTOCONNECT_PERIOD = 60; // seconds
	const RESPONSE_TIMEOUT = 10;
	const ACTIVITY_TIMEOUT = 120;
	
	public $ething = null;
	
	public $options = array();
	
	private $lastActivity = 0;
	
	private $buffer = "";
	
	// response management
	private $responseListeners = array();
	
	// activity management
	private $activities = array();
	
	private $lastAutoconnectLoop = 0;
	private $preventFailConnectLog = 0;
	
	protected $isOpened = false;
	
	private $socket = null;
	
	public function __construct(Ething $ething, array $options = array()){
		
		$this->ething = $ething;
		$this->options = array_replace_recursive($this->options, $options);
		
	}
	
	public function open(){
		$this->lastAutoconnectLoop = microtime(true);
		
		if($this->isOpened){
			if(!$this->close())
				return false; // unable to close !
		}
		
		// cf: https://github.com/clue/php-multicast-react/blob/master/src/Factory.php
		
		$stream = @stream_socket_server('udp://0.0.0.0:'.Mihome::MULTICAST_PORT, $errno, $errstr, STREAM_SERVER_BIND);
		if ($stream === false) {
            throw new \Exception('Unable to create receiving socket: ' . $errstr, $errno);
        }
		
		$socket = socket_import_stream($stream);
        if ($socket === false) {
            throw new \Exception('Unable to access underlying socket resource');
        }
		
		// allow multiple processes to bind to the same address
        $ret = socket_set_option($socket, SOL_SOCKET, SO_REUSEADDR, 1);
        if ($ret === false) {
            throw new \Exception('Unable to enable SO_REUSEADDR');
        }
		
		// join multicast group and bind to port
        $ret = socket_set_option(
            $socket,
            IPPROTO_IP,
            MCAST_JOIN_GROUP,
            array('group' => Mihome::MULTICAST_ADDRESS, 'interface' => 0)
        );
        if ($ret === false) {
            throw new \Exception('Unable to join multicast group');
        }
		
		$this->socket = $socket;
		$this->registerStream($stream, 0);
		$this->isOpened = true;
		
		\Log::info("Mihome: listening...");
		
		return true;
		
		/*
		if($sock = socket_create(AF_INET, SOCK_DGRAM, SOL_UDP)){
			
			socket_set_option($sock, IPPROTO_IP, IP_MULTICAST_TTL, 32);
			socket_set_option($sock, IPPROTO_IP, IP_MULTICAST_LOOP, 1);
			socket_set_option($sock, IPPROTO_IP, MCAST_JOIN_GROUP, array('group' => '224.0.0.50', 'interface' => 0));
			
			if(socket_bind($sock, "0.0.0.0", 9898)){
				
				socket_set_nonblock($sock);
				
				$this->socket = $sock;
				$this->registerSocket($sock);
				
				$this->isOpened = true;
				
				$this->lastActivity = time();
				$this->buffer = '';
				
				\Log::info("Mihome: listening to 224.0.0.50:9898");
				
				return true;
				
			} else {
				throw new \Exception("cannot bind to port 9898");
			}
			
			
		} else {
			throw new \Exception(socket_strerror(socket_last_error()));
		}
		
		return false;*/
	}
	
	static private function extract(array $arr, array $keys){
		$ret = array();
		foreach($keys as $k){
			$ret[$k] = array_key_exists($k, $arr) ? $arr[$k] : null;
		}
		return $ret;
	}
	
	public function process($stream, $id){
		if($this->isOpened){
			
			
			$data = stream_socket_recvfrom($stream, Mihome::SOCKET_BUFSIZE, 0, $peerAddress);
			if ($data === false) {
				// receiving data failed => remote side rejected one of our packets
				// due to the nature of UDP, there's no way to tell which one exactly
				// $peer is not filled either
				\Log::error("Mihome: receive error");
				$this->close();
				return;
			}
			
			\Log::info("Mihome: receive data from ".$peerAddress." : ".$data);
			
			$response = json_decode($data, true);
			if(is_array($response)){
				
				$sid = $response['sid'];
				$cmd = $response['cmd'];
				
				$this->activities[$sid] = time();
				
				switch ($cmd){
					
					case 'heartbeat':
					case 'report':
					case 'read_ack':
						
						if($response['model'] === 'gateway'){
							// concerning a gateway
							
							$gatewayDevice = $this->ething->findOne(array(
								'type' => 'Device\\MihomeGateway',
								'sid' => $sid
							));
							
							if(!$gatewayDevice){
								$gatewayDevice = MihomeGateway::create($this->ething, array_merge( array('name' => 'gateway'), static::extract($response, array('sid', 'ip', 'port')) ));
								if(!$gatewayDevice){
									\Log::error("Mihome: unable to create the gateway sid:{$sid}");
								}
							}
							
							if($gatewayDevice){
								$gatewayDevice->processData($response);
							}
							
							
						} else {
							// concerning a device
							
							$device = $this->ething->findOne(array(
								'type' => new \MongoDB\BSON\Regex('^Device\\\\Mihome.*$'),
								'sid' => $sid
							));
							
							if(!$device){
								
								switch($response['model']){
									case 'sensor_ht':
									case 'weather.v1':
										$device = \Ething\Device\MihomeSensorHT::create($this->ething, array_merge( array('name' => 'thermometer'), static::extract($response, array('sid')) ));
										break;
									
								}
								
								if(!$device){
									\Log::error("Mihome: unable to create the device model:{$response['model']} sid:{$sid}");
								}
								
							}
							
							if($device){
								$device->processData($response);
							}
							
							
						}
						
						break;
					case 'write_ack':
						break;
					default:
						\Log::warn("Mihome: received unk command '{$response['cmd']}'");
						break;
				}
				
				if(in_array($cmd, array('read_ack', 'write_ack', 'get_id_list_ack'))){
					
					// response ?
					
					foreach($this->responseListeners as $i => $responseListener){
						if( $responseListener['sid'] === $sid && $responseListener['ack'] === $cmd) {
							// remove this item
							array_splice($this->responseListeners, $i, 1);
							
							if(is_callable($responseListener['callback']))
								call_user_func($responseListener['callback'], false, $responseListener['command'], $response);
						}
					}
					
				}
				
			}
			
			/*
			
			$ret = @socket_recvfrom($this->socket, $chunk, 1024, MSG_DONTWAIT, $from, $port);
			
			if($ret === false){
				// an error occurs
				\Log::error("Mihome: socket_recvfrom: ".socket_strerror(socket_last_error()));
				$this->close();
				return;
			} else if($ret>0){
				
				// create a buffer per client
				// $this->buffer[$from.':'.$port] .= $chunk;
				
				\Log::debug($chunk);
				
			}*/
			
			
		}
	}
	
	
	public function sendData(MihomeGateway $gateway, array $command, $callback = null){
		if(isset($command['cmd']) && isset($command['data']) && $command['cmd'] === 'write' && is_array($command['data'])){
			$command['data']['key'] = $gateway->getGatewayKey();
		}
		return $this->sendCommand($command, $callback, $gateway->ip);
	}
	
	public function sendCommand(array $command, $callback = null, $addr = Mihome::MULTICAST_ADDRESS){
		$commandStr = \json_encode($command);
		
		if($this->isOpened){
			
			\Log::debug("Mihome: send data to ".$addr." : ".$commandStr);
			
			$res = stream_socket_sendto($this->getRegisteredStream(0), $commandStr, 0, $addr.':'.Mihome::MULTICAST_PORT);
			
			if($res===false){
				if(is_callable($callback)){
					call_user_func($callback, 'send error', $command, null);
				}
			} else {
				if(is_callable($callback)){
					
					$cmd = isset($command['cmd']) ? $command['cmd'] : '';
					$sid = isset($command['sid']) ? $command['sid'] : '';
					
					$this->responseListeners[] = array(
						'callback' => $callback,
						'ts' => microtime(true),
						'sid' => $sid,
						'ack' => $cmd.'_ack',
						'command' => $command
					);
					
				}
			}
		} else {
			if(is_callable($callback)){
				call_user_func($callback, 'not connected', $command, null);
			}
		}
		
	}
	
	public function close(){
		if( $this->isOpened ){
			$this->closeAndUnregisterAll();
			$this->isOpened = false;
			\Log::info("Mihome: closed");
		}
		return !$this->isOpened;
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
		
		// activities check
		foreach($this->activities as $ssi => $lastActivity){
			if( ($now - $lastActivity) > self::ACTIVITY_TIMEOUT ){
				
				// remove this item
				unset($this->activities[$ssi]);
				
				$device = $this->ething->findOne(array(
					'type' => new \MongoDB\BSON\Regex('^Device\\\\Mihome.*$'),
					'sid' => $sid
				));
				
				if($device){
					$device->setConnectState(false);
				}
				
			}
		}
		
		// check for a deconnection
		if(!$this->isOpened && $this->isOpened != $this->lastState_)
			\Log::info("Mihome: disconnected");
		$this->lastState_ = $this->isOpened;
		
		// autoconnect
		if(!$this->isOpened && ($now - $this->lastAutoconnectLoop) > self::AUTOCONNECT_PERIOD ){
			try{
				$this->open();
				$this->preventFailConnectLog = 0;
			} catch(\Exception $e){
				if($this->preventFailConnectLog % 5 === 0) \Log::warn("Mihome: unable to connect : {$e->getMessage()}");
				$this->preventFailConnectLog += 1;
			}
		}
		
	}
	
};


