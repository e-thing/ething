<?php

	/**
	 * @swagger-definition
	 * "RFLinkSwitch":{ 
	 *   "type": "object",
	 *   "summary": "Generic RFLink switch.",
	 *   "description": "RFLinkSwitch Device resource representation. This device is automatically created by a RFLinkGateway instance.",
	 * 	 "allOf": [
	 * 		{
	 * 		   "$ref":"#/definitions/Device"
	 * 		},
	 * 		{  
	 * 		   "type": "object",
	 * 		   "properties":{
	 *             "nodeId": {
	 * 		          "type":"string",
	 * 		          "description":"The id of the switch."
	 * 		       },
	 *             "protocol": {
	 * 		          "type":"string",
	 * 		          "description": "The protocol used by this switch."
	 * 		       },
	 *             "switchId": {
	 * 		          "type":"string",
	 * 		          "description": "TThe id of the button."
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

class RFLinkSwitch extends Device
{
	
	
	public static $defaultAttr = array(
		'nodeId' => null,
		'protocol' => null,
		'switchId' => null
	);
	
	public function gateway(){
		return $this->createdBy();
	}
	
	public function storeData($attr){
		if(!empty($attr)){
			
			// format
			foreach($attr as $key => &$value){
				if($key==='CMD'){
					$value = boolval(is_string($value) ? preg_match('/^on$/i', $value) : $value);
				}
			}
			
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
							'type' => array( '$ne' => $r->type() )
						)))
							throw new Exception('a node with the same nodeId and protocol already exists');
					};
				}
				break;
			case 'protocol':
			case 'switchId':
				$ret = (is_string($value) && strlen($value));
				break;
			default:
				$ret = parent::validate($key,$value,$context);
				break;
			
		}
		return $ret;
	}
	
	
	public function operations(){
		return array(
			new Operation($this, 'on', null, null, 'turn on', function($op, $stream, $data, $options){
					$node = $op->device();
					if($node->gateway()->sendMessage("10;{$node->protocol};{$node->nodeId};{$node->switchId};ON;", $stream, $options)){ // 10;NewKaku;00c142;1;ON;
						$node->storeData(array(
							'CMD' => true
						));
						return true;
					}
					return false;
				}),
			new Operation($this, 'off', null, null, 'turn off', function($op, $stream, $data, $options){
					$node = $op->device();
					if($node->gateway()->sendMessage("10;{$node->protocol};{$node->nodeId};{$node->switchId};OFF;", $stream, $options)){ // 10;NewKaku;00c142;1;OFF;
						$node->storeData(array(
							'CMD' => false
						));
						return true;
					}
					return false;
				}),
			new Operation($this, 'getState', null, 'application/json', 'return current state', function($op, $stream, $data, $options){
					$stream->out(in_array($op->device()->getData('CMD','OFF'), array('ON','ALLON')));
					return true;
				}),
			new Operation($this, 'setState', Helpers::array_to_object_recursive(array(
					'type' => 'object',
					'additionalProperties' => false,
					'required' => array('CMD'),
					'properties' => array(
						'CMD' => array(
							"enum" => [ "ON", "OFF" ]
						)
					)
				)), null, 'set state', function($op, $stream, $data, $options){
					$node = $op->device();
					
					$value = false;
					
					if(isset($data['CMD'])){
						$value = is_string($data['CMD']) ? preg_match('/^on$/i', $data['CMD']) : boolval($data['CMD']);
					}
					
					if($node->gateway()->sendMessage("10;{$node->protocol};{$node->nodeId};{$node->switchId};".($value ? 'ON': 'OFF').";", $stream, $options)){ // 10;NewKaku;00c142;1;OFF;
						$node->storeData(array(
							'CMD' => $value
						));
						return true;
					}
					return false;
				})
		);
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
			'switchId' => $args['SWITCH'],
			'protocol' => $protocol,
			'name' => 'switch-'.$args['ID'].'-'.$args['SWITCH']
		), $gateway);
	}
	
	public static function filterDeviceFromMessage(array $devices, $protocol, array $args) {
		if(isset($args['SWITCH'])){
			foreach($devices as $device){
				if($device->switchId === $args['SWITCH']) return $device;
			}
		}
		return null;
	}
	
	public function processMessage($protocol, array $args){
		$this->updateSeenDate();
		
		if(isset($args['CMD'])){
			$this->storeData(array(
				'CMD' => $args['CMD']
			));
		}
		
		if(isset($args['BAT'])){
			$this->set('battery', RFLink::convertBattery($args['BAT']));
		}
	}
}



