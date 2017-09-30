<?php

	/**
	 * @swagger-definition
	 * "RFLinkMultimeter":{ 
	 *   "type": "object",
	 *   "summary": "Generic RFLink multimeter.",
	 *   "description": "RFLinkMultimeter Device resource representation. This device is automatically created by a RFLinkGateway instance.",
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

class RFLinkMultimeter extends Device
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
		
		if($this->hasData('KWATT')){
			$ops[] = new Operation($this, 'getKWatt', null, 'application/json', 'return the power (in KWatt)', function($op, $stream, $data, $options){
					$stream->out($op->device()->getData('KWATT'));
					return true;
				});
		}
		
		if($this->hasData('WATT')){
			$ops[] = new Operation($this, 'getWatt', null, 'application/json', 'return the power (in Watt)', function($op, $stream, $data, $options){
					$stream->out($op->device()->getData('WATT'));
					return true;
				});
		}
		
		if($this->hasData('CURRENT')){
			$ops[] = new Operation($this, 'getCurrent', null, 'application/json', 'return the current phase 1 (in A)', function($op, $stream, $data, $options){
					$stream->out($op->device()->getData('CURRENT'));
					return true;
				});
		}
		
		if($this->hasData('CURRENT2')){
			$ops[] = new Operation($this, 'getCurrent2', null, 'application/json', 'return the current phase 2 (in A)', function($op, $stream, $data, $options){
					$stream->out($op->device()->getData('CURRENT2'));
					return true;
				});
		}
		
		if($this->hasData('CURRENT3')){
			$ops[] = new Operation($this, 'getCurrent3', null, 'application/json', 'return the current phase 3 (in A)', function($op, $stream, $data, $options){
					$stream->out($op->device()->getData('CURRENT3'));
					return true;
				});
		}
		
		if($this->hasData('VOLT')){
			$ops[] = new Operation($this, 'getVoltage', null, 'application/json', 'return the voltage (in V)', function($op, $stream, $data, $options){
					$stream->out($op->device()->getData('VOLT'));
					return true;
				});
		}
		
		if($this->hasData('FREQ')){
			$ops[] = new Operation($this, 'getFrequency', null, 'application/json', 'return the frequency (in Hz)', function($op, $stream, $data, $options){
					$stream->out($op->device()->getData('FREQ'));
					return true;
				});
		}
		
		if($this->hasData('PF')){
			$ops[] = new Operation($this, 'getPowerFactor', null, 'application/json', 'return the power factor (between -1 and 1)', function($op, $stream, $data, $options){
					$stream->out($op->device()->getData('PF'));
					return true;
				});
		}
		
		if($this->hasData('ENERGY')){
			$ops[] = new Operation($this, 'getEnergy', null, 'application/json', 'return the instant energy (in watt hour)', function($op, $stream, $data, $options){
					$stream->out($op->device()->getData('ENERGY'));
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
			'name' => 'multimeter-'.$args['ID']
		), $gateway);
	}
	
	public function processMessage($protocol, array $args){
		$this->updateSeenDate();
		
		$data = array();
		
		if(isset($args['KWATT'])){
			$data['KWATT'] = RFLink::convertWatt($args['KWATT']);
		}
		
		if(isset($args['WATT'])){
			$data['WATT'] = RFLink::convertWatt($args['WATT']);
		}
		
		if(isset($args['CURRENT'])){
			$data['CURRENT'] = RFLink::convertCurrent($args['CURRENT']);
		}
		
		if(isset($args['CURRENT2'])){
			$data['CURRENT2'] = RFLink::convertCurrent($args['CURRENT2']);
		}
		
		if(isset($args['CURRENT3'])){
			$data['CURRENT3'] = RFLink::convertCurrent($args['CURRENT3']);
		}
		
		if(isset($args['VOLT'])){
			$data['VOLT'] = RFLink::convertVoltage($args['VOLT']);
		}
		
		if(isset($args['FREQ'])){
			$data['FREQ'] = RFLink::convertFreq($args['FREQ']);
		}
		
		if(isset($args['PF'])){
			$data['PF'] = RFLink::convertPowerFactor($args['PF']);
		}
		
		if(isset($args['ENERGY'])){
			$data['ENERGY'] = RFLink::convertEnergy($args['ENERGY']);
		}
		
		if(!empty($data)) $this->storeData($data);
		
		if(isset($args['BAT'])){
			$this->set('battery', RFLink::convertBattery($args['BAT']));
		}
	}
}



