<?php


namespace Ething\Device;

use \Ething\Exception;
use \Ething\Ething;
use \Ething\Resource;
use \Ething\Helpers;

class YeelightBulbRGBW extends YeelightDevice
{	

	public static $defaultAttr = array();
	
	
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
						"description" =>  "It should be expressed in decimal integer ranges from 0 to 16777215 (hex: 0xFFFFFF).",
						"type" => "integer",
						"minimum" => 0,
						"maximum" => 16777215,
						"default" => 65280
					),
					'brightness' => array(
						"type" => "integer",
						"minimum" => 0,
						"maximum" => 100,
						"default" => 100
					)
				)
			)), null, 'turn on the device with the specified color', function($op, $stream, $data, $options){
				$data = array_merge(array('color'=>65280, 'brightness'=>100), $data);
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
			})
			
		));
	}
	
	public static function create(Ething $ething, array $attributes, Resource $createdBy = null) {
		return parent::createYeelightDevice($ething, array_merge(self::$defaultAttr, $attributes), array(), $createdBy);
	}
	
}




