<?php

	/**
	 * @swagger-definition
	 * "Device\\ZigateDevice":{ 
	 *   "type": "object",
	 *   "description": "ZigateDevice Device base class representation",
	 * 	 "allOf": [
	 * 		{
	 * 		   "$ref":"#/definitions/Device"
	 * 		},
	 * 		{  
	 * 		   "type": "object",
	 * 		   "properties":{
	 *             "address": {
	 * 		          "type":"string",
	 * 		          "description":"The short address of this device on the zigbee network"
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


abstract class ZigateDevice extends Device
{
	
	public static $defaultAttr = array(
		'address' => null,
		'model' => null,
		'manufacturer' => null
	);
	
	public function gateway(){
		return $this->createdBy();
	}
	
	public static function validate($key, &$value, &$context) {
		$ret = false;
		switch($key){
			case 'address':
				$ret = is_string($value) && !empty($value);
				break;
			case 'model':
			case 'manufacturer':
				$ret = is_null($value) || (is_string($value) && !empty($value));
				break;
			default:
				$ret = parent::validate($key,$value,$context);
				break;
			
		}
		return $ret;
	}
	
	
	public function operations(){
		return array(
			new Operation($this, 'listEndPoints', null, 'application/json', 'list available endpoints', function($op, $stream, $data, $options){
				return $op->device()->sendMessage('0045', str_pad($op->device()->address, 4, "0", STR_PAD_LEFT), true, $stream, $options);
			}),
			new Operation($this, 'getDescriptor', Helpers::array_to_object_recursive(array(
				'type' => 'object',
				'additionalProperties' => false,
				'required' => array('endpoint'),
				'properties' => array(
					'endpoint' => array(
						'type' => 'string',
						'minLength' => 1,
						'maxLength' => 2
					)
				)
			)), 'application/json', 'retrieve the descriptor of a given endpoint', function($op, $stream, $data, $options){
				$data = array_merge(array('endpoint' => '00'), $data);
				return $op->device()->sendMessage('0043', str_pad($op->device()->address, 4, "0", STR_PAD_LEFT).str_pad($data['endpoint'], 2, "0", STR_PAD_LEFT), true, $stream, $options);
			})
		);
	}
	
	
	public function onMessage(Message $message){
		
		// device specific !
		$this->setConnectState(true);
		
	}
	
	
	// create a new resource
	protected static function createZigateDevice(Ething $ething, array $attributes, array $meta = array(), Resource $createdBy = null) {
		if(!($createdBy instanceof ZigateGateway))
			throw new Exception("This ZigateDevice must be created by a ZigateGateway");
		return parent::createDevice($ething, array_merge(self::$defaultAttr, $attributes), array_merge( array(
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
		return $this->gateway()->sendMessage($type, $payload, $waitResponse, $stream, $options);
	}
	
	
	
}



