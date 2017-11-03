<?php

	/**
	 * @swagger-definition
	 * "Device\\BleaEthernetGateway":{ 
	 *   "type": "object",
	 *   "description": "BleaEthernetGateway Device resource representation",
	 * 	 "allOf": [
	 * 		{
	 * 		   "$ref":"#/definitions/Device\\BleaGateway"
	 * 		},
	 * 		{  
	 * 		   "type": "object",
	 * 		   "properties":{
	 *             "host": {
	 * 		          "type":"string",
	 * 		          "description":"The ip address or hostname of the gateway."
	 * 		       },
	 *             "port": {
	 * 		          "type":"number",
	 * 		          "description":"The port number of the gateway.",
	 * 		          "default": 5005
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



class BleaEthernetGateway extends BleaGateway
{
		
	public static $defaultAttr = array(
		'host' => null,
		'port' => 5005
	);
	
	
	public static function validate($key, &$value, &$context) {
		$ret = false;
		switch($key){
			case 'host':
				if(is_string($value) && !empty($value)){
					
					$validIpAddressRegex = '/^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$/';
					$validHostnameRegex = '/^(([a-zA-Z]|[a-zA-Z][a-zA-Z0-9\-]*[a-zA-Z0-9])\.)*([A-Za-z]|[A-Za-z][A-Za-z0-9\-]*[A-Za-z0-9])$/';
					
					if(preg_match($validIpAddressRegex, $value) || preg_match($validHostnameRegex, $value)){
						$ret = true;
					}
					
				}
				break;
			case 'port':
				if(is_int($value) && $value>=0 && $value<=65535){
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



