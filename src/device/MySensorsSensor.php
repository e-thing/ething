<?php

	/**
	 * @swagger-definition
	 * "Device\\MySensorsSensor":{ 
	 *   "type": "object",
	 *   "description": "MySensorsSensor Device resource representation. This device is normally automatically created by a MySensorsNode instance.",
	 * 	 "allOf": [
	 * 		{
	 * 		   "$ref":"#/definitions/Device"
	 * 		},
	 * 		{  
	 * 		   "type": "object",
	 * 		   "properties":{
	 *             "sensorId": {
	 * 		          "type":"number",
	 * 		          "description":"The id of the sensor."
	 * 		       },
	 *             "sensorType": {
	 * 		          "type":"string",
	 * 		          "description":"The type of the sensor."
	 * 		       }
	 * 		   }
	 * 		}
	 *   ]
	 * }
	 */
	 
	 
namespace Ething\Device;

use \Ething\Exception;
use \Ething\MySensors\MySensors;
use \Ething\MySensors\Message;
use \Ething\Stream;
use \Ething\Resource;
use \Ething\Ething;
use \Ething\Helpers;


class MySensorsSensor extends Device
{
	
	public static $defaultAttr = array(
		'sensorId' => null,
		'sensorType' => null
	);
	
	public function node(){
		return $this->createdBy();
	}
	
	public function nodeId(){
		return $this->node()->nodeId();
	}
	
	public function gateway(){
		return $this->node()->gateway();
	}
	
	public function sensorId(){
		return $this->sensorId;
	}
	
	public function sensorType(){
		return $this->sensorType;
	}
	
	public function storeData($datatype, $value){
		if(is_int($datatype)) $datatype = MySensors::valueTypeStr($datatype);
		if(isset($value) && is_string($datatype)){
			
			$this->setData($datatype, $value);
			
			$storageName = $datatype;
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
				$storage->insert(array(
					$datatype => $value
				));
			}
			
			$this->dispatchSignal(\Ething\Event\DeviceDataSet::emit($this, (object)array(
				$datatype => $value
			)));
			
		}
	}
	
	public function storeStream($streamtype, $data){
		if(is_int($streamtype)) $streamtype = MySensors::streamTypeStr($streamtype);
		if(isset($data) && is_string($streamtype)){
			
			switch($streamtype){
				case "ST_SOUND":
					$storageName = 'sound';
					break;
				case "ST_IMAGE":
					$storageName = 'image';
					break;
			}
			
			if(isset($storageName)){
				
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
					$storage->write($data);
				}
			}
			
		}
	}
	
	public function sendValue($datatype, $value, $stream = null){
		if($this->sendMessage(MySensors::SET, MySensors::NO_ACK, $datatype, $value, $stream)){
			$this->storeData($datatype, $value);
			return true;
		}
		return false;
	}
	
	public static function validate($key, &$value, &$context) {
		
		$ret = false;
		switch($key){
			case 'sensorId':
				if(!is_int($value) || $value < 0 || $value > 254)
					throw new Exception("must be an integer between 0 and 254, '{$value}' given");
				// check if there is a sensor with the same id that already exist
				$context['postfns'][] = function($r){
					
					if(count($r->node()->getSensors(array(
						'sensorId' => $r->sensorId(),
						'_id' => array( '$ne' => $r->id() )
					))) > 0)
						throw new Exception('a sensor with the same sensorId already exists');
					
				};
				$ret = true;
				break;
			case 'sensorType':
				$value = MySensors::sensorTypeStr($value);
				if($value === null)
					throw new Exception('must be a valid integer or a string describing a sensor type');
				$ret = true;
				break;
			default:
				$ret = parent::validate($key,$value,$context);
				break;
			
		}
		return $ret;
	}
	
	
	
	
	
	public function operations(){
		
		$ops = array(
			new Operation($this, 'sendMessage', Helpers::array_to_object_recursive(array(
					'type' => 'object',
					'additionalProperties' => false,
					'required' => array('type','ack','subtype','payload'),
					'properties' => array(
						'type' => array(
							'type' => 'integer',
							'minimum' => 0,
							'maximum' => 4
						),
						'ack' => array(
							'type' => 'boolean'
						),
						'subtype' => array(
							'type' => 'integer',
							'minimum' => 0,
							'maximum' => 56
						),
						'payload' => array(
							'type' => 'string',
							'maxLength' => 25
						)
					)
				)), 'text/plain', 'send a message', function($op, $stream, $data, $options){
					return $op->device()->sendMessage($data['type'], $data['ack'], $data['subtype'], $data['payload'], $stream, $options);
				})
		);
		
		$sensorType = $this->sensorType;
		
		if(in_array($sensorType, array('S_TEMP','S_WATER_QUALITY'))){
			$ops[] = new Operation($this, 'getTemperature', null, 'text/plain', 'get the temperature', function($op, $stream, $data, $options){
				$stream->out($this->getData('V_TEMP',null));
				return true;
			});
		}
		
		if(in_array($sensorType, array('S_LIGHT','S_BINARY','S_DIMMER','S_SPRINKLER','S_HVAC','S_HEATER'))){
			$ops[] = new Operation($this, 'on', null, 'text/plain', 'turn on', function($op, $stream, $data, $options){
				return $this->sendValue('V_STATUS', true, $stream);
			});
			$ops[] = new Operation($this, 'off', null, 'text/plain', 'turn off', function($op, $stream, $data, $options){
				return $this->sendValue('V_STATUS', false, $stream);
			});
		}
		if($sensorType==='S_DIMMER'){
			$ops[] = new Operation($this, 'setPercentage', Helpers::array_to_object_recursive(array(
				'type' => 'object',
				'additionalProperties' => false,
				'required' => array('percentage'),
				'properties' => array(
					'percentage' => array(
						'type' => 'integer',
						'minimum' => 0,
						'maximum' => 100
					)
				)
			)), 'text/plain', 'set percentage value', function($op, $stream, $data, $options){
				return $this->sendValue('V_PERCENTAGE', $data['percentage'], $stream);
			});
		}
		if(in_array($sensorType, array('S_HEATER','S_HVAC'))){
			$ops[] = new Operation($this, 'setTemperature', Helpers::array_to_object_recursive(array(
				'type' => 'object',
				'additionalProperties' => false,
				'required' => array('temperature'),
				'properties' => array(
					'temperature' => array(
						'type' => 'number',
						'minimum' => -60,
						'maximum' => 60
					)
				)
			)), 'text/plain', 'set temperature', function($op, $stream, $data, $options){
				return $this->sendValue('V_TEMP', $data['temperature'], $stream);
			});
		}
		if(in_array($sensorType, array('S_DOOR', 'S_MOTION', 'S_SMOKE', 'S_SPRINKLER', 'S_WATER_LEAK', 'S_SOUND', 'S_VIBRATION', 'S_MOISTURE'))){
			$ops[] = new Operation($this, 'setArmState', Helpers::array_to_object_recursive(array(
				'type' => 'object',
				'additionalProperties' => false,
				'required' => array('armed'),
				'properties' => array(
					'armed' => array(
						'type' => 'boolean'
					)
				)
			)), 'text/plain', 'set arm state', function($op, $stream, $data, $options){
				return $this->sendValue('V_ARMED', $data['armed'], $stream);
			});
			$ops[] = new Operation($this, 'isArmed', null, 'text/plain', 'get arm state', function($op, $stream, $data, $options){
				$stream->out($this->getData('V_ARMED',false));
				return true;
			});
			$ops[] = new Operation($this, 'setTripState',  Helpers::array_to_object_recursive(array(
				'type' => 'object',
				'additionalProperties' => false,
				'required' => array('tripped'),
				'properties' => array(
					'tripped' => array(
						'type' => 'boolean'
					)
				)
			)), 'text/plain', 'set trip state', function($op, $stream, $data, $options){
				return $this->sendValue('V_TRIPPED', $data['tripped'], $stream);
			});
			$ops[] = new Operation($this, 'isTripped', null, 'text/plain', 'get trip state', function($op, $stream, $data, $options){
				$stream->out($this->getData('V_TRIPPED',false));
				return true;
			});
		}
		
		
		return $ops;
	}
	
	
	
	
	
	
	// create a new resource
	public static function create(Ething $ething, array $attributes, Resource $createdBy = null) {
		if(!($createdBy instanceof MySensorsNode))
			throw new Exception("This MySensorsSensor must be created by a MySensorsNode");
		return parent::createDevice($ething, array_merge(self::$defaultAttr, $attributes), array(), $createdBy);
	}
	
	public function sendMessage($messageType, $ack, $subType, $payload = '', $stream = null, $options = array()){
		return $this->node()->sendMessage($this->sensorId(), $messageType, $ack, $subType, $payload, $stream, $options);
	}
	
	
}



