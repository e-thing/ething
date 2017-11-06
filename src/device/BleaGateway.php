<?php


	/**
	 * @swagger-definition
	 * "Device\\BleaGateway":{ 
	 *   "type": "object",
	 *   "description": "BleaGateway base class",
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



abstract class BleaGateway extends Device
{
	
	public static $defaultAttr = array(
		'inclusion' => true,
	);
	
	
	public static function validate($key, &$value, &$context) {
		$ret = false;
		switch($key){
			
			case 'inclusion':
				$ret = is_bool($value);
				break;
				
			default:
				$ret = parent::validate($key,$value,$context);
				break;
			
		}
		return $ret;
	}
	
	public function operations(){
		return array(
			new Operation($this, 'learnin', null, null, 'enter into learn mode', function($op, $stream, $data, $options){
				return $op->device()->learnin();
			}),
			new Operation($this, 'learnout', null, null, 'exit the learn mode', function($op, $stream, $data, $options){
				return $op->device()->learnout();
			})
		);
	}
	
	
	public function learnin(){
		return $this->sendData(array(
			'cmd' => 'learnin',
			'allowAll' => 0
		));
	}
	
	public function learnout(){
		return $this->sendData(array(
			'cmd' => 'learnout',
			'allowAll' => 0
		));
	}
	
	public function sendData(array $data, $stream = null, $options = array()){
		return $this->ething->daemon('device.blea.send '.$this->id().' '.\base64_encode(\json_encode($data))."\n", $stream, $options);
	}
	
	// create a new resource
	protected static function createBleaGateway(Ething $ething, array $attributes, array $meta = array(), Resource $createdBy = null) {
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
	
	
	
	
}



