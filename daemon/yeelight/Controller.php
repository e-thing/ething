<?php


namespace Ething\Yeelight;


use \Ething\Yeelight\Yeelight;
use \Ething\Device\YeelightDevice;


class Controller extends \Stream {
	
	const AUTOCONNECT_PERIOD = 60; // seconds	
	const RESPONSE_TIMEOUT = 10; // seconds	
	const CONNECT_TIMEOUT = 2; // seconds	
	
	
	public $device = null;
	
	protected $logger;
	
	private $lastActivity = 0;
	
	private $buffer = "";
	
	private $lastAutoconnectLoop = 0;
	private $preventFailConnectLog = false;
	
	protected $isOpened = false;
	
	// response management
	private $responseListeners = array();
	
	public $options = array();
	
	public function __construct(YeelightDevice $device, array $options = array()){
		
		$this->device = $device;
		$this->options = array_replace_recursive($this->options, $options);
		$this->logger = $this->device->ething->logger();
	}
	
	public function ething(){
		return $this->device->ething;
	}
	
	public function name(){
		return $this->device->name();
	}
	
	public function __get($name){
		return isset($this->options[$name]) ? $this->options[$name] : null;
    }
	
	public function open(){
		
		if($this->isOpened){
			if(!$this->close())
				return false; // unable to close !
		}
		
		$device = $this->device;
		$host = $device->get('host');
		
		$stream = @stream_socket_client("tcp://".$host.':55443', $errno, $errstr, self::CONNECT_TIMEOUT);
		if($stream === false)
			throw new \Exception("Yeelight: unable to connect to the device {$host} : {$errstr}");
		
		// make this stream non blocking !
		stream_set_blocking($stream, false);
		
		$this->stream = $stream;
		$this->lastActivity = time();
		$this->buffer = '';
		
		$this->isOpened = true;
		$this->logger->info("Yeelight: connected to {$host}");
		
		$device->setConnectState(true);
		
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
					
					try {
						// must be json
						$message = json_decode($line, true);
						if(!is_array($message)) throw new \Exception();
						
						$this->logger->debug("Yeelight: message received = {$line}");
						$this->processMessage($message);
						
					} catch (\Exception $e) {
						// skip the line
						$this->logger->warn("Yeelight: unable to handle the message {$line}");
						continue;
					}
					
				}
				
			}
		}
	}
	
	
	public function write($str){
		if($this->isOpened){
			$this->lastActivity = time();
			return @fwrite($this->stream, $str);
		}
		return 0;
	}
	
	public function close(){
		if( $this->isOpened ){
			@fclose($this->stream);
			$this->stream = null;
			$this->isOpened = false;
			$this->lastAutoconnectLoop = 0;
			$this->device->setConnectState(false);
			$this->logger->info("Yeelight: closed");
		}
		return !$this->isOpened;
	}
	
	/*
	exemple of messages : (https://www.yeelight.com/download/Yeelight_Inter-Operation_Spec.pdf)
		// response to the query {"id":1,"method":"get_prop","params":["power", "not_exist", "bright"]}
		{"id":1, "result":["off","","100"]}
		// notifications
		{"method":"props","params":{"power":"on"}}
		{"method":"props","params":{"power":"off"}}
		
	*/
	public function processMessage($message) {
		
		$device = $this->device;
		
		// refresh the device meta data before update it !
		$device->refresh();
		
		$device->updateSeenDate();
		
		$isResponse = isset($message["id"]);
		
		if($isResponse){
			
			$responseId = intval($message["id"]);
			$responseResult = isset($message["result"]) ? $message["result"] : array();
			
			foreach($this->responseListeners as $i => $responseListener){
				
				if($responseListener['id'] === $responseId){
					// remove this item
					array_splice($this->responseListeners, $i, 1);
					
					if(is_callable($responseListener['callback']))
						call_user_func($responseListener['callback'], false, $responseResult);
					
					break;
				}
			}
			
		} else if(isset($message["method"]) && isset($message["params"])) {
			// notification
			
			$method = $message["method"];
			$params = $message["params"];
			
			
			if($method === "props"){
				
				foreach($params as &$value){
					if(is_numeric($value))
						$value = $value + 0;
				}
				
				$device->storeData($params);
				
			} else {
				throw new \Exception();
			}
			
		} else {
			throw new \Exception();
		}
		
	}
	
	
	
	private $lastState_ = false;
	
	public function update(){
		// do some stuff regularly
		$now = microtime(true);
		
		// check for a deconnection
		if(!$this->isOpened && $this->isOpened != $this->lastState_)
			$this->logger->info("Yeelight: disconnected");
		$this->lastState_ = $this->isOpened;
		
		// autoconnect
		if(!$this->isOpened && ($now - $this->lastAutoconnectLoop) > self::AUTOCONNECT_PERIOD ){
			try{
				$this->open();
				$this->logger->info("Yeelight: connected");
				$this->preventFailConnectLog = false;
			} catch(\Exception $e){
				if(!$this->preventFailConnectLog) $this->logger->warn("Yeelight: unable to connect : {$e->getMessage()}");
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
	public function send(array $message, $callback = null, $waitResponse = null) {
		
		$message['id'] = rand(1,9999);
		
		$this->logger->debug("Yeelight: message send id={$message['id']}");
		
		if(!$this->isOpened){
			if(is_callable($callback)){
				call_user_func($callback, 'not connected', $message);
			}
			return 0;
		}
		
		$wb =  $this->write(json_encode($message)."\r\n");
		
		if($waitResponse){
			// wait for a response
			$this->responseListeners[] = array(
				'callback' => function($error, $messageReceived) use($callback, $message) {
					if(is_callable($callback)) call_user_func($callback, $error, $message, $messageReceived);
				},
				'ts' => microtime(true),
				'messageSent' => $message,
				'id' => $message['id']
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


