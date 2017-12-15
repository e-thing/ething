<?php

	/**
	 * @swagger-definition
	 * "Device\\ZigateGateway":{ 
	 *   "type": "object",
	 *   "description": "ZigateGateway Device resource representation",
	 * 	 "allOf": [
	 * 		{
	 * 		   "$ref":"#/definitions/Device"
	 * 		},
	 * 		{  
	 * 		   "type": "object",
	 * 		   "properties":{
	 *             "appVersion": {
	 * 		          "type":"string",
	 * 		          "description":"The version of the Zigate firmware.",
	 * 		          "readOnly": true
	 * 		       },
	 *             "sdkVersion": {
	 * 		          "type":"string",
	 * 		          "description":"The version of the Zigate SDK.",
	 * 		          "readOnly": true
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
use \Ething\Helpers;
use \Ething\Stream;
use \Ething\Zigate\Zigate;
use \Ething\Zigate\Message;


abstract class ZigateGateway extends Device
{
	
	public static $defaultAttr = array(
		'appVersion' => null,
		'sdkVersion' => null
	);
	
	public function getDevices(array $filter = null){
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
	
	public function getDevice($addr){
		return $this->ething->findOne(array(
			'type' => new \MongoDB\BSON\Regex("^Device"),
			'createdBy.id' => $this->id(),
			'address' => $addr
		));
	}
	
	public static function validate($key, &$value, &$context) {
		$ret = false;
		switch($key){
			case 'appVersion':
			case 'sdkVersion':
				$ret = (is_null($value) || is_string($value) || is_int($value));
				break;
			default:
				$ret = parent::validate($key,$value,$context);
				break;
			
		}
		return $ret;
	}
	
	
	public function operations(){
		return array(
			new Operation($this, 'getVersion', null, 'application/json', 'request gateway version', function($op, $stream, $data, $options){
				return $op->device()->sendMessage('0010', '', true, $stream, $options);
			}),
			new Operation($this, 'sendMessage', Helpers::array_to_object_recursive(array(
				'type' => 'object',
				'additionalProperties' => false,
				'required' => array('type', 'hasResponse'),
				'properties' => array(
					'type' => array(
						'type' => 'string',
						'minLength' => 1,
						'maxLength' => 4
					),
					'payload' => array(
						'type' => 'string'
					),
					'hasResponse' => array(
						'type' => 'boolean'
					)
				)
			)), 'application/json', 'send a message', function($op, $stream, $data, $options){
				$data = array_merge(array('type' => '', 'payload'=>'', 'hasResponse' => false), $data);
				return $op->device()->sendMessage($data['type'], $data['payload'], boolval($data['hasResponse']), $stream, $options);
			}),
			new Operation($this, 'startInclusion', null, 'application/json', 'start inclusion for 30 secondes', function($op, $stream, $data, $options){
				return $op->device()->sendMessage('0049', 'FFFC1E', false, $stream, $options);
			})
		);
	}
	
	
	
	
	
	
	// create a new resource
	protected static function createZigateGateway(Ething $ething, array $attributes, array $meta = array(), Resource $createdBy = null) {
		return parent::createDevice($ething, array_merge(self::$defaultAttr, $attributes), array_merge( array(
			'version' => null,
			'connected' => false
		), $meta), $createdBy);
	}
	
	public function setConnectState($connected) {
		$change = $this->setAttr('connected', boolval($connected));
		$this->update();
		
		if($change){
			$this->dispatchSignal($connected ? \Ething\Event\DeviceConnected::emit($this) : \Ething\Event\DeviceDisconnected::emit($this));
		}
	}
	
	public function sendMessage($type, $payload = '', $waitResponse = false, $stream = null, $options = array()){
		if($waitResponse === false)
			$cmd = 'device.zigate.send '.$this->id().' '.$type.' "'.$payload.'"';
		else {
			$cmd = 'device.zigate.sendWaitResponse '.$this->id().' '.$type.' "'.$payload.'" "';
			if(is_string($waitResponse)) $cmd .= $waitResponse;
			$cmd .= '"';
		}
		return $this->ething->daemon($cmd, $stream, $options);
	}
	
	
}



