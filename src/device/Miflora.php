<?php

	/**
	 * @swagger-definition
	 * "Device\\Miflora":{ 
	 *   "type": "object",
	 *   "description": "Miflora device representation",
	 * 	 "allOf": [
	 * 		{
	 * 		   "$ref":"#/definitions/BleaDevice"
	 * 		}
	 *   ]
	 * }
	 */
	 
namespace Ething\Device;

use \Ething\Exception;
use \Ething\Ething;
use \Ething\Resource;
use \Ething\Helpers;

class Miflora extends BleaDevice
{	

	public static $defaultAttr = array();
	
	
	public function storeData($attr){
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
	
	public function operations(){
		return array_merge(parent::operations(), array(
			
			new Operation($this, 'getTemperature', null, 'application/json', 'return current temperature (in degree Celsius)', function($op, $stream, $data, $options){
				$stream->sendJSON($op->device()->getData('temperature'));
				return true;
			}),
			
			new Operation($this, 'getMoisture', null, 'application/json', 'return moisture (in %)', function($op, $stream, $data, $options){
				$stream->sendJSON($op->device()->getData('moisture'));
				return true;
			}),
			
			new Operation($this, 'getFertility', null, 'application/json', 'return fertility (in uS/cm)', function($op, $stream, $data, $options){
				$stream->sendJSON($op->device()->getData('fertility'));
				return true;
			}),
			
			new Operation($this, 'getLUX', null, 'application/json', 'return luminosity (in lux)', function($op, $stream, $data, $options){
				$stream->sendJSON($op->device()->getData('LUX'));
				return true;
			})
		));
	}
	
	public static function create(Ething $ething, array $attributes, Resource $createdBy = null) {
		return parent::createBleaDevice($ething, array_merge(self::$defaultAttr, $attributes), array(), $createdBy);
	}
	
	public function processData(array $attr) {
		
		parent::processData($attr);
		
		$data = array();
		
		foreach($args as $key => $value){
			
			switch($key){
				case 'moisture':
				case 'fertility':
				case 'temperature':
					$data[$key] = $value;
					break;
				case 'sunlight':
					$data['LUX'] = $value;
					break;
					
			}
		}
		
		if(!empty($data)) $this->storeData($data);
		
	}
	
}




