<?php

	/**
	 * @swagger-definition
	 * "Device\\MihomeSensorHT":{ 
	 *   "type": "object",
	 *   "description": "Mihome temperatire/humidity/pressure Sensor Device class.",
	 * 	 "allOf": [
	 * 		{
	 * 		   "$ref":"#/definitions/MihomeDevice"
	 * 		},
	 * 		{  
	 * 		   "type": "object",
	 * 		   "properties":{}
	 * 		}
	 *   ]
	 * }
	 */

namespace Ething\Device;

use \Ething\Exception;
use \Ething\Resource;
use \Ething\Ething;
use \Ething\Mihome\Mihome;

class MihomeSensorHT extends MihomeDevice
{
	
	
	public static $defaultAttr = array();
	
	
	
	public function operations(){
		return array();
	}
	
	public static function create(Ething $ething, array $attributes, Resource $createdBy = null) {
		return parent::createMihomeDevice($ething, array_merge(self::$defaultAttr, $attributes), array(), $createdBy);
	}
	
	
	public function decodeData(array $data) {
		$attr = array();
		
		if(isset($data['temperature'])){
			$attr['temperature'] = intval($data['temperature'])/100.0;
		}
		if(isset($data['humidity'])){
			$attr['humidity'] = intval($data['humidity'])/100.0;
		}
		if(isset($data['pressure'])){ // hPa
			$attr['pressure'] = intval($data['pressure']);
		}
		
		return $attr;
	}
	
	public function storeData(array $attr){
		if(!empty($attr)){
			
			$this->setData($attr);
			
			$storageName = 'data';
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
				$storage->insert($attr);
			}
			
			$this->dispatchSignal(\Ething\Event\DeviceDataSet::emit($this, (object)$attr));
		}
	}
	
}



 