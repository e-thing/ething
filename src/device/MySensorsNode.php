<?php

	/**
	 * @swagger-definition
	 * "Device\\MySensorsNode":{ 
	 *   "type": "object",
	 *   "description": "MySensorsNode Device resource representation. This device is normally automatically created by a MySensorsGateway instance.",
	 * 	 "allOf": [
	 * 		{
	 * 		   "$ref":"#/definitions/Device"
	 * 		},
	 * 		{  
	 * 		   "type": "object",
	 * 		   "properties":{
	 *             "nodeId": {
	 * 		          "type":"number",
	 * 		          "description":"The id of the node."
	 * 		       },
	 *             "sketchName": {
	 * 		          "type":"string",
	 * 		          "description":"The name of the sketch uploaded.",
	 * 		          "readOnly": true
	 * 		       },
	 *             "sketchVersion": {
	 * 		          "type":"string",
	 * 		          "description":"The version of the sketch uploaded.",
	 * 		          "readOnly": true
	 * 		       },
	 *             "smartSleep": {
	 * 		          "type":"boolean",
	 * 		          "description":"SmartSleep feature enabled for this node."
	 * 		       },
	 *             "libVersion": {
	 * 		          "type":"string",
	 * 		          "description":"The version of the MySensors library used.",
	 * 		          "readOnly": true
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


class MySensorsNode extends Device
{
	
	
	public static $defaultAttr = array(
		'nodeId' => null,
		'sketchName' => '',
		'sketchVersion' => '',
		'smartSleep' => false,
		'firmware' => null,
		'libVersion' => null
	);
	
	public function gateway(){
		return $this->createdBy();
	}
	
	public function nodeId(){
		return $this->nodeId;
	}
	
	public static function validate($key, &$value, &$context) {
		$ret = false;
		switch($key){
			case 'nodeId':
				if(!is_int($value) || $value < 1 || $value > 254)
					throw new Exception('must be an integer between 1 and 254');
				// check if there is a node with the same id that already exist
				$context['postfns'][] = function($r){
					
					if(count($r->gateway()->getNodes(array(
						'nodeId' => $r->nodeId(),
						'_id' => array( '$ne' => $r->id() )
					))) > 0)
						throw new Exception('a node with the same nodeId already exists');
					
				};
				$ret = true;
				break;
			case 'sketchName':
			case 'sketchVersion':
				if(!is_string($value))
					throw new Exception('must be a string');
				$ret = true;
				break;
			case 'smartSleep':
				if(!is_bool($value))
					throw new Exception('must be a boolean');
				$ret = true;
				break;
			case 'firmware': // firmware information
				$ret = is_null($value) || is_object($value) || Helpers::is_assoc($value);
				break;
			case 'battery':
				if($ret = parent::validate($key,$value,$context)){
					$context['callbacks'][] = function($r){
						// update the battery value to the attached sensors too
						foreach($r->getSensors() as $sensor){
							$sensor->set('battery',$r->battery);
						}
					};
				}
				break;
			case 'libVersion':
				if(!is_null($value) && !is_string($value))
					throw new Exception('must be a string');
				$ret = true;
				break;
			default:
				$ret = parent::validate($key,$value,$context);
				break;
			
		}
		return $ret;
	}
	
	
	public function getSensors(array $filter = null){
		$q = array(
			'type' => new \MongoDB\BSON\Regex("^Device"),
			'createdBy.id' => $this->id()
		);
		
		if(!empty($filter))
			$q = array(
				'$and' => array($q, $filter)
			);
		
		return $this->ething->find($q);
	}
	
	public function getSensor($sensorId){
		return $this->ething->findOne(array(
			'type' => new \MongoDB\BSON\Regex("^Device"),
			'createdBy.id' => $this->id(),
			'sensorId' => $sensorId
		));
	}
	
	public function addSensor($attr){
		return MySensorsSensor::create($this->ething, $attr, $this);
	}
	
	public function removeAllSensors(){
		// remove all the nodes attached to it !
		foreach($this->getSensors() as $sensor){
			$sensor->remove();
		}
	}
	
	
	
	public function operations(){
		return array(
			new Operation($this, 'sendMessage', Helpers::array_to_object_recursive(array(
					'type' => 'object',
					'additionalProperties' => false,
					'required' => array('sensorId','type','ack','subtype','payload'),
					'properties' => array(
						'sensorId' => array(
							'type' => 'integer',
							'minimum' => 0,
							'maximum' => 255
						),
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
					return $op->device()->sendMessage($data['sensorId'], $data['type'], $data['ack'], $data['subtype'], $data['payload'], $stream, $options);
				}),
			new Operation($this, 'reboot', null, null, 'Request for node to reboot', function($op, $stream, $data, $options){
					return $op->device()->sendMessage(MySensors::INTERNAL_CHILD, MySensors::INTERNAL, MySensors::NO_ACK, MySensors::I_REBOOT, null, $stream, $options);
				}),
			new Operation($this, 'OTA firmware update', Helpers::array_to_object_recursive(array(
					'type' => 'object',
					'additionalProperties' => false,
					'required' => array('firmware'),
					'properties' => array(
						'firmware' => array(
							'type' => 'string',
							'format' => 'binary',
							'minLength' => 1, // not empty !
							'description' => 'only *.hex files must be uploaded !'
						)
					)
				)), 'application/json', 'OTA (on the air) firmware update', function($op, $stream, $data, $options){
					return $op->device()->updateFirmware(\base64_decode($data['firmware']), $stream, $options);
				})
			
		);
	}
	
	
	
	
	
	
	// create a new resource
	public static function create(Ething $ething, array $attributes, Resource $createdBy = null) {
		if(!($createdBy instanceof MySensorsGateway))
			throw new Exception("This MySensorsNode must be created by a MySensorsGateway");
		return parent::createDevice($ething, array_merge(self::$defaultAttr, $attributes), array(), $createdBy);
	}
	
	public function remove($removeChildren = false) {
		
		// remove all the sensors attached to it !
		$this->removeAllSensors();
		
		// remove the resource
		parent::remove($removeChildren);
		
	}
	
	public function sendMessage($childSensorId, $messageType, $ack, $subType, $payload = '', $stream = null, $options = array()){
		$message = new Message($this->nodeId(), $childSensorId, $messageType, $ack, $subType, $payload);
		return $this->gateway()->sendMessage($message, $stream, $options);
	}
	
	public function updateFirmware($firmware, $stream = null, $options = array()){
		return $this->ething->daemon('device.mysensors.updateFirmware '.$this->id().' '.\base64_encode($firmware)."\n", $stream, $options);
	}
}



