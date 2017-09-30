<?php

	/**
	 * @swagger-definition
	 * "RFLinkThermometer":{ 
	 *   "type": "object",
	 *   "summary": "Generic RFLink thermometer.",
	 *   "description": "RFLinkThermometer Device resource representation. This device is automatically created by a RFLinkGateway instance.",
	 * 	 "allOf": [
	 * 		{
	 * 		   "$ref":"#/definitions/Device"
	 * 		},
	 * 		{  
	 * 		   "type": "object",
	 * 		   "properties":{
	 *             "nodeId": {
	 * 		          "type":"string",
	 * 		          "description":"The id of the device."
	 * 		       },
	 *             "protocol": {
	 * 		          "type":"string",
	 * 		          "description": "The protocol used by this device."
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
use \Ething\RFLink\RFLink;
use \Ething\Helpers;
use \Ething\Stream;

class RFLinkThermometer extends Device
{
	
	
	public static $defaultAttr = array(
		'nodeId' => null,
		'protocol' => null
	);
	
	public function gateway(){
		return $this->createdBy();
	}
	
	public function storeData($attr){
		if(!empty($attr)){
			
			$this->setData($attr);
			
			$storageName = 'temperature';
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
	
	public static function validate($key, &$value, &$context) {
		$ret = false;
		switch($key){
			case 'nodeId':
				if(is_string($value) && strlen($value)){
					$ret = true;
					// check if there is a node with the same id that already exist
					$context['postfns'][] = function($r){
						if($r->gateway()->getNode(array(
							'nodeId' => $r->nodeId,
							'protocol' => $r->protocol,
							'_id' => array( '$ne' => $r->id() )
						)))
							throw new Exception('a node with the same nodeId and protocol already exists');
					};
				}
				break;
			case 'protocol':
				$ret = (is_string($value) && strlen($value));
				break;
			default:
				$ret = parent::validate($key,$value,$context);
				break;
			
		}
		return $ret;
	}
	
	
	public function operations(){
		$ops = array();
		
		if($this->hasData('TEMP')){
			$ops[] = new Operation($this, 'getTemperature', null, 'application/json', 'return current temperature (in degree Celsius)', function($op, $stream, $data, $options){
					$stream->out($op->device()->getData('TEMP'));
					return true;
				});
		}
		
		if($this->hasData('HUM')){
			$ops[] = new Operation($this, 'getHumidity', null, 'application/json', 'return current humidity (in %)', function($op, $stream, $data, $options){
					$stream->out($op->device()->getData('HUM'));
					return true;
				});
		}
		
		if($this->hasData('BARO')){
			$ops[] = new Operation($this, 'getPressure', null, 'application/json', 'return current atmospheric pressure (in Pa)', function($op, $stream, $data, $options){
					$stream->out($op->device()->getData('BARO'));
					return true;
				});
		}
		
		if($this->hasData('UV')){
			$ops[] = new Operation($this, 'getUV', null, 'application/json', 'return current UV intensity', function($op, $stream, $data, $options){
					$stream->out($op->device()->getData('UV'));
					return true;
				});
		}
		
		return $ops;
	}
	
	
	
	// create a new resource
	public static function create(Ething $ething, array $attributes, Resource $createdBy = null) {
		if(!($createdBy instanceof RFLinkGateway))
			throw new Exception("This RFLinkNode must be created by a RFLinkGateway");
		return parent::createDevice($ething, array_merge(self::$defaultAttr, $attributes), array(), $createdBy);
	}
	
	// functions used by controller
	public static function createDeviceFromMessage($protocol, array $args, RFLinkGateway $gateway) {
		return self::create($gateway->ething, array(
			'nodeId' => $args['ID'],
			'protocol' => $protocol,
			'name' => 'thermometer-'.$args['ID']
		), $gateway);
	}
	
	public function processMessage($protocol, array $args){
		$this->updateSeenDate();
		
		$data = array();
		
		if(isset($args['TEMP'])){
			$data['TEMP'] = RFLink::convertTemperature($args['TEMP']);
		}
		
		if(isset($args['HUM'])){
			$data['HUM'] = RFLink::convertHum($args['HUM']);
		}
		
		if(isset($args['BARO'])){
			$data['BARO'] = RFLink::convertBaro($args['BARO']);
		}
		
		if(isset($args['UV'])){
			$data['UV'] = RFLink::convertUV($args['UV']);
		}
		
		if(!empty($data)) $this->storeData($data);
		
		if(isset($args['BAT'])){
			$this->set('battery', RFLink::convertBattery($args['BAT']));
		}
	}
}



