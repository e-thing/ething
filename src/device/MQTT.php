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
	
	public static $defaultAttr = array(
		'host' => null,
		'port' => 1883,
		'topic' => null,
		'auth' => null
	);
	
	
	public static function validate($key, &$value, &$context) {
		$ret = false;
		switch($key){
			case 'host':
				if(is_string($value) && !empty($value)){
					$ret = true;
					$context['callbacks']['restart'] = function($r) {
						$r->restart();
					};
				}
				break;
			case 'port':
				if(is_int($value) && $value>=0 && $value<= 65535){
					$ret = true;
					$context['callbacks']['restart'] = function($r) {
						$r->restart();
					};
				}
				break;
			case 'topic': // optional
				if(is_string($value) && !empty($value)){
					
					if( strpos($value, '#') !== false || strpos($value, '+') ){
						throw new Exception('no wildcards allowed');
					}
					
					$context['callbacks']['restart'] = function($r) {
						$r->restart();
					};
					
					$ret = true;
				} else if(is_null($value))
					$ret = true;
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
		
		return $this->ething->deamon('device.mqtt.send '.$this->id().' "'.\addslashes($topic).'" '.\base64_encode($payload)."\n", $stream, $options);
	}
	
	public function processMessage($topic, $message) {
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
		
		
		// file or fallback
		
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
	}
	
	
	// create a new resource
	public static function create(Ething $ething, array $attributes, Resource $createdBy = null) {
		return parent::createDevice($ething, array_merge(self::$defaultAttr, $attributes), array(), $createdBy);
	}
	
	
	public function instanciateMqttClient(){
		return new \Ething\MQTT\Client($this);
	}
	
	
	public function remove() {
		$this->ething->deamon('device.mqtt.end '.$this->id()."\n");
		
		// remove the resource
		parent::remove();
		
	}
	
	public function restart(){
		$this->ething->deamon('device.mqtt.start '.$this->id()."\n");
	}
	
}



