<?php


	/**
	 * @swagger-definition
	 * "Device\\RFLinkGateway":{ 
	 *   "type": "object",
	 *   "description": "RFLinkGateway Device resource representation",
	 * 	 "allOf": [
	 * 		{
	 * 		   "$ref":"#/definitions/Device"
	 * 		},
	 * 		{  
	 * 		   "type": "object",
	 * 		   "properties":{
	 *             "inclusion": {
	 * 		          "type":"boolean",
	 * 		          "description":"Enable the inclusion mode (ie: create automatically new devices on packet receiving)"
	 * 		       },
	 *             "version": {
	 * 		          "type":"string",
	 * 		          "description":"The version of the RFLink library used.",
	 * 		          "readOnly": true
	 * 		       },
	 *             "revision": {
	 * 		          "type":"string",
	 * 		          "description":"The revision number of the RFLink library used.",
	 * 		          "readOnly": true
	 * 		       },
	 *             "build": {
	 * 		          "type":"string",
	 * 		          "description":"The build number of the RFLink library used.",
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
use \Ething\RFLink\RFLink;
use \Ething\Helpers;
use \Ething\Stream;



abstract class RFLinkGateway extends Device
{
	
	public static $defaultAttr = array(
		'inclusion' => true,
		'version' => null,
		'revision' => null,
		'build' => null
	);
	
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
	
	public function getNode($filter){
		return $this->ething->findOne(array(
			'$and' => array(
				array(
					'type' => new \MongoDB\BSON\Regex("^Device"),
					'createdBy.id' => $this->id()
				), $filter
			)
		));
	}
	
	public function addNode($class, $attr){
		$fullClassname = 'Ething\\Device\\RFLink'.$class;
		if(\class_exists($fullClassname)){
			return $fullClassname::create($this->ething, $attr, $this);
		}
		return false;
	}
	
	public function removeAllNodes(){
		// remove all the nodes attached to it !
		foreach($this->getNodes() as $node){
			$node->remove();
		}
	}
	
	public static function validate($key, &$value, &$context) {
		$ret = false;
		switch($key){
			
			case 'inclusion':
				$ret = is_bool($value);
				break;
			
			case 'version':
			case 'revision':
			case 'build':
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
	
	public function operations(){
		return array(
			new Operation($this, 'sendMessage', Helpers::array_to_object_recursive(array(
					'type' => 'object',
					'additionalProperties' => false,
					'required' => array('payload'),
					'properties' => array(
						'payload' => array(
							'type' => 'string',
							'minLength' => 1
						)
					)
				)), 'text/plain', 'send a message', function($op, $stream, $data, $options){
					$data = array_merge(array('payload'=>''), $data);
					return $op->device()->sendMessage($data['payload'], $stream, $options);
				}),
			new Operation($this, 'reboot', null, null, 'reboot the gateway', function($op, $stream, $data, $options){
					return $op->device()->sendMessage("10;REBOOT;", $stream, $options);
				}),
			new Operation($this, 'getVersion', null, null, 'get the version of the gateway', function($op, $stream, $data, $options){
					return $op->device()->sendMessageWaitResponse("10;VERSION;", $stream, $options);
				})
		);
	}
	
	
	// create a new resource
	protected static function createRFLinkGateway(Ething $ething, array $attributes, array $meta = array(), Resource $createdBy = null) {
		return parent::createDevice($ething, array_merge(self::$defaultAttr, $attributes), $meta, $createdBy);
	}
	
	public function remove($removeChildren = false) {
		
		// remove all the nodes attached to it !
		$this->removeAllNodes();
		
		// remove the resource
		parent::remove($removeChildren);
		
	}
	
	public function sendMessage($message, $stream = null, $options = array()){
		return $this->ething->daemon('device.rflink.send '.$this->id().' '.\base64_encode($message)."\n", $stream, $options);
	}
	
	// send a message and wait for the response.
	// note: not all request has a response !
	public function sendMessageWaitResponse($message, $stream = null, $options = array()){
		return $this->ething->daemon('device.rflink.sendWaitResponse '.$this->id().' '.\base64_encode($message)."\n", $stream, $options);
	}
	
	abstract public function instanciateController();
	
	// log a message in a table, usefull for debugging
	public function log($message){
		
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
				'message' => $message
			));
		}
	}
	
	
}



