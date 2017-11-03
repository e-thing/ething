<?php

	/**
	 * @swagger-definition
	 * "Device\\BleaUnknown":{ 
	 *   "type": "object",
	 *   "description": "BleaUnknown device representation",
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

class BleaUnknown extends BleaDevice
{	

	public static $defaultAttr = array();
	
	
	public function operations(){
		return array();
	}
	
	public static function create(Ething $ething, array $attributes, Resource $createdBy = null) {
		return parent::createBleaDevice($ething, array_merge(self::$defaultAttr, $attributes), array(), $createdBy);
	}
	
}




