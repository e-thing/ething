<?php
	

	/**
	 * @swagger-definition
	 * "Device\\MQTT":{ 
	 *   "type": "object",
	 *   "description": "MQTT Device resource representation",
	 * 	 "allOf": [
	 * 		{
	 * 		   "$ref":"#/definitions/Device"
	 * 		},
	 * 		{  
	 * 		   "type": "object",
	 * 		   "properties":{
	 *             "host": {
	 * 		          "type":"string",
	 * 		          "description":"The host of the MQTT broker to connect to."
	 * 		       },
	 *             "port": {
	 * 		          "type":"number",
	 * 		          "description":"The port number of the MQTT broker to connect to."
	 * 		       },
	 *             "topic": {
	 * 		          "type":"string",
	 * 		          "description":"The topic to subscribe to."
	 * 		       },
	 *             "auth": {
	 *                "type":"object",
	 * 	              "properties":{  
	 * 	              	"user":{  
	 * 	              	   "type":"string",
	 * 	              	   "description":"the username to use for the authentication."
	 * 	              	},
	 * 	              	"password":{  
	 * 	              	   "type":"string",
	 * 	              	   "description":"the password to use for the authentication."
	 * 	              	}
	 *                },
	 * 		          "description":"An object describing the credentials to use."
	 * 		       },
	 *             "connected": {
	 * 		          "type":"boolean",
	 * 		          "description":"Set to true when a connection to that device is opened.",
	 * 		          "readOnly": true
	 * 		       }
	 * 		   }
	 * 		}
	 *   ]
	 * }
	 */

namespace Ething\Device;

use \Ething\Exception;
use \Ething\Ething;
use \Ething\Resource;
use \Ething\Table; // sanitizeData
use \Ething\File; // isPrintable
use \Ething\Helpers;
//use \Ething\MQTT\phpMQTT;

class MQTT extends Device
{	
	
	public static $payloadContentTypes = array('application/json','text/plain','application/xml');
	
	public static $defaultAttr = array(
		'host' => null,
		'port' => 1883,
		'auth' => null
	);
	
	protected $subs = null;
	
	public static function validate($key, &$value, &$context) {
		$ret = false;
		switch($key){
			case 'host':
				if(is_string($value) && !empty($value)){
					$ret = true;
				}
				break;
			case 'port':
				if(is_int($value) && $value>=0 && $value<= 65535){
					$ret = true;
				}
				break;
			case 'auth':
				if(is_object($value))
					$value = (array)$value;
				if(is_array($value) && !empty($value['user']) && !empty($value['password']) && is_string($value['user']) && is_string($value['password'])){
					$ret = true;
					
					$authUser = $value['user'];
					$authPwd = $value['password'];
					
					$value = array(
						'user' => $authUser,
						'password' => $authPwd
					);
				}
				else if(is_null($value))
					$ret = true;
				break;
			case 'subscription':
				
				if(is_array($value) && empty($value)) $value = null;
				
				if(is_array($value)){
					
					foreach($value as $k => &$v){
						if(is_object($v)) $v = (array)$v;
						
						foreach($v as $k => $vv){
							
							switch($k){
								case 'topic':
									if(!is_string($vv) || empty($vv))
										throw new Exception('topic: must be a non empty string');
									break;
								case 'contentType':
									if(!is_null($vv)){
										if(!is_string($vv) || empty($vv))
											throw new Exception('contentType: must be a non empty string');
										if(!in_array($vv,  self::$payloadContentTypes))
											throw new Exception('contentType: only the following types are allowed: '.implode(',', self::$payloadContentTypes));
									}
									break;
								case 'jsonPath':
									if(!is_string($vv) && !is_null($vv))
										throw new Exception('jsonPath: must be a string');
									break;
								case 'regexp':
									
									if(!is_string($vv) && !is_null($vv))
										throw new Exception('regexp: must be a string');
									break;
								case 'xpath':
									if(!is_string($vv) && !is_null($vv))
										throw new Exception('xpath: must be a string');
									break;
								default:
									throw new Exception('unknown key \''.$k.'\'');
									break;
							}
							
						}
						
					}
					
					$ret = true;
				} else if(is_null($value))
					$ret = true;
				
				if($ret) {
					$subs = $value;
					$context['callbacks'][] = function($r) use ($subs) {
						
						$r->subs = null;
						
						$r->ething->fs->removeFile($r->getAttr('_subscription'));
						$r->removeAttr('_subscription');
						
						if(isset($subs)){
							$r->setAttr('_subscription', $r->ething->fs->storeFile('Device/'.$r->id().'/specification', json_encode($subs), array(
								'parent' => $r->id()
							)));
						}
						
					};
				}
				unset($context['config'][$key]);// remove this key
				
				break;
			default:
				$ret = parent::validate($key,$value,$context);
				break;
			
		}
		return $ret;
	}
	
	
	public function operations(){
		return array(
			new Operation($this, 'publish', Helpers::array_to_object_recursive(array(
					'type' => 'object',
					'additionalProperties' => false,
					'required' => array('topic', 'payload'),
					'properties' => array(
						'topic' => array(
							'type' => 'string',
							"minLength" => 1,
							"default" => isset($this->topic) ? $this->topic : ''
						),
						'payload' => array(
							'type' => 'string',
							'format' => 'text'
						)
					)
				)), null, 'publish a message', function($op, $stream, $data, $options){
					$data = array_merge(array(
						'payload' => '',
						'topic' => ''
					), $data);
					return $op->device()->publish($data['topic'], $data['payload'], $stream, $options);
				})
		);
	}
	
	
	
	public function publish($topic, $payload, $stream = null, $options = array()){
		
		/*$mqtt = new phpMQTT($this->host, $this->port, (string)$this->id());
		if ($mqtt->connect()) {
			$mqtt->publish($topic,$payload,0);
			$mqtt->close();
			return true;
		}*/
		
		return $this->ething->daemon('device.mqtt.send '.$this->id().' "'.\addslashes($topic).'" '.\base64_encode($payload)."\n", $stream, $options);
	}
	
	/*public function processMessage($topic, $message) {
		$this->updateSeenDate();
		
		$isFileWithExt = preg_match('/[^\/]*\.([^.]+)$/', $topic); // file, e.g. data.json
		$storageName = basename($topic);
		
		if(!$isFileWithExt){
			// try to put the data into a table, first !
			$data = \json_decode($message, true);
			
			if(\json_last_error() !== JSON_ERROR_NONE){
				// not a json format, but may be a small printable string
				if(strlen($message)<=256 && File::isPrintable($message)){
					$data = $message;
				}
			}
			
			if(isset($data)){
				
				if(!is_array($data)){
					$data = array( 'value' => $data );
				}
				
				$dataArray = array($data);
				
				if(Table::sanitizeData($dataArray)){
					// ok, the data are valid
					
					$storage = $this->ething->findOne(array(
						'name' => $storageName,
						'type' => 'Table',
						'createdBy.id' => $this->id()
					));
					
					if(!$storage){
						// create it !
						$storage = $this->ething->create('Table', array(
							'name' => $storageName
						), $this);
					}
					
					if($storage){
						$storage->insert($data);
					}
					
					return true;
				}
				
			}
			
		}
		
		$storage = $this->ething->findOne(array(
			'name' => $storageName,
			'type' => 'File',
			'createdBy.id' => $this->id()
		));
		
		if(!$storage){
			$storage = $this->ething->create('File', array(
				'name' => $storageName
			), $this);
		}
		
		if($storage){
			$storage->write($message);
		}
		
		return true;
	}*/
	
	
	// create a new resource
	public static function create(Ething $ething, array $attributes, Resource $createdBy = null) {
		return parent::createDevice($ething, array_merge(self::$defaultAttr, $attributes), array(
			'connected' => false
		), $createdBy);
	}
	
	public function setConnectState($connected) {
		$change = $this->setAttr('connected', boolval($connected));
		$this->update();
		
		if($change){
			$this->dispatchSignal($connected ? \Ething\Event\DeviceConnected::emit($this) : \Ething\Event\DeviceDisconnected::emit($this));
		}
	}
	
	public function instanciateMqttClient(){
		return new \Ething\MQTT\Client($this);
	}
	
	public function getSubscription() {
		if(isset($this->subs)) return $this->subs; // cached
		$spec = $this->ething->fs->retrieveFile($this->getAttr('_subscription'));
		$this->subs = $spec ? json_decode($spec, true) : array();
		return $this->subs;
	}
	
	public function setSubscription($subs = null) {
		return $this->set('subscription',$subs);
	}
	
	public function processPayload($topic, $payload){
		
		$this->updateSeenDate();
		
		foreach($this->getSubscription() as $item){
			
			if($item['topic'] === $topic){
				
				$data = null;
				$storageType = null;
				$storageName = basename($topic);
				
				switch($item['contentType']){
					
					case 'application/json':
						
						$decoded = \json_decode($payload, true);
						if(\json_last_error() === JSON_ERROR_NONE){
							
							if(!empty($item['jsonPath'])){
								$results = (new \JSONPath($decoded))->find($item['jsonPath']);
								if(count($results))
									$data = $results[0];
							} else {
								$data = $decoded;
							}
							if(isset($data)){
								if(!(is_int($data) || is_float($data) || is_string($data) || is_bool($data))){
									$storageType = 'File';
									$storageName .= '.json';
									$data = \json_encode($data,JSON_PRETTY_PRINT|JSON_UNESCAPED_SLASHES);
								}
							}
						}
						
						break;
					
					case 'text/plain':
						
						if(!empty($item['regexp'])){
							foreach(preg_split("/(\r?\n)/", $payload) as $line){
								if(preg_match($item['regexp'], $line, $matches)){
									$data = count($matches)>1 ? $matches[1] : $matches[0];
									if(!empty($data)){
										if(is_numeric($data))
											$data = $data + 0;
										break;
									}
								}
							}
						} else {
							$data = $payload;
							if(is_numeric($data))
								$data = $data + 0;
						}
						
						break;
					
					case 'application/xml':
						
						if(empty($item['xpath'])){
							$storageType = 'File';
							$storageName .= '.xml';
							$data = $payload;
						} else {
							// xpath
							$xml = \simplexml_load_string($payload);
							if($xml !== false){
								$elements=$xml->xpath($item['xpath']);
								if($elements !== false){
									foreach($elements as $el){
										$data = (string)$el;
										if(!empty($data)){
											if(is_numeric($data))
												$data = $data + 0;
											break;
										}
									}
								}
							}
						}
						
						break;
				}
				
				if(isset($data)){
						
					if(!isset($storageType)){
						if(is_string($data) && strlen($data)>256){
							$storageType = 'File';
						} else {
							$storageType = 'Table';
						}
					}
					
					$storage = $this->ething->findOne(array(
						'name' => $storageName,
						'type' => $storageType,
						'createdBy.id' => $this->id()
					));
					
					if(!$storage){
						// create it !
						$storage = $this->ething->create($storageType, array(
							'name' => $storageName
						), $this);
					}
					
					if($storage){
						switch($storageType){
							case 'Table':
								$storage->insert(array(
									'value' => $data
								));
								break;
							case 'File':
								$storage->write($data);
								break;
						}
					}
					
					$this->dispatchSignal(\Ething\Event\DeviceDataSet::emit($this, (object)array(
						'value' => $data
					)));
					
				}
				
			}
			
		}
		
	}
	
}



