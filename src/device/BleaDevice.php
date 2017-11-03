<?php

	/**
	 * @swagger-definition
	 * "Device\\BleaDevice":{ 
	 *   "type": "object",
	 *   "description": "Blea Device base class.",
	 * 	 "allOf": [
	 * 		{
	 * 		   "$ref":"#/definitions/Device"
	 * 		},
	 * 		{  
	 * 		   "type": "object",
	 * 		   "properties":{
	 *             "mac": {
	 * 		          "type":"string",
	 * 		          "description":"The mac address of the device."
	 * 		       },
	 *             "rssi": {
	 * 		          "type":"number",
	 * 		          "description":"The strength of the device's signal as seen on the receiving gateway.",
	 * 		          "readOnly": true
	 * 		       },
	 *             "gateway": {
	 * 		          "type":"string",
	 * 		          "description":"The id of the last gateway that has seen this device.",
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


class BleaDevice extends Device
{
	
	
	public static $defaultAttr = array(
		'mac' => null
	);
	
	
	public static function validate($key, &$value, &$context) {
		$ret = false;
		switch($key){
			case 'mac':
				if(is_string($value)){
					$context['postfns'][] = function($r) {
						// check if there is no other gateway with the same address
						if(count($r->ething->find(array(
							'mac' => $r->get('mac'),
							'_id' => array( '$ne' => $r->id() )
						)))>0)
							throw new Exception('a blea device with the same mac address already exists');
					};
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
		return array(
			new Operation($this, 'refresh', null, null, 'try to refresh this device', function($op, $stream, $data, $options){
				return $op->device()->refresh();
			})
		);
	}
	
	
	public function refresh(){
		return $this->sendData(array(
			'cmd' => 'refresh',
			'device' => array(
				'id' => $this->mac,
				'name' => preg_replace("/^.*\\\/", '', $this->type())
			)
		));
	}
	
	public function sendData(array $data, $stream = null, $options = array()){
		return $this->ething->daemon('device.blea.send '.$this->id().' '.\base64_encode(\json_encode($data))."\n", $stream, $options);
	}
	
	
	protected static function createBleaDevice(Ething $ething, array $attributes, array $meta = array(), Resource $createdBy = null) {
		return parent::createDevice($ething, array_merge(self::$defaultAttr, $attributes), array_merge(array(
			'connected' => false,
			'rssi' => null,
			'gateway' => null
		), $meta), $createdBy);
	}
	
	public function setConnectState($connected) {
		$change = $this->setAttr('connected', boolval($connected));
		$this->update();
		
		if($change){
			$this->dispatchSignal($connected ? \Ething\Event\DeviceConnected::emit($this) : \Ething\Event\DeviceDisconnected::emit($this));
		}
	}
	
	public function processData(array $attr, BleaGateway $gatewayDevice) {
		
		$this->updateSeenDate();
		
		if(isset($attr['battery'])){
			$this->set('battery', $attr['battery']);
		}
		
		if(isset($attr['rssi'])){
			$this->setAttr('rssi', $attr['rssi']);
		}
		
		if(isset($attr['rawdata'])){
			$this->ething->logger()->info("BleaDevice: {$this->name()} id={$this->id()} rawdata = {$attr['rawdata']}");
		}
		
		$this->setAttr('gateway', $gatewayDevice->id());
		
		$this->update();
	}
	
}



