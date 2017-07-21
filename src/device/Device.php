<?php
	

/**
 * @swagger-definition
 * "Device":{ 
 *   "type": "object",
 *   "description": "Device base class representation",
 * 	 "allOf": [
 * 		{
 * 		   "$ref":"#/definitions/Resource"
 * 		},
 * 		{  
 * 		   "type": "object",
 * 		   "properties":{
 *             "lastSeenDate": {
 * 		          "type":"string",
 * 		          "format":"date-time",
 * 		          "readOnly": true,
 * 		          "description":"Last time this device was reached or made a request (formatted RFC 3339 timestamp)."
 * 		       },
 *             "battery": {
 * 		          "type":"number",
 * 		          "description":"The battery level of this device (must be between 0 (empty) and 100 (full) , or null if the device has no battery information)."
 * 		       },
 *             "location": {
 *                "type":"object",
 * 	              "properties":{  
 * 	              	"latitude":{  
 * 	              	   "type":"number",
 * 	              	   "description":"the latitude"
 * 	              	},
 * 	              	"longitude":{  
 * 	              	   "type":"number",
 * 	              	   "description":"the longitude"
 * 	              	},
 * 	              	"altitude":{  
 * 	              	   "type":"number",
 * 	              	   "description":"the altitude"
 * 	              	},
 * 	              	"place":{  
 * 	              	   "type":"string",
 * 	              	   "description":"the name of the place. For instance 'home'."
 * 	              	},
 * 	              	"floor":{
 * 	              	   "type":"number",
 * 	              	   "description":"the floor number"
 * 	              	},
 * 	              	"room":{
 * 	              	   "type":"string",
 * 	              	   "description":"the name of the room"
 * 	              	}
 *                },
 * 		          "description":"The location of this device."
 * 		       },
 *             "operations": {
 * 		          "type":"array",
 * 		          "items":{
 * 		              "type":"string"
 * 		          },
 * 		          "description":"The list of the operations available.",
 * 		          "readOnly": true
 * 		       }
 * 		   }
 * 		}
 *   ]
 * }
 */

namespace Ething\Device;

use \Ething\Resource;
use \Ething\Event;
use \Ething\Exception;
use \Ething\Ething;
use \Ething\Stream;

abstract class Device extends Resource
{
	
	const BATTERY_NONE = null;
	const BATTERY_EMPTY = 0;
	const BATTERY_LOW   = 10;
	const BATTERY_HALF  = 50;
	const BATTERY_FULL  = 100;
	
	
	const VALIDATE_NAME = '/^[a-zA-Z0-9\-.\'_ ]{1,99}$/';
	
	
	public static $defaultAttr = array(
		'battery'   => null, // 0-100 : the battery level, if null it means that no battery information is provided
		'location' => null
	);
	
	
	public function updateSeenDate() {
		$this->setAttr('lastSeenDate', new \MongoDB\BSON\UTCDateTime());
		$this->update();
	}
	
	
	
	public static function validate($key, &$value, &$context) {
		$ret = false;
		switch($key){
			case 'battery':
				if(is_int($value) || is_float($value)){
					if($value<0) $value=0;
					else if($value>100) $value=100;
					
					$currentValue = isset($context['resource']) ? $context['resource']->battery : null;
					if(
						$value < self::BATTERY_LOW &&
						($currentValue===null || $currentValue >= self::BATTERY_LOW)
					)
						$context['callbacks'][] = function($r){
							$r->dispatchSignal(Event\LowBatteryDevice::emit($r));
						};
					
					$ret = true;
				}
				else
					$ret = is_null($value);
				break;
			/*case 'name': // overwride default, no duplicate
				if($ret = parent::validate($key,$value,$context)){
					
					// check if a device already have this name
					$context['postfns'][] = function($r) {
						// check if there is no other gateway with the same port
						if(count($r->ething->find(array(
							'type' => array('$regex' => new \MongoDB\BSON\Regex("^Device")),
							'name' => $r->get('name'),
							'_id' => array( '$ne' => $r->id() )
						)))>0)
							throw new Exception('a device already has this name');
					};
				}
				break;*/
			case 'location':
				if(is_object($value))
					$value = (array)$value;
				if(is_array($value) && count($value)===0)
					$value = null;
				if(is_array($value)){
					foreach($value as $key => $v){
						switch($key){
							case 'longitude':
							case 'latitude':
							case 'altitude':
								if(!(is_int($v) || is_float($v)))
									throw new Exception("invalid 'location.{$key}' field, must be a number");
								break;
							case 'place':
							case 'room':
								if(!is_string($v))
									throw new Exception("invalid 'location.{$key}' field, must be a string");
								break;
							case 'floor':
								if(!is_int($v))
									throw new Exception("invalid 'location.{$key}' field, must be an integer");
								break;
							default:
								throw new Exception("invalid 'location.{$key}' field");
						}
					}
					$ret = true;
				}
				else if(is_null($value)){
					$ret = true;
				}
				break;
			default:
				$ret = parent::validate($key,$value,$context);
				break;
		}
		return $ret;
	}
	
	// return true if the call was successsfull, false if an error occurs.
	// the output data is stored in the Stream instance (since it can be a stream, e.g. MJPEG).
	public function call( $operation, Stream $stream = null, array $data = null, array $options = array()){
		$operation = is_string($operation) ? $this->operation($operation) : $operation;
		if(!$operation)
			throw new Exception("this operation is not accessible");
		if(!isset($data)) $data = array();
		return $operation->call($stream, $data, $options);
	}
	
	
	public function operation($operationId){
		foreach($this->operations() as $op){
			if($op->name() === $operationId)
				return $op;
		}
	}
	
	public function repair() {
		$this->resetOperations();
	}
	
	// return an associative array containing all the available operations for this device
	abstract public function operations();
	
	protected function resetOperations(){
		$operations = array();
		foreach( $this->operations() as $operation ){
			$operations[] = $operation->name();
		}
		$this->setAttr('operations', $operations);
		$this->update();
	}
	
	// create a new device
	protected static function createDevice(Ething $ething, array $attributes, array $meta = array(), Resource $createdBy = null) {
		$device = parent::createRessource($ething, array_merge(self::$defaultAttr, $attributes), array_merge( array(
			'lastSeenDate' => null,
			'operations' => array()
		), $meta), $createdBy);
		if($device){
			$device->resetOperations();
		}
		return $device;
	}
	
}



