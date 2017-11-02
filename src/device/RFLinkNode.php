<?php


	 
	 
namespace Ething\Device;

use \Ething\Exception;
use \Ething\Ething;
use \Ething\Resource;
use \Ething\RFLink\RFLink;
use \Ething\Stream;
use \Ething\Helpers;

class RFLinkNode extends Device
{
	
	
	public static $defaultAttr = array(
		'subType' => null,
		'nodeId' => null,
		'protocol' => null,
		'switchId' => null
	);
	
	
	
	public function gateway(){
		return $this->createdBy();
	}
	
	public function storeData($attr){
		if(!empty($attr)){
			
			$storedAttr = array();
			
			// convert/rename
			foreach($attr as $k => $v){
				$storedAttr[RFLink::getAttrName($k)] = RFLink::convertAttrValue($k, $v);
			}
			
			$this->setData($storedAttr);
			
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
				$storage->insert($storedAttr);
			}
			
			$this->dispatchSignal(\Ething\Event\DeviceDataSet::emit($this, (object)$storedAttr));
			
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
							'_id' => array( '$ne' => $r->id() ),
							'switchId' => null // accept multiple switches with the same nodeId
						)))
							throw new Exception('a node with the same nodeId and protocol already exists');
					};
				}
				break;
			case 'protocol':
				$ret = (is_string($value) && strlen($value));
				break;
			case 'switchId':
				$ret = (is_string($value) && strlen($value));
				break;
			case 'subType':
				$ret = (is_string($value) && in_array($value, RFLink::$subTypes));
				break;
			default:
				$ret = parent::validate($key,$value,$context);
				break;
			
		}
		return $ret;
	}
	
	
	public function operations(){
		$ops = array();
		
		if($this->subType === 'switch'){
			
			$ops[] = new Operation($this, 'on', null, null, 'turn on', function($op, $stream, $data, $options){
				$node = $op->device();
				if($node->gateway()->sendMessage("10;{$node->protocol};{$node->nodeId};{$node->switchId};ON;", $stream, $options)){ // 10;NewKaku;00c142;1;ON;
					$node->storeData(array(
						'CMD' => 'ON'
					));
					return true;
				}
				return false;
			});
			$ops[] = new Operation($this, 'off', null, null, 'turn off', function($op, $stream, $data, $options){
				$node = $op->device();
				if($node->gateway()->sendMessage("10;{$node->protocol};{$node->nodeId};{$node->switchId};OFF;", $stream, $options)){ // 10;NewKaku;00c142;1;OFF;
					$node->storeData(array(
						'CMD' => 'OFF'
					));
					return true;
				}
				return false;
			});
			$ops[] = new Operation($this, 'setState', Helpers::array_to_object_recursive(array(
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
				
				$value = 'OFF';
				
				if(isset($data['CMD'])){
					if(is_string($data['CMD']) && preg_match('/^on$/i', $data['CMD']))
						$value = 'ON';
					else 
						$value = boolval($data['CMD']) ? 'ON': 'OFF';
				}
				
				if($node->gateway()->sendMessage("10;{$node->protocol};{$node->nodeId};{$node->switchId};".$value.";", $stream, $options)){ // 10;NewKaku;00c142;1;OFF;
					$node->storeData(array(
						'CMD' => $value
					));
					return true;
				}
				return false;
			});
			
		}
		
		if( in_array($this->subType , array('switch', 'door' , 'motion')) ){
			$ops[] = new Operation($this, 'getState', null, 'application/json', 'return current state', function($op, $stream, $data, $options){
				$stream->sendJSON($op->device()->getData(RFLink::getAttrName('CMD'),false));
				return true;
			});
		}
		
		if($this->subType === 'thermometer'){
			if($this->hasData('TEMP')){
				$ops[] = new Operation($this, 'getTemperature', null, 'application/json', 'return current temperature (in degree Celsius)', function($op, $stream, $data, $options){
						$stream->sendJSON($op->device()->getData(RFLink::getAttrName('TEMP')));
						return true;
					});
			}
			
			if($this->hasData('HUM')){
				$ops[] = new Operation($this, 'getHumidity', null, 'application/json', 'return current humidity (in %)', function($op, $stream, $data, $options){
						$stream->sendJSON($op->device()->getData(RFLink::getAttrName('HUM')));
						return true;
					});
			}
			
			if($this->hasData('BARO')){
				$ops[] = new Operation($this, 'getPressure', null, 'application/json', 'return current atmospheric pressure (in Pa)', function($op, $stream, $data, $options){
						$stream->sendJSON($op->device()->getData(RFLink::getAttrName('BARO')));
						return true;
					});
			}
			
			if($this->hasData('UV')){
				$ops[] = new Operation($this, 'getUV', null, 'application/json', 'return current UV intensity', function($op, $stream, $data, $options){
						$stream->sendJSON($op->device()->getData(RFLink::getAttrName('UV')));
						return true;
					});
			}
		}
		
		if($this->subType === 'weatherStation'){
			if($this->hasData('RAIN')){
				$ops[] = new Operation($this, 'getRain', null, 'application/json', 'return current rain level (in mmm)', function($op, $stream, $data, $options){
						$stream->sendJSON($op->device()->getData(RFLink::getAttrName('RAIN')));
						return true;
					});
			}
			
			if($this->hasData('RAINRATE')){
				$ops[] = new Operation($this, 'getRainRate', null, 'application/json', 'return current rain rate (in mmm/h)', function($op, $stream, $data, $options){
						$stream->sendJSON($op->device()->getData(RFLink::getAttrName('RAINRATE')));
						return true;
					});
			}
			
			if($this->hasData('WINSP')){
				$ops[] = new Operation($this, 'getWindSpeed', null, 'application/json', 'return current wind speed (in km/h)', function($op, $stream, $data, $options){
						$stream->sendJSON($op->device()->getData(RFLink::getAttrName('WINSP')));
						return true;
					});
			}
			
			if($this->hasData('AWINSP')){
				$ops[] = new Operation($this, 'getAverageWindSpeed', null, 'application/json', 'return current average wind speed (in km/h)', function($op, $stream, $data, $options){
						$stream->sendJSON($op->device()->getData(RFLink::getAttrName('AWINSP')));
						return true;
					});
			}
			
			if($this->hasData('WINGS')){
				$ops[] = new Operation($this, 'getWindGust', null, 'application/json', 'return current wind gust (in km/h)', function($op, $stream, $data, $options){
						$stream->sendJSON($op->device()->getData(RFLink::getAttrName('WINGS')));
						return true;
					});
			}
			
			if($this->hasData('WINDIR')){
				$ops[] = new Operation($this, 'getWindDirection', null, 'application/json', 'return current wind direction (in degrees)', function($op, $stream, $data, $options){
						$stream->sendJSON($op->device()->getData(RFLink::getAttrName('WINDIR')));
						return true;
					});
			}
			
			if($this->hasData('WINCHL')){
				$ops[] = new Operation($this, 'getWindChill', null, 'application/json', 'return current wind chill (in degree Celsius)', function($op, $stream, $data, $options){
						$stream->sendJSON($op->device()->getData(RFLink::getAttrName('WINCHL')));
						return true;
					});
			}
			
			if($this->hasData('WINTMP')){
				$ops[] = new Operation($this, 'getWindTemperature', null, 'application/json', 'return current wind temperature (in degree Celsius)', function($op, $stream, $data, $options){
						$stream->sendJSON($op->device()->getData(RFLink::getAttrName('WINTMP')));
						return true;
					});
			}
			
			if($this->hasData('TEMP')){
				$ops[] = new Operation($this, 'getTemperature', null, 'application/json', 'return current temperature (in degree Celsius)', function($op, $stream, $data, $options){
						$stream->sendJSON($op->device()->getData(RFLink::getAttrName('TEMP')));
						return true;
					});
			}
			
			if($this->hasData('HUM')){
				$ops[] = new Operation($this, 'getHumidity', null, 'application/json', 'return current humidity (in %)', function($op, $stream, $data, $options){
						$stream->sendJSON($op->device()->getData(RFLink::getAttrName('HUM')));
						return true;
					});
			}
			
			if($this->hasData('BARO')){
				$ops[] = new Operation($this, 'getPressure', null, 'application/json', 'return current atmospheric pressure (in Pa)', function($op, $stream, $data, $options){
						$stream->sendJSON($op->device()->getData(RFLink::getAttrName('BARO')));
						return true;
					});
			}
			
			if($this->hasData('UV')){
				$ops[] = new Operation($this, 'getUV', null, 'application/json', 'return current UV intensity', function($op, $stream, $data, $options){
						$stream->sendJSON($op->device()->getData(RFLink::getAttrName('UV')));
						return true;
					});
			}
			
			if($this->hasData('LUX')){
				$ops[] = new Operation($this, 'getLUX', null, 'application/json', 'return current light intensity', function($op, $stream, $data, $options){
						$stream->sendJSON($op->device()->getData(RFLink::getAttrName('LUX')));
						return true;
					});
			}
			
			if($this->hasData('HSTATUS')){
				$ops[] = new Operation($this, 'getHygroStatus', null, 'application/json', 'return current hygrometry status', function($op, $stream, $data, $options){
						$stream->sendJSON($op->device()->getData(RFLink::getAttrName('HSTATUS')));
						return true;
					});
			}
			
			if($this->hasData('BFORECAST')){
				$ops[] = new Operation($this, 'getForecast', null, 'application/json', 'return forecast', function($op, $stream, $data, $options){
						$stream->sendJSON($op->device()->getData(RFLink::getAttrName('BFORECAST')));
						return true;
					});
			}
		}
		
		if($this->subType === 'multimeter'){
			
			if($this->hasData('WATT') || $this->hasData('KWATT')){
				$ops[] = new Operation($this, 'getWatt', null, 'application/json', 'return the power (in Watt)', function($op, $stream, $data, $options){
						if($op->device()->hasData('WATT'))
							$stream->sendJSON($op->device()->getData(RFLink::getAttrName('WATT')));
						else
							$stream->sendJSON($op->device()->getData(RFLink::getAttrName('KWATT')));
						return true;
					});
			}
			
			if($this->hasData('CURRENT')){
				$ops[] = new Operation($this, 'getCurrent', null, 'application/json', 'return the current phase 1 (in A)', function($op, $stream, $data, $options){
						$stream->sendJSON($op->device()->getData(RFLink::getAttrName('CURRENT')));
						return true;
					});
			}
			
			if($this->hasData('CURRENT2')){
				$ops[] = new Operation($this, 'getCurrent2', null, 'application/json', 'return the current phase 2 (in A)', function($op, $stream, $data, $options){
						$stream->sendJSON($op->device()->getData(RFLink::getAttrName('CURRENT2')));
						return true;
					});
			}
			
			if($this->hasData('CURRENT3')){
				$ops[] = new Operation($this, 'getCurrent3', null, 'application/json', 'return the current phase 3 (in A)', function($op, $stream, $data, $options){
						$stream->sendJSON($op->device()->getData(RFLink::getAttrName('CURRENT3')));
						return true;
					});
			}
			
			if($this->hasData('VOLT')){
				$ops[] = new Operation($this, 'getVoltage', null, 'application/json', 'return the voltage (in V)', function($op, $stream, $data, $options){
						$stream->sendJSON($op->device()->getData(RFLink::getAttrName('VOLT')));
						return true;
					});
			}
			
			if($this->hasData('FREQ')){
				$ops[] = new Operation($this, 'getFrequency', null, 'application/json', 'return the frequency (in Hz)', function($op, $stream, $data, $options){
						$stream->sendJSON($op->device()->getData(RFLink::getAttrName('FREQ')));
						return true;
					});
			}
			
			if($this->hasData('PF')){
				$ops[] = new Operation($this, 'getPowerFactor', null, 'application/json', 'return the power factor (between -1 and 1)', function($op, $stream, $data, $options){
						$stream->sendJSON($op->device()->getData(RFLink::getAttrName('PF')));
						return true;
					});
			}
			
			if($this->hasData('ENERGY')){
				$ops[] = new Operation($this, 'getEnergy', null, 'application/json', 'return the instant energy (in watt hour)', function($op, $stream, $data, $options){
						$stream->sendJSON($op->device()->getData(RFLink::getAttrName('ENERGY')));
						return true;
					});
			}
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
	public static function createDeviceFromMessage($subType, $protocol, array $args, RFLinkGateway $gateway) {
		
		return static::create($gateway->ething, array(
			'nodeId' => $args['ID'],
			'switchId' => isset($args['SWITCH']) ? RFLink::convertSwitchId($args['SWITCH']) : null,
			'protocol' => $protocol,
			'subType' => $subType,
			'name' => $subType.'-'.$args['ID']
		), $gateway);
	}
	
	public function processMessage($protocol, array $args) {
		
		$this->updateSeenDate();
		
		$data = array();
		
		foreach($args as $attr => $value){
			if(array_key_exists($attr, RFLink::$attrMap)){
				$data[$attr] = $value;
			}
		}
		
		if(!empty($data)) $this->storeData($data);
		
		if(isset($args['BAT'])){
			$this->set('battery', RFLink::convertBattery($args['BAT']));
		}
		
	}
}



