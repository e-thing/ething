<?php

	/**
	 * @swagger-definition
	 * "Device\\ZigateAqaraTHP":{ 
	 *   "type": "object",
	 *   "description": "Mihome temperatire/humidity/pressure Sensor Device class.",
	 * 	 "allOf": [
	 * 		{
	 * 		   "$ref":"#/definitions/ZigateDevice"
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
use \Ething\Zigate\Zigate;
use \Ething\Zigate\Message;

class ZigateAqaraTHP extends ZigateDevice
{
	
	
	public static $defaultAttr = array();
	
	
	
	public static function create(Ething $ething, array $attributes, Resource $createdBy = null) {
		return parent::createZigateDevice($ething, array_merge(self::$defaultAttr, $attributes), array(), $createdBy);
	}
	
	
	public function onMessage(Message $message){
		
		
		
	}
	
}



 