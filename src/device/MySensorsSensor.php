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
		//if(is_int($datatype)) $datatype = MySensors::valueTypeStr($datatype);
		$datatype = MySensors::valueTypeToName($datatype);
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
	
	public function sendValue($datatype, $value = '', $stream = null, $store = false){
		if($this->sendMessage(MySensors::SET, MySensors::NO_ACK, $datatype, $value, $stream)){
			if($store) $this->storeData($datatype, $value); # in some case, the device returns the state to the controller after any change
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
				)), 'application/json', 'send a message', function($op, $stream, $data, $options){
					return $op->device()->sendMessage($data['type'], $data['ack'], $data['subtype'], $data['payload'], $stream, $options);
				})
		);
		
		$sensorType = $this->sensorType;
		
		switch($sensorType){
			
			case 'S_DOOR':
				$ops[] = $this->createGetOp('V_TRIPPED');
				$ops[] = $this->createGetOp('V_ARMED');
				break;
			case 'S_MOTION':
				$ops[] = $this->createGetOp('V_TRIPPED');
				$ops[] = $this->createGetOp('V_ARMED');
				break;
			case 'S_SMOKE':
				$ops[] = $this->createGetOp('V_TRIPPED');
				$ops[] = $this->createGetOp('V_ARMED');
				break;
			case 'S_BINARY':
			case 'S_LIGHT':
				$ops[] = $this->createGetOp('V_STATUS');
				$ops[] = $this->createGetOp('V_WATT');
				break;
			case 'S_DIMMER':
				$ops[] = $this->createGetOp('V_STATUS');
				$ops[] = $this->createGetOp('V_PERCENTAGE');
				$ops[] = $this->createGetOp('V_WATT');
				
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
				)), 'application/json', 'set percentage value', function($op, $stream, $data, $options){
					return $op->device()->sendValue('V_PERCENTAGE', $data['percentage'], $stream, true);
				});
				
				break;
			case 'S_COVER':
				$ops[] = $this->createGetOp('V_PERCENTAGE');
				
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
				)), 'application/json', 'set cover percentage', function($op, $stream, $data, $options){
					return $op->device()->sendValue('V_PERCENTAGE', $data['percentage'], $stream, true);
				});
				
				$ops[] = new Operation($this, 'up', null, 'application/json', 'move cover up', function($op, $stream, $data, $options){
					return $op->device()->sendValue('V_UP', '', $stream);
				});
				
				$ops[] = new Operation($this, 'down', null, 'application/json', 'move cover down', function($op, $stream, $data, $options){
					return $op->device()->sendValue('V_DOWN', '', $stream);
				});
				
				$ops[] = new Operation($this, 'stop', null, 'application/json', 'stop cover', function($op, $stream, $data, $options){
					return $op->device()->sendValue('V_STOP', '', $stream);
				});
				
				break;
			case 'S_TEMP':
				$ops[] = $this->createGetOp('V_TEMP');
				break;
			case 'S_HUM':
				$ops[] = $this->createGetOp('V_HUM');
				break;
			case 'S_BARO':
				$ops[] = $this->createGetOp('V_PRESSURE');
				$ops[] = $this->createGetOp('V_FORECAST');
				break;
			case 'S_WIND':
				$ops[] = $this->createGetOp('V_WIND');
				$ops[] = $this->createGetOp('V_GUST');
				$ops[] = $this->createGetOp('V_DIRECTION');
				break;
			case 'S_RAIN':
				$ops[] = $this->createGetOp('V_RAIN');
				$ops[] = $this->createGetOp('V_RAINRATE');
				break;
			case 'S_UV':
				$ops[] = $this->createGetOp('V_UV');
				break;
			case 'S_WEIGHT':
				$ops[] = $this->createGetOp('V_WEIGHT');
				$ops[] = $this->createGetOp('V_IMPEDANCE');
				break;
			case 'S_POWER':
				$ops[] = $this->createGetOp('V_WATT');
				$ops[] = $this->createGetOp('V_KWH');
				$ops[] = $this->createGetOp('V_VAR');
				$ops[] = $this->createGetOp('V_VA');
				$ops[] = $this->createGetOp('V_POWER_FACTOR');
				break;
			case 'S_HEATER':
				$ops[] = $this->createGetOp('V_HVAC_SETPOINT_HEAT');
				$ops[] = $this->createGetOp('V_HVAC_FLOW_STATE');
				$ops[] = $this->createGetOp('V_TEMP');
				$ops[] = $this->createGetOp('V_STATUS');
				break;
			case 'S_DISTANCE':
				$ops[] = $this->createGetOp('V_DISTANCE');
				$ops[] = $this->createGetOp('V_UNIT_PREFIX');
				break;
			case 'S_LIGHT_LEVEL':
				$ops[] = $this->createGetOp('V_LIGHT_LEVEL');
				$ops[] = $this->createGetOp('V_LEVEL');
				break;
			case 'S_ARDUINO_NODE':
				
				break;
			case 'S_ARDUINO_REPEATER_NODE':
				
				break;
			case 'S_LOCK':
				$ops[] = $this->createGetOp('V_LOCK_STATUS');
				break;
			case 'S_IR':
				$ops[] = $this->createGetOp('V_IR_RECORD');
				break;
			case 'S_WATER':
				$ops[] = $this->createGetOp('V_FLOW');
				$ops[] = $this->createGetOp('V_VOLUME');
				break;
			case 'S_AIR_QUALITY':
				$ops[] = $this->createGetOp('V_LEVEL');
				$ops[] = $this->createGetOp('V_UNIT_PREFIX');
				break;
			case 'S_CUSTOM':
				
				break;
			case 'S_DUST':
				$ops[] = $this->createGetOp('V_LEVEL');
				$ops[] = $this->createGetOp('V_UNIT_PREFIX');
				break;
			case 'S_SCENE_CONTROLLER':
				$ops[] = new Operation($this, 'on', null, 'application/json', 'turn scene on', function($op, $stream, $data, $options){
					return $op->device()->sendValue('V_SCENE_ON', '', $stream);
				});
				$ops[] = new Operation($this, 'off', null, 'application/json', 'turn scene off', function($op, $stream, $data, $options){
					return $op->device()->sendValue('V_SCENE_OFF', '', $stream);
				});
				break;
			case 'S_RGB_LIGHT':
				$ops[] = $this->createGetOp('V_RGB');
				$ops[] = $this->createGetOp('V_WATT');
				break;
			case 'S_RGBW_LIGHT':
				$ops[] = $this->createGetOp('V_RGBW');
				$ops[] = $this->createGetOp('V_WATT');
				break;
			case 'S_COLOR_SENSOR':
				$ops[] = $this->createGetOp('V_RGB');
				break;
			case 'S_HVAC':
				$ops[] = $this->createGetOp('V_STATUS');
				$ops[] = $this->createGetOp('V_TEMP');
				$ops[] = $this->createGetOp('V_HVAC_SETPOINT_HEAT');
				$ops[] = $this->createGetOp('V_HVAC_SETPOINT_COOL');
				$ops[] = $this->createGetOp('V_HVAC_FLOW_STATE');
				$ops[] = $this->createGetOp('V_HVAC_FLOW_MODE');
				$ops[] = $this->createGetOp('V_HVAC_SPEED');
				
				$ops[] = new Operation($this, 'setCoolTemperaturePoint', Helpers::array_to_object_recursive(array(
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
				)), 'application/json', 'set cool temperature point', function($op, $stream, $data, $options){
					return $op->device()->sendValue('V_HVAC_SETPOINT_COOL', $data['temperature'], $stream, true);
				});
			
				$ops[] = new Operation($this, 'setFlowMode', Helpers::array_to_object_recursive(array(
					'type' => 'object',
					'additionalProperties' => false,
					'required' => array('mode'),
					'properties' => array(
						'mode' => array(
							'type' => 'string',
							'enum' => array("Auto", "ContinuousOn", "PeriodicOn")
						)
					)
				)), 'application/json', 'set flow mode', function($op, $stream, $data, $options){
					return $op->device()->sendValue('V_HVAC_FLOW_MODE', $data['mode'], $stream, true);
				});
				
				$ops[] = new Operation($this, 'setFlowSpeed', Helpers::array_to_object_recursive(array(
					'type' => 'object',
					'additionalProperties' => false,
					'required' => array('speed'),
					'properties' => array(
						'speed' => array(
							'type' => 'string',
							'enum' => array("Min", "Normal", "Max", "Auto")
						)
					)
				)), 'application/json', 'set flow speed', function($op, $stream, $data, $options){
					return $op->device()->sendValue('V_HVAC_SPEED', $data['speed'], $stream, true);
				});
				
				break;
			case 'S_MULTIMETER':
				$ops[] = $this->createGetOp('V_VOLTAGE');
				$ops[] = $this->createGetOp('V_CURRENT');
				$ops[] = $this->createGetOp('V_IMPEDANCE');
				break;
			case 'S_SPRINKLER':
				$ops[] = $this->createGetOp('V_STATUS');
				$ops[] = $this->createGetOp('V_TRIPPED');
				break;
			case 'S_WATER_LEAK':
				$ops[] = $this->createGetOp('V_TRIPPED');
				$ops[] = $this->createGetOp('V_ARMED');
				break;
			case 'S_SOUND':
				$ops[] = $this->createGetOp('V_LEVEL');
				$ops[] = $this->createGetOp('V_TRIPPED');
				$ops[] = $this->createGetOp('V_ARMED');
				break;
			case 'S_VIBRATION':
				$ops[] = $this->createGetOp('V_LEVEL');
				$ops[] = $this->createGetOp('V_TRIPPED');
				$ops[] = $this->createGetOp('V_ARMED');
				break;
			case 'S_MOISTURE':
				$ops[] = $this->createGetOp('V_LEVEL');
				$ops[] = $this->createGetOp('V_TRIPPED');
				$ops[] = $this->createGetOp('V_ARMED');
				break;
			case 'S_INFO':
				$ops[] = $this->createGetOp('V_TEXT');
				break;
			case 'S_GAS':
				$ops[] = $this->createGetOp('V_FLOW');
				$ops[] = $this->createGetOp('V_VOLUME');
				break;
			case 'S_GPS':
				$ops[] = $this->createGetOp('V_POSITION');
				break;
			case 'S_WATER_QUALITY':
				$ops[] = $this->createGetOp('V_TEMP');
				$ops[] = $this->createGetOp('V_PH');
				$ops[] = $this->createGetOp('V_ORP');
				$ops[] = $this->createGetOp('V_EC');
				$ops[] = $this->createGetOp('V_STATUS');
				break;
			case 'S_CAM':
				
				break;
			case 'S_UNK':
				
				break;
			
		}
		
		/*
		* common operations
		*/
		
		// V_STATUS setter
		if(in_array($sensorType, array('S_LIGHT','S_BINARY','S_DIMMER','S_SPRINKLER','S_HVAC','S_HEATER'))){
			$ops[] = new Operation($this, 'on', null, 'application/json', 'turn on', function($op, $stream, $data, $options){
				return $op->device()->sendValue('V_STATUS', true, $stream, true);
			});
			$ops[] = new Operation($this, 'off', null, 'application/json', 'turn off', function($op, $stream, $data, $options){
				return $op->device()->sendValue('V_STATUS', false, $stream, true);
			});
		}
		
		// V_TEMP V_HVAC_SETPOINT_HEAT V_HVAC_FLOW_STATE setter
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
			)), 'application/json', 'set temperature', function($op, $stream, $data, $options){
				return $op->device()->sendValue('V_TEMP', $data['temperature'], $stream, true);
			});
			$ops[] = new Operation($this, 'setTemperaturePoint', Helpers::array_to_object_recursive(array(
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
			)), 'application/json', 'set temperature point', function($op, $stream, $data, $options){
				return $op->device()->sendValue('V_HVAC_SETPOINT_HEAT', $data['temperature'], $stream, true);
			});
			
			$ops[] = new Operation($this, 'setFlowState', Helpers::array_to_object_recursive(array(
				'type' => 'object',
				'additionalProperties' => false,
				'required' => array('state'),
				'properties' => array(
					'state' => array(
						'type' => 'string',
						'enum' => array("Off", "HeatOn", "CoolOn", "AutoChangeOver")
					)
				)
			)), 'application/json', 'set flow state', function($op, $stream, $data, $options){
				return $op->device()->sendValue('V_HVAC_FLOW_STATE', $data['state'], $stream, true);
			});
		}
		
		// V_ARMED setter
		if(in_array($sensorType, array('S_DOOR', 'S_MOTION', 'S_SMOKE', 'S_WATER_LEAK', 'S_SOUND', 'S_VIBRATION', 'S_MOISTURE'))){
			$ops[] = new Operation($this, 'setArmState', Helpers::array_to_object_recursive(array(
				'type' => 'object',
				'additionalProperties' => false,
				'required' => array('armed'),
				'properties' => array(
					'armed' => array(
						'type' => 'boolean'
					)
				)
			)), 'application/json', 'set arm state', function($op, $stream, $data, $options){
				return $op->device()->sendValue('V_ARMED', $data['armed'], $stream, true);
			});
		}
		
		
		
		return $ops;
	}
	
	
	public function createGetOp($valueType){
		
		$name = MySensors::valueTypeToName($valueType);
		
		$opName = 'get'.implode('', array_map('ucfirst', explode(' ', $name)));
		
		return new Operation($this, $opName, null, 'application/json', 'get the "{$name}" value', function($op, $stream, $data, $options){
			$stream->sendJSON($op->device()->getData($name,null));
			return true;
		});
		
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



