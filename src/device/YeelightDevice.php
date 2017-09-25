<?php

	/**
	 * @swagger-definition
	 * "Device\\YeelightDevice":{ 
	 *   "type": "object",
	 *   "description": "YeelightDevice Device resource representation",
	 * 	 "allOf": [
	 * 		{
	 * 		   "$ref":"#/definitions/Device"
	 * 		},
	 * 		{  
	 * 		   "type": "object",
	 * 		   "properties":{
	 *             "host": {
	 * 		          "type":"string",
	 * 		          "description":"The ip address of the device to connect to."
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
use \Ething\Url;
use \Ething\Proxy;
use \Ething\Request;
use \Ething\Response;
use \Ething\Stream;
use \Ething\Helpers;
use \Ething\Net;




abstract class YeelightDevice extends Device
{	

	
	public static $defaultAttr = array(
		'host' => null
	);
	
	
	public static function validate($key, &$value, &$context) {
		$ret = false;
		switch($key){
			case 'host':
				if(is_string($value) && !empty($value)){
					
					$validIpAddressRegex = '/^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$/';
					$validHostnameRegex = '/^(([a-zA-Z]|[a-zA-Z][a-zA-Z0-9\-]*[a-zA-Z0-9])\.)*([A-Za-z]|[A-Za-z][A-Za-z0-9\-]*[A-Za-z0-9])$/';
					
					if(preg_match($validIpAddressRegex, $value) || preg_match($validHostnameRegex, $value)){
						$ret = true;
					}
					
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
			new Operation($this, 'off', null, null, 'turn off the device', function($op, $stream, $data, $options){
				return $op->device()->sendMessageWaitResponse('{"id":1,"method":"set_power", "params":["off", "smooth", 500]}', $stream, $options);
			}),
			new Operation($this, 'on', null, null, 'turn on the device', function($op, $stream, $data, $options){
				return $op->device()->sendMessageWaitResponse('{"id":1,"method":"set_power", "params":["on", "smooth", 500]}', $stream, $options);
			})
			
		);
	}
	
	
	public function storeData(array $state){
		if(!empty($state)){
			$this->setData($state);
			$this->dispatchSignal(\Ething\Event\DeviceDataSet::emit($this, (object)$state));
		}
	}
	
	/*public function sendMessage($message, $stream = null){
		$fp = fsockopen($this->host, 55443, $errno, $errstr, 5);
		if (!$fp) {
			$stream->close(400, "{$errstr} ({$errno})");
			return false;
		} else {
			socket_set_timeout($fp,5);
			fwrite($fp, $message."\r\n");
			while (!feof($fp)) {
				$str = fgets($fp, 128);
				if(is_string($str)) $stream->out($str);
				if($str === false || strlen($str) != 128) break;
			}
			fclose($fp);
			$stream->close();
			return true;
		}
	}*/
	
	protected static function createYeelightDevice(Ething $ething, array $attributes, array $meta = array(), Resource $createdBy = null) {
		return parent::createDevice($ething, array_merge(self::$defaultAttr, $attributes), $meta, $createdBy);
	}
	
	
	public function ping($timeout = 1) {
		
		$result = Net::ping($this->host, $timeout);
		$online = ($result!==false);
		$previousState = boolval($this->getAttr('_ping'));
		if($previousState != $online){
			// the state changed
			if(!$online){
				// this device has been disconnected !
				$this->dispatchSignal(\Ething\Event\DeviceUnreachable::emit($this));
			}
			$this->setAttr('_ping', $online);
		}
		
		if($online){
			$this->updateSeenDate();
		}

		return $result;
	}
	
	public function sendMessage($message, $stream = null, $options = array()){
		if(is_array($message)) $message = \json_encode($message);
		return $this->ething->daemon('device.yeelight.send '.$this->id().' '.\base64_encode($message)."\n", $stream, $options);
	}
	
	// send a message and wait for the response.
	// note: not all request has a response !
	public function sendMessageWaitResponse($message, $stream = null, $options = array()){
		if(is_array($message)) $message = \json_encode($message);
		return $this->ething->daemon('device.yeelight.sendWaitResponse '.$this->id().' '.\base64_encode($message)."\n", $stream, $options);
	}
	
}



