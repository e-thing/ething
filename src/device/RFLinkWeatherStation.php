<?php

	/**
	 * @swagger-definition
	 * "RFLinkWeatherStation":{ 
	 *   "type": "object",
	 *   "summary": "Generic RFLink weather station.",
	 *   "description": "RFLinkWeatherStation Device resource representation. This device is automatically created by a RFLinkGateway instance.",
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

class RFLinkWeatherStation extends Device
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
		
		if($this->hasData('RAIN')){
			$ops[] = new Operation($this, 'getRain', null, 'application/json', 'return current rain level (in mmm)', function($op, $stream, $data, $options){
					$stream->out($op->device()->getData('RAIN'));
					return true;
				});
		}
		
		if($this->hasData('RAINRATE')){
			$ops[] = new Operation($this, 'getRainRate', null, 'application/json', 'return current rain rate (in mmm/h)', function($op, $stream, $data, $options){
					$stream->out($op->device()->getData('RAINRATE'));
					return true;
				});
		}
		
		if($this->hasData('WINSP')){
			$ops[] = new Operation($this, 'getWindSpeed', null, 'application/json', 'return current wind speed (in km/h)', function($op, $stream, $data, $options){
					$stream->out($op->device()->getData('WINSP'));
					return true;
				});
		}
		
		if($this->hasData('AWINSP')){
			$ops[] = new Operation($this, 'getAverageWindSpeed', null, 'application/json', 'return current average wind speed (in km/h)', function($op, $stream, $data, $options){
					$stream->out($op->device()->getData('AWINSP'));
					return true;
				});
		}
		
		if($this->hasData('WINGS')){
			$ops[] = new Operation($this, 'getWindGust', null, 'application/json', 'return current wind gust (in km/h)', function($op, $stream, $data, $options){
					$stream->out($op->device()->getData('WINGS'));
					return true;
				});
		}
		
		if($this->hasData('WINDIR')){
			$ops[] = new Operation($this, 'getWindDirection', null, 'application/json', 'return current wind direction (in degrees)', function($op, $stream, $data, $options){
					$stream->out($op->device()->getData('WINDIR'));
					return true;
				});
		}
		
		if($this->hasData('WINCHL')){
			$ops[] = new Operation($this, 'getWindChill', null, 'application/json', 'return current wind chill (in degree Celsius)', function($op, $stream, $data, $options){
					$stream->out($op->device()->getData('WINCHL'));
					return true;
				});
		}
		
		if($this->hasData('WINTMP')){
			$ops[] = new Operation($this, 'getWindTemperature', null, 'application/json', 'return current wind temperature (in degree Celsius)', function($op, $stream, $data, $options){
					$stream->out($op->device()->getData('WINTMP'));
					return true;
				});
		}
		
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
		
		if($this->hasData('LUX')){
			$ops[] = new Operation($this, 'getLUX', null, 'application/json', 'return current light intensity', function($op, $stream, $data, $options){
					$stream->out($op->device()->getData('LUX'));
					return true;
				});
		}
		
		if($this->hasData('HSTATUS')){
			$ops[] = new Operation($this, 'getHygroStatus', null, 'application/json', 'return current hygrometry status', function($op, $stream, $data, $options){
					$stream->out($op->device()->getData('HSTATUS'));
					return true;
				});
		}
		
		if($this->hasData('BFORECAST')){
			$ops[] = new Operation($this, 'getForecast', null, 'application/json', 'return forecast', function($op, $stream, $data, $options){
					$stream->out($op->device()->getData('BFORECAST'));
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
			'name' => 'weatherstation-'.$args['ID']
		), $gateway);
	}
	
	public function processMessage($protocol, array $args){
		$this->updateSeenDate();
		
		$data = array();
		
		if(isset($args['RAIN'])){
			$data['RAIN'] = RFLink::convertRain($args['RAIN']);
		}
		
		if(isset($args['RAINRATE'])){
			$data['RAINRATE'] = RFLink::convertRainRate($args['RAINRATE']);
		}
		
		if(isset($args['WINSP'])){
			$data['WINSP'] = RFLink::convertWindSpeed($args['WINSP']);
		}
		
		if(isset($args['AWINSP'])){
			$data['AWINSP'] = RFLink::convertWindSpeed($args['AWINSP']);
		}
		
		if(isset($args['WINGS'])){
			$data['WINGS'] = RFLink::convertWindGust($args['WINGS']);
		}
		
		if(isset($args['WINDIR'])){
			$data['WINDIR'] = RFLink::convertWindDirection($args['WINDIR']);
		}
		
		if(isset($args['WINCHL'])){
			$data['WINCHL'] = RFLink::convertTemperature($args['WINCHL']);
		}
		
		if(isset($args['WINTMP'])){
			$data['WINTMP'] = RFLink::convertTemperature($args['WINTMP']);
		}
		
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
		
		if(isset($args['LUX'])){
			$data['LUX'] = RFLink::convertLux($args['LUX']);
		}
		
		if(isset($args['HSTATUS'])){
			$data['HSTATUS'] = RFLink::convertHygroStatus($args['HSTATUS']);
		}
		
		if(isset($args['BFORECAST'])){
			$data['BFORECAST'] = RFLink::convertForecast($args['BFORECAST']);
		}
		
		if(!empty($data)) $this->storeData($data);
		
		if(isset($args['BAT'])){
			$this->set('battery', RFLink::convertBattery($args['BAT']));
		}
	}
}



