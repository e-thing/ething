<?php

	/**
	 * @swagger-definition
	 * "Device\\BleaLocalGateway":{ 
	 *   "type": "object",
	 *   "description": "BleaLocalGateway Device resource representation",
	 * 	 "allOf": [
	 * 		{
	 * 		   "$ref":"#/definitions/Device\\BleaGateway"
	 * 		},
	 * 		{  
	 * 		   "type": "object",
	 * 		   "properties":{
	 *             "device": {
	 * 		          "type":"string",
	 * 		          "description":"The name of the bluetooth device. Usually hci0."
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



class BleaLocalGateway extends BleaGateway
{
		
	public static $defaultAttr = array(
		'device' => null
	);
	
	
	public static function validate($key, &$value, &$context) {
		$ret = false;
		switch($key){
			case 'device':
				if(is_string($value) && !empty($value)){
					
					$context['postfns'][] = function($r) {
						// check if there is no other gateway with the same port
						if(count($r->ething->find(array(
							'type' => 'Device\\BleaLocalGateway',
							'device' => $r->get('device'),
							'_id' => array( '$ne' => $r->id() )
						)))>0)
							throw new Exception('a gateway using the same device name already exists');
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
	
	
	// create a new resource
	public static function create(Ething $ething, array $attributes, Resource $createdBy = null) {
		return parent::createBleaGateway($ething, array_merge(self::$defaultAttr, $attributes), array(), $createdBy);
	}
	
}



