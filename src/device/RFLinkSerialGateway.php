<?php


	/**
	 * @swagger-definition
	 * "Device\\RFLinkSerialGateway":{ 
	 *   "type": "object",
	 *   "description": "RFLinkSerialGateway Device resource representation",
	 * 	 "allOf": [
	 * 		{
	 * 		   "$ref":"#/definitions/Device\\RFLinkGateway"
	 * 		},
	 * 		{  
	 * 		   "type": "object",
	 * 		   "properties":{
	 *             "baudrate": {
	 * 		          "type":"number",
	 * 		          "description":"The baudrate (default to 57600)."
	 * 		       },
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



class RFLinkSerialGateway extends RFLinkGateway
{
	
	static private $validBauds = array (
		110,
		150,
		300,
		600,
		1200,
		2400,
		4800,
		9600,
		19200,
		38400,
		57600,
		115200
	);
	
	public static $defaultAttr = array(
		'baudrate' => 57600,
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
						'type' => array( '$in' => array('Device\\MySensorsSerialGateway','Device\\RFLinkSerialGateway')),
						'port' => $r->get('port'),
						'_id' => array( '$ne' => $r->id() )
					)))>0)
						throw new Exception('a device using the same port already exists');
				};
				$context['callbacks']['restart'] = function($r) {
					$r->restart();
				};
				$ret = true;
				break;
			case 'baudrate':
				if(!in_array($value, static::$validBauds, true))
					throw new Exception('invalid baudrate'.$value);
				$ret = true;
				$context['callbacks']['restart'] = function($r) {
					$r->restart();
				};
				break;
			default:
				$ret = parent::validate($key,$value,$context);
				break;
			
		}
		return $ret;
	}
	
	
	// create a new resource
	public static function create(Ething $ething, array $attributes, Resource $createdBy = null) {
		return parent::createRFLinkGateway($ething, array_merge(self::$defaultAttr, $attributes), array(), $createdBy);
	}
	
	
	public function instanciateController(){
		return new \Ething\RFLink\SerialController($this);
	}
	
}



