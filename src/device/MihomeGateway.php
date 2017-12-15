<?php


	/**
	 * @swagger-definition
	 * "Device\\MihomeGateway":{ 
	 *   "type": "object",
	 *   "description": "MihomeGateway class",
	 * 	 "allOf": [
	 * 		{
	 * 		   "$ref":"#/definitions/Device"
	 * 		},
	 * 		{  
	 * 		   "type": "object",
	 * 		   "properties":{
	 *             "sid": {
	 * 		          "type":"string",
	 * 		          "description":"The uniq sid of the gateway"
	 * 		       },
	 *             "ip": {
	 * 		          "type":"string",
	 * 		          "description":"The IP address of the gateway"
	 * 		       },
	 *             "port": {
	 * 		          "type":"number",
	 * 		          "description":"The port number of the gateway"
	 * 		       },
	 *             "password": {
	 * 		          "type":"string",
	 * 		          "description":"The password of the gateway"
	 * 		       },
	 *             "connected": {
	 * 		          "type":"boolean",
	 * 		          "description":"Set to true when a connection to that device is opened.",
	 * 		          "readOnly": true
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
use \Ething\Mihome\Mihome;
use \Ething\Helpers;

class MihomeGateway extends Device
{
	
	public static $defaultAttr = array(
		'sid' => null,
		'ip' => null,
		'port' => 9898,
		'password' => null
	);
	
	
	public static $musicMap = array("Police siren", "Police siren 2", "Accident tone", "Missle countdown", "Ghost", "Sniper", "War", "Air Strike", "Barking dogs", "Doorbell ring tone", "Knock on door", "Hilarious", "Alarm clock", "MiMix", "Enthusiastic", "GuitarClassic", "IceWorldPiano", "LeisureTime", "Childhood", "MorningStreamlet", "MusicBox", "Orange", "Thinker");
	
	public static function validate($key, &$value, &$context) {
		$ret = false;
		switch($key){
			case 'ip':
				if(is_string($value) && !empty($value)){
					$validIpAddressRegex = '/^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$/';				
					if(preg_match($validIpAddressRegex, $value)){
						$ret = true;
					}
				}
				break;
			case 'port':
				if(is_int($value) && $value>=0 && $value<=65535){
					$ret = true;
				}
				break;
			case 'sid':
			case 'password':
				if(is_string($value) && !empty($value)){
					$ret = true;
				}
				break;
			default:
				$ret = parent::validate($key,$value,$context);
				break;
			
		}
		return $ret;
	}
	
	public function operations(){
		return array(
			
			new Operation($this, 'on', null, null, 'turn on the device', function($op, $stream, $data, $options){
				$dev = $op->device();
				$hrgb = intval(hexdec(sprintf("0x%02x%06x", 100, \hexdec(preg_replace('/^(#|0x)/i', '', $dev->getData('color', '#FFFFFF'))))));
				$cmd = array(
					"cmd" => "write",
					"model" => "gateway",
					"sid" => $dev->sid,
					"short_id" => 0,
					"data" => array(
						"rgb" => $hrgb
					)
				);
				return $dev->sendCommand($cmd, $stream, $options);
			}),
			
			new Operation($this, 'off', null, null, 'turn off the device', function($op, $stream, $data, $options){
				$dev = $op->device();
				$hrgb = intval(hexdec(sprintf("0x%02x%06x", 0, \hexdec(preg_replace('/^(#|0x)/i', '', $dev->getData('color', '#FFFFFF'))))));
				$cmd = array(
					"cmd" => "write",
					"model" => "gateway",
					"sid" => $dev->sid,
					"short_id" => 0,
					"data" => array(
						"rgb" => $hrgb
					)
				);
				return $dev->sendCommand($cmd, $stream, $options);
			}),
			
			new Operation($this, 'getStatus', null, 'application/json', 'return the current state', function($op, $stream, $data, $options){
				$stream->sendJSON(boolval($op->device()->getData('brightness',0)));
				return true;
			}),
			
			new Operation($this, 'getColor', null, 'application/json', 'return the color (hex)', function($op, $stream, $data, $options){
				$stream->sendJSON($op->device()->getData('color','#000000'));
				return true;
			}),
			
			new Operation($this, 'setColor', Helpers::array_to_object_recursive(array(
				'type' => 'object',
				'additionalProperties' => false,
				'required' => array('color'),
				'properties' => array(
					'color' => array(
						"type" => "string",
						"minLength" => 6,
						"format" => "color"
					),
					'brightness' => array(
						"type" => "integer",
						"minimum" => 0,
						"maximum" => 100,
						"default" => 100
					)
				)
			)), 'application/json', 'set the gateway to the specified color', function($op, $stream, $data, $options){
				
				$data = array_merge(array("color"=>'#0000FF', 'brightness'=>100), $data);
				
				$data['color'] = \hexdec(preg_replace('/^(#|0x)/i', '', $data['color']));
				
				$hrgb = intval(hexdec(sprintf("0x%02x%06x", $data['brightness'], $data['color'])));
				
				$dev = $op->device();
				$cmd = array(
					"cmd" => "write",
					"model" => "gateway",
					"sid" => $dev->sid,
					"short_id" => 0,
					"data" => array(
						"rgb" => $hrgb
					)
				);
				return $dev->sendCommand($cmd, $stream, $options);
			}),
			
			new Operation($this, 'getBrightness', null, 'application/json', 'return the brightness (%)', function($op, $stream, $data, $options){
				$stream->sendJSON($op->device()->getData('brightness',0));
				return true;
			}),
			
			new Operation($this, 'setBrightness', Helpers::array_to_object_recursive(array(
				'type' => 'object',
				'additionalProperties' => false,
				'required' => array('brightness'),
				'properties' => array(
					'brightness' => array(
						"type" => "integer",
						"minimum" => 0,
						"maximum" => 100,
						"default" => 50
					)
				)
			)), null, 'turn on the device with the specified brightness', function($op, $stream, $data, $options){
				$data = array_merge(array('brightness'=>100), $data);
				$dev = $op->device();
				$hrgb = intval(hexdec(sprintf("0x%02x%06x", $data['brightness'], \hexdec(preg_replace('/^(#|0x)/i', '', $dev->getData('color', '#FFFFFF'))))));
				$cmd = array(
					"cmd" => "write",
					"model" => "gateway",
					"sid" => $dev->sid,
					"short_id" => 0,
					"data" => array(
						"rgb" => $hrgb
					)
				);
				return $dev->sendCommand($cmd, $stream, $options);
			}),
			
			new Operation($this, 'playMusic', Helpers::array_to_object_recursive(array(
				'type' => 'object',
				'additionalProperties' => false,
				'required' => array('music', 'volume'),
				'properties' => array(
					'music' => array(
						"enum" => \Ething\Device\MihomeGateway::$musicMap
					),
					'volume' => array(
						'type' => 'integer',
						'minimum' => 0,
						'maximum' => 100,
						'default' => 50
					)
				)
			)), 'application/json', 'playMusic', function($op, $stream, $data, $options){
				
				$data = array_merge(array("music" => 0, "volume" => 50), $data);
				
				if(is_string($data["music"])){
					$data["music"] = array_search($data["music"], \Ething\Device\MihomeGateway::$musicMap);
					if($data["music"] === false) $data["music"] = 0;
				}
				
				$dev = $op->device();
				$cmd = array(
					"cmd" => "write",
					"model" => "gateway",
					"sid" => $dev->sid,
					"short_id" => 0,
					"data" => array(
						"mid" => $data["music"],
						"vol" => $data["volume"]
					)
				);
				return $dev->sendCommand($cmd, $stream, $options);
			}),
			
			new Operation($this, 'stopMusic', null, 'application/json', 'stopMusic', function($op, $stream, $data, $options){
				$dev = $op->device();
				$cmd = array(
					"cmd" => "write",
					"model" => "gateway",
					"sid" => $dev->sid,
					"short_id" => 0,
					"data" => array(
						"mid" => 10000
					)
				);
				return $dev->sendCommand($cmd, $stream, $options);
			})
		);
	}
	
	
	public static function create(Ething $ething, array $attributes, Resource $createdBy = null) {
		return parent::createDevice($ething, array_merge(self::$defaultAttr, $attributes), array(
			'connected' => false,
			'_token' => ''
		), $createdBy);
	}
	
	public function setConnectState($connected) {
		$change = $this->setAttr('connected', boolval($connected));
		$this->update();
		
		if($change){
			$this->dispatchSignal($connected ? \Ething\Event\DeviceConnected::emit($this) : \Ething\Event\DeviceDisconnected::emit($this));
		}
	}
	
	public function getGatewayKey() {
        $encrypt = openssl_encrypt($this->getAttr('_token'), 'AES-128-CBC', $this->password, OPENSSL_RAW_DATA, Mihome::IV);
        $gatewaykey = '';
        for ($i = 0; $i < 16; $i++) {
            $gatewaykey .= sprintf('%02x', ord($encrypt[$i]));
        }

        return $gatewaykey;
    }
	
	public function processData(array $response) {
		
		$this->updateSeenDate();
		
		if(isset($response['token'])){
			$this->setAttr('_token', $response['token']);
		}
		
		$data = \json_decode($response['data'], true);
		
		$attr = array();
		
		if(is_array($data)){
			
			if(isset($data['rgb'])){
				$rgb = $data['rgb'] & 0xffffff;
				$brightness = $data['rgb'] >> 24;
				
				$attr['color'] = '#'.strtoupper(\str_pad(\dechex($rgb), 6, '0', STR_PAD_LEFT));
				$attr['brightness'] = $brightness;
			}
			
			if(isset($data['illumination'])){
				$attr['illumination'] = intval($data['illumination']) - 300; // lm
			}
			
		}
		
		if(isset($data['token'])){
			$attr['token'] = $data['token'];
		}
		
		$this->storeData($attr);
		
		$this->setConnectState(true);
		
		$this->update();
		
	}
	
	public function storeData(array $attr){
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
	
	public function sendCommand(array $cmd, $stream = null, $options = array()){
		return $this->ething->daemon('device.mihome.send '.$this->id().' '.\base64_encode(\json_encode($cmd))."\n", $stream, $options);
	}
	
}



