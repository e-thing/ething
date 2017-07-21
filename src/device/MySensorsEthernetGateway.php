<?php

	/**
	 * @swagger-definition
	 * "Device\\MySensorsEthernetGateway":{ 
	 *   "type": "object",
	 *   "description": "MySensorsEthernetGateway Device resource representation",
	 * 	 "allOf": [
	 * 		{
	 * 		   "$ref":"#/definitions/Device\\MySensorsGateway"
	 * 		},
	 * 		{  
	 * 		   "type": "object",
	 * 		   "properties":{
	 *             "address": {
	 * 		          "type":"string",
	 * 		          "description":"The ip address or hostname of the gateway."
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



class MySensorsEthernetGateway extends MySensorsGateway
{
	
	const VALIDATE_ADDRESS = '/^(([0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3})|([\\w-.]+))(:[0-9]{1,5})?$/';
	
	public static $defaultAttr = array(
		'address' => null
	);
	
	
	public static function validate($key, &$value, &$context) {
		$ret = false;
		switch($key){
			case 'address':
				if(!is_string($value) || !preg_match(static::VALIDATE_ADDRESS, $value))
					throw new Exception('invalid address');
				$context['postfns'][] = function($r) {
					// check if there is no other gateway with the same address
					if(count($r->ething->find(array(
						'type' => 'Device\\MySensorsGateway',
						'address' => $r->get('address'),
						'_id' => array( '$ne' => $r->id() )
					)))>0)
						throw new Exception('a gateway with the same address already exists');
				};
				$context['callbacks']['restart'] = function($r) {
					$r->restart();
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
		return parent::createMySensorsGateway($ething, array_merge(self::$defaultAttr, $attributes), array(), $createdBy);
	}
	
	public function instanciateController(){
		return new \Ething\MySensors\EthernetController($this);
	}
}



