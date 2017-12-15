<?php

	/**
	 * @swagger-definition
	 * "Device\\ZigateSerialGateway":{ 
	 *   "type": "object",
	 *   "description": "ZigateSerialGateway Device resource representation",
	 * 	 "allOf": [
	 * 		{
	 * 		   "$ref":"#/definitions/Device\\ZigateGateway"
	 * 		},
	 * 		{  
	 * 		   "type": "object",
	 * 		   "properties":{
	 *             "port": {
	 * 		          "type":"string",
	 * 		          "description":"The serial port name."
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



class ZigateSerialGateway extends ZigateGateway
{
	
	public static $defaultAttr = array(
		'port' => null
	);
	
	
	public static function validate($key, &$value, &$context) {
		$ret = false;
		switch($key){
			case 'port':
				if(!is_string($value))
					throw new Exception('invalid serial port');
				$context['postfns'][] = function($r) {
					// check if there is no other gateway with the same port
					if(count($r->ething->find(array(
						'type' => array( '$in' => array('Device\\MySensorsSerialGateway','Device\\RFLinkSerialGateway','Device\\ZigateSerialGateway')),
						'port' => $r->get('port'),
						'_id' => array( '$ne' => $r->id() )
					)))>0)
						throw new Exception('a device using the same port already exists');
				};
				$ret = true;
				break;
			default:
				$ret = parent::validate($key,$value,$context);
				break;
			
		}
		return $ret;
	}
	
	
	// create a new resource
	public static function create(Ething $ething, array $attributes, Resource $createdBy = null) {
		return parent::createZigateGateway($ething, array_merge(self::$defaultAttr, $attributes), array(), $createdBy);
	}
	
	
}



