<?php

	/**
	 * @swagger-definition
	 * "Device\\YeelightBulbRGBW":{ 
	 *   "type": "object",
	 *   "description": "YeelightBulbRGBW Device resource representation",
	 * 	 "allOf": [
	 * 		{
	 * 		   "$ref":"#/definitions/YeelightDevice"
	 * 		}
	 *   ]
	 * }
	 */
	 
namespace Ething\Device;

use \Ething\Exception;
use \Ething\Ething;
use \Ething\Resource;
use \Ething\Helpers;

class YeelightBulbRGBW extends YeelightDevice
{	

	public static $defaultAttr = array();
	
	
	public function storeData(array $state){
		
		if(isset($state['rgb'])){
			$state['color'] = '#'.strtoupper(\str_pad(\dechex($state['rgb']), 6, '0', STR_PAD_LEFT));
		}
		
		if(isset($state['bright'])){
			$state['brightness'] = $state['bright'];
			unset($state['bright']);
		}
		
		parent::storeData($state);
	}
	
	public function operations(){
		return array_merge(parent::operations(), array(
			
			new Operation($this, 'setTemperature', Helpers::array_to_object_recursive(array(
				'type' => 'object',
				'additionalProperties' => false,
				'required' => array('temperature'),
				'properties' => array(
					'temperature' => array(
						"type" => "integer",
						"minimum" => 1700,
						"maximum" => 6500,
						"default" => 5000
					),
					'brightness' => array(
						"type" => "integer",
						"minimum" => 0,
						"maximum" => 100,
						"default" => 100
					)
				)
			)), null, 'turn on the device with the specified temperature', function($op, $stream, $data, $options){
				$data = array_merge(array('temperature'=>5000, 'brightness'=>100), $data);
				return $op->device()->sendMessageWaitResponse('{"id":1,"method":"set_scene", "params":["ct", '.$data['temperature'].', '.$data['brightness'].']}', $stream, $options);
			}),
			
			new Operation($this, 'setColor', Helpers::array_to_object_recursive(array(
				'type' => 'object',
				'additionalProperties' => false,
				'required' => array('color'),
				'properties' => array(
					'color' => array(
						"description" =>  "It should be expressed in hexadecimal, by exemple 0xFFFFFF).",
						"type" => "string",
						"format" => "color",
						"default" => 0x0000FF
					),
					'brightness' => array(
						"type" => "integer",
						"minimum" => 0,
						"maximum" => 100,
						"default" => 100
					)
				)
			)), null, 'turn on the device with the specified color', function($op, $stream, $data, $options){
				$data = array_merge(array('color'=>0x0000FF, 'brightness'=>100), $data);
				if(is_string($data['color'])) // hex ?
					$data['color'] = \hexdec(preg_replace('/^(#|0x)/i', '', $data['color']));
				return $op->device()->sendMessageWaitResponse('{"id":1,"method":"set_scene", "params":["color", '.$data['color'].', '.$data['brightness'].']}', $stream, $options);
			}),
			
			new Operation($this, 'setHSV', Helpers::array_to_object_recursive(array(
				'type' => 'object',
				'additionalProperties' => false,
				'required' => array('hue','saturation'),
				'properties' => array(
					'hue' => array(
						"type" => "integer",
						"minimum" => 0,
						"maximum" => 359,
						"default" => 255
					),
					'saturation' => array(
						"type" => "integer",
						"minimum" => 0,
						"maximum" => 100,
						"default" => 45
					),
					'brightness' => array(
						"type" => "integer",
						"minimum" => 0,
						"maximum" => 100,
						"default" => 100
					)
				)
			)), null, 'turn on the device with the specified color', function($op, $stream, $data, $options){
				$data = array_merge(array('hue'=>255, 'saturation'=>45, 'brightness'=>100), $data);
				return $op->device()->sendMessageWaitResponse('{"id":1,"method":"set_scene", "params":["hsv", '.$data['hue'].', '.$data['saturation'].', '.$data['brightness'].']}', $stream, $options);
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
				$data = array_merge(array('color'=>$op->device()->getData('rgb',0xFFFFFF), 'brightness'=>100), $data);
				return $op->device()->sendMessageWaitResponse('{"id":1,"method":"set_scene", "params":["color", '.$data['color'].', '.$data['brightness'].']}', $stream, $options);
			}),
			
			new Operation($this, 'getStatus', null, 'application/json', 'return the current state', function($op, $stream, $data, $options){
				$stream->sendJSON(boolval(preg_match('/on/i', $op->device()->getData('power','off'))));
				return true;
			}),
			
			new Operation($this, 'getBrightness', null, 'application/json', 'return the brightness (%)', function($op, $stream, $data, $options){
				$stream->sendJSON($op->device()->getData('brightness',0));
				return true;
			}),
			
			new Operation($this, 'getColor', null, 'application/json', 'return the color (hex)', function($op, $stream, $data, $options){
				$stream->sendJSON($op->device()->getData('color','#000000'));
				return true;
			})
			
		));
	}
	
	public static function create(Ething $ething, array $attributes, Resource $createdBy = null) {
		return parent::createYeelightDevice($ething, array_merge(self::$defaultAttr, $attributes), array(), $createdBy);
	}
	
}




