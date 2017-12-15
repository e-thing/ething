<?php

	/**
	 * @swagger-definition
	 * "Device\\MihomeDevice":{ 
	 *   "type": "object",
	 *   "description": "Mihome Device base class.",
	 * 	 "allOf": [
	 * 		{
	 * 		   "$ref":"#/definitions/Device"
	 * 		},
	 * 		{  
	 * 		   "type": "object",
	 * 		   "properties":{
	 *             "sid": {
	 * 		          "type":"string",
	 * 		          "description":"The uniq sid of the device",
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
use \Ething\Resource;
use \Ething\Ething;
use \Ething\Mihome\Mihome;

abstract class MihomeDevice extends Device
{
	
	
	public static $defaultAttr = array(
		'sid' => null
	);
	
	
	public static function validate($key, &$value, &$context) {
		$ret = false;
		switch($key){
			case 'sid':
				if(is_string($value) && !empty($value)){
					$ret = true;
				}
				break;
			default:
				$ret = parent::validate($key,$value,$context);
				break;
			
		}
		return $ret;
	}
	
	
	
	public function operations(){
		return array();
	}
	
	
	
	
	protected static function createMihomeDevice(Ething $ething, array $attributes, array $meta = array(), Resource $createdBy = null) {
		/*if(!($createdBy instanceof MihomeGateway))
			throw new Exception("This device must be created by a MihomeGateway");*/
		return parent::createDevice($ething, array_merge(self::$defaultAttr, $attributes), array_merge(array(
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
	
	abstract public function decodeData(array $data);
	
	public function processData(array $response) {
		
		$this->updateSeenDate();
		
		$data = \json_decode($response['data'], true);
		
		$attr = array();
		
		if(is_array($data)){
			
			if(isset($data['voltage'])){
				$attr['voltage'] = intval($data['voltage'])/1000.; // volt
			}
			
			$attr = array_merge($attr, $this->decodeData($data));
		}
		
		$this->storeData($attr);
		
		$this->setConnectState(true);
		
	}
	
	public function storeData(array $attr){
		if(!empty($attr)){
			$this->setData($attr);
			$this->dispatchSignal(\Ething\Event\DeviceDataSet::emit($this, (object)$attr));
		}
	}
	
	public function gateway(){
		return $this->createdBy();
	}
	
	public function sendCommand(array $cmd, $stream = null, $options = array()){
		return $this->gateway()->sendMessage($cmd, $stream, $options);
	}
	
}



