<?php

	/**
	 * @swagger-definition
	 * "Device\\MySensorsGateway":{ 
	 *   "type": "object",
	 *   "description": "MySensorsGateway Device resource representation",
	 * 	 "allOf": [
	 * 		{
	 * 		   "$ref":"#/definitions/Device"
	 * 		},
	 * 		{  
	 * 		   "type": "object",
	 * 		   "properties":{
	 *             "isMetric": {
	 * 		          "type":"boolean",
	 * 		          "description":"Set the unit to Metric(default) instead of Imperial."
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
use \Ething\Ething;
use \Ething\Resource;
use \Ething\MySensors\MySensors;
use \Ething\MySensors\Message;
use \Ething\Helpers;
use \Ething\Stream;



abstract class MySensorsGateway extends Device
{
	
	public static $defaultAttr = array(
		'isMetric' => true,
		'libVersion' => null
	);
	
	
	public static function validate($key, &$value, &$context) {
		$ret = false;
		switch($key){
			case 'isMetric':
				if(!is_bool($value))
					throw new Exception('must be a boolean');
				$ret = true;
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
	
	public function isMetric(){
		return $this->isMetric;
	}
	
	public function getNodes(array $filter = null){
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
	
	public function getNode($nodeId){
		return $this->ething->findOne(array(
			'type' => new \MongoDB\BSON\Regex("^Device"),
			'createdBy.id' => $this->id(),
			'nodeId' => $nodeId
		));
	}
	
	public function addNode($attr){
		return MySensorsNode::create($this->ething, $attr, $this);
	}
	
	public function removeAllNodes(){
		// remove all the nodes attached to it !
		foreach($this->getNodes() as $node){
			$node->remove();
		}
	}
	
	
	
	public function operations(){
		return array(
			new Operation($this, 'getVersion', null, 'text/plain', 'request gateway version', function($op, $stream, $data, $options){
					return $op->device()->sendMessageWaitResponse(new Message(MySensors::GATEWAY_ADDRESS, MySensors::INTERNAL_CHILD, MySensors::INTERNAL, MySensors::NO_ACK, MySensors::I_VERSION), $stream, $options);
				}),
			new Operation($this, 'sendHeartBeat', null, 'text/plain', 'send a Heartbeat request', function($op, $stream, $data, $options){
					return $op->device()->sendMessageWaitResponse(new Message(MySensors::GATEWAY_ADDRESS, MySensors::INTERNAL_CHILD, MySensors::INTERNAL, MySensors::NO_ACK, MySensors::I_HEARTBEAT_REQUEST), $stream, $options);
				}),
			new Operation($this, 'sendMessage', Helpers::array_to_object_recursive(array(
					'type' => 'object',
					'additionalProperties' => false,
					'required' => array('nodeId','sensorId','type','ack','subtype','payload'),
					'properties' => array(
						'nodeId' => array(
							'type' => 'integer',
							'minimum' => 0,
							'maximum' => 255,
							'default' => 0
						),
						'sensorId' => array(
							'type' => 'integer',
							'minimum' => 0,
							'maximum' => 255,
							'default' => 0
						),
						'type' => array(
							'type' => 'integer',
							'minimum' => 0,
							'maximum' => 4,
							'default' => 0
						),
						'ack' => array(
							'type' => 'boolean',
							'default' => false
						),
						'subtype' => array(
							'type' => 'integer',
							'minimum' => 0,
							'maximum' => 56,
							'default' => 0
						),
						'payload' => array(
							'type' => 'string',
							'maxLength' => 25
						)
					)
				)), 'text/plain', 'send a message', function($op, $stream, $data, $options){
					return $op->device()->sendMessage(new Message($data['nodeId'], $data['sensorId'], $data['type'], $data['ack'], $data['subtype'], $data['payload']), $stream, $options);
				}),
			new Operation($this, 'reboot', null, 'text/plain', 'Request gateway to reboot', function($op, $stream, $data, $options){
					return $op->device()->sendMessage(new Message(MySensors::GATEWAY_ADDRESS, MySensors::INTERNAL_CHILD, MySensors::INTERNAL, MySensors::NO_ACK, MySensors::I_REBOOT), $stream, $options);
				})
		);
	}
	
	
	
	
	
	
	// create a new resource
	protected static function createMySensorsGateway(Ething $ething, array $attributes, array $meta = array(), Resource $createdBy = null) {
		return parent::createDevice($ething, array_merge(self::$defaultAttr, $attributes), array_merge( array(
			'libVersion' => null
		), $meta), $createdBy);
	}
	
	
	public function restart(){
		$this->ething->daemon('device.mysensors.start '.$this->id()."\n");
	}
	
	public function remove($removeChildren = false) {
		
		$this->ething->daemon('device.mysensors.end '.$this->id()."\n");
		
		// remove all the nodes attached to it !
		$this->removeAllNodes();
		
		// remove the resource
		parent::remove($removeChildren);
		
	}
	
	
	
	public function sendMessage(Message $message, $stream = null, $options = array()){
		return $this->ething->daemon('device.mysensors.send '.$this->id().' '.\base64_encode($message->stringify())."\n", $stream, $options);
	}
	
	// send a message and wait for the response.
	// note: not all request has a response !
	public function sendMessageWaitResponse(Message $message, $stream = null, $options = array()){
		return $this->ething->daemon('device.mysensors.sendWaitResponse '.$this->id().' '.\base64_encode($message->stringify())."\n", $stream, $options);
	}
	
	
	abstract public function instanciateController();
	
	// log a message in a table, usefull for debugging
	public function log(Message $message, $out = false){
		
		if($message->messageType === MySensors::STREAM) return;
		
		$logTable = $this->ething->findOne(array(
			'name' => 'log.db',
			'type' => 'Table',
			'createdBy.id' => $this->id()
		));
		
		if(!$logTable){
			// create it !
			try{
				$logTable = $this->ething->create('Table', array(
					'name' => 'log.db',
					'maxLength' => 500
				), $this);
			} catch(\Exception $e){}
		}
		
		if($logTable){
			$logTable->insert(array(
				'direction' => $out ? 'OUT' : 'IN',
				'message' => $message->toHumanReadable()
			));
		}
	}
	
	
}



