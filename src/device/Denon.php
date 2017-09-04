<?php
	

	/**
	 * @swagger-definition
	 * "Device\\Denon":{ 
	 *   "type": "object",
	 *   "description": "Denon or Marantz device representation",
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

class Denon extends Device
{
	
		
	
	
	public static $defaultAttr = array(
		'host' => null // the ip address
	);
	
	
	public static function validate($key, &$value, &$context) {
		$ret = false;
		switch($key){
			case 'host':
				
				if(!is_string($value) || !\filter_var($value, FILTER_VALIDATE_IP))
					throw new Exception('Not a valid IP address');
				
				$ret = true;
				
				break;
			default:
				$ret = parent::validate($key,$value,$context);
				break;
			
		}
		return $ret;
	}
	
	
	
	
	public function operations(){
		return array(
			new Operation($this, 'powerOn', null, null, 'power on the device', function($op, $stream, $data, $options){
				return $op->device()->sendCmd('PWON');
			}),
			new Operation($this, 'powerOff', null, null, 'power off the device', function($op, $stream, $data, $options){
				return $op->device()->sendCmd('PWSTANDBY');
			}),
			new Operation($this, 'setVolumeUp', null, null, 'turn up the volume', function($op, $stream, $data, $options){
				return $op->device()->sendCmd('MVUP');
			}),
			new Operation($this, 'setVolumeDown', null, null, 'turn down the volume', function($op, $stream, $data, $options){
				return $op->device()->sendCmd('MVDOWN');
			}),
			new Operation($this, 'setSource', Helpers::array_to_object_recursive(array(
				'type' => 'object',
				'additionalProperties' => false,
				'required' => array('src'),
				'properties' => array(
					'src' => array(
						"enum" => [ "CD", "TUNER", "IRADIO", "IPD" ]
					)
				)
			)), null, 'select the source', function($op, $stream, $data, $options){
				return $op->device()->sendCmd('SI'.$data['src']);
			}),
			new Operation($this, 'getNetCover', null, 'image/jpg', 'get the radio cover', function($op, $stream, $data, $options){
				return $op->device()->getNetCover($stream);
			}),
			new Operation($this, 'getStatus', null, 'application/json', 'return the device status', function($op, $stream, $data, $options){
				$stream->out($op->device()->getDeviceStatus());
				return true;
			}),
			new Operation($this, 'getNetAudioStatus', null, 'application/json', 'return the device NET status', function($op, $stream, $data, $options){
				return $op->device()->sendPostCmd('GetNetAudioStatus', null, $stream);
			}),
			new Operation($this, 'getCDStatus', null, 'application/json', 'return the device CD status', function($op, $stream, $data, $options){
				return $op->device()->sendPostCmd('GetCDStatus', null, $stream);
			}),
			new Operation($this, 'setCDControl', Helpers::array_to_object_recursive(array(
				'type' => 'object',
				'additionalProperties' => false,
				'required' => array('cmd'),
				'properties' => array(
					'cmd' => array(
						"enum" => [ "STOP", "PLAY", "PAUSE", "PREV_TRACK", "NEXT_TRACK" ]
					)
				)
			)), null, 'control the CD player', function($op, $stream, $data, $options){
				$cntrl = array(
					"STOP"=>'00', "PLAY"=>'01', "PAUSE"=>'02', "PREV_TRACK"=>'05', "NEXT_TRACK"=>'06'
				);
				return (isset($data['cmd']) && array_key_exists($data['cmd'], $cntrl)) ? $op->device()->sendPostCmd('SetCDControl', $cntrl[$data['cmd']]) : false;
			}),
			// generic
			new Operation($this, 'sendCmd', Helpers::array_to_object_recursive(array(
				'type' => 'object',
				'additionalProperties' => false,
				'required' => array('cmd'),
				'properties' => array(
					'cmd' => array(
						"type" => "string"
					)
				)
			)), null, 'send a command through formiPhoneAppDirect.xml', function($op, $stream, $data, $options){
				return $op->device()->sendCmd($data['cmd']);
			}),
			new Operation($this, 'sendCmd2', Helpers::array_to_object_recursive(array(
				'type' => 'object',
				'additionalProperties' => false,
				'required' => array('cmd'),
				'properties' => array(
					'cmd' => array(
						"type" => "string"
					),
					'value' => array(
						"type" => "string"
					)
				)
			)), 'text/xml', 'send a command through AppCommand.xml', function($op, $stream, $data, $options){
				$data = array_merge(array('cmd'=>null, 'value'=>null), $data);
				return $op->device()->sendPostCmd($data['cmd'], $data['value'], $stream);
			})
		);
	}
	
	// rien d'interessant ... a part le nom du modele
	public function getDeviceInfo(){
		
		$url = new Url('http://'.$this->host);
		$url->concatPath('/goform/Deviceinfo.xml');
		
		$response = Proxy::get($this->ething, $url);
		
		if($response->isSuccessful()){
			
			$deviceInfo = new \SimpleXMLElement($response->body);
			
			return array(
				'model' => $deviceInfo->ModelName,
				'macAddress' => $deviceInfo->MacAddress
			);
		}
		
		return false;
	}
	
	
	public function getDeviceStatus(){
		
		$url = new Url('http://'.$this->host);
		$url->concatPath('/goform/formMainZone_MainZoneXmlStatus.xml');
		
		$response = Proxy::get($this->ething, $url);
		
		if($response->isSuccessful()){
			
			$xml = new \SimpleXMLElement($response->body);
			
			return array(
				'power' => strtoupper($xml->Power->value) === 'ON',
				'input' => strval($xml->InputFuncSelect->value),
				'volume' => intval($xml->MasterVolume->value),
				'mute' => strtoupper($xml->Mute->value) === 'ON'
			);
		}
		
		return false;
	}
	
	
	public function setMute($mute){
		$url = new Url('http://'.$this->host);
		$url->concatPath('/goform/formiPhoneAppMute.xml?1+Mute'.($mute?'ON':'OFF'));
		
		$response = Proxy::get($this->ething, $url);
		
		return $response->isSuccessful();
	}
	
	public function turnOnOff($on){
		$url = new Url('http://'.$this->host);
		$url->concatPath('/goform/formiPhoneAppPower.xml?1+Power'.($on?'On':'Standby'));
		
		$response = Proxy::get($this->ething, $url);
		
		return $response->isSuccessful();
	}
	
	public function getNetCover($stream){
		$url = new Url('http://'.$this->host);
		$url->concatPath('/NetAudio/art.asp-jpg');
		
		$response = Proxy::get($this->ething, $url, $stream);
		
		return $response->isSuccessful();
	}
	
	
	/*
	 working cmd for marantz M-CR611 :
	 
	 PWON
	 PWSTANDBY
     
	 MVUP
	 MVDOWN
	 MV00 // min = mute
	 MV08  
	 MV20 // loud
	 ...
     
	 MUON // mute
	 MUOFF
     
	 SICD // CD
	 SITUNER // DAB
	 SIIRADIO // internet radio
	 SISERVER // music server
	 SIUSB // front usb
	 SIIPD // front usb start playback
	 
	*/
	public function sendCmd($cmd, $stream = null){
		$url = new Url('http://'.$this->host);
		$url->concatPath('/goform/formiPhoneAppDirect.xml?'.$cmd);
		
		$response = Proxy::get($this->ething, $url, $stream);
		
		return $response->isSuccessful();
	}
	
	/*
	GetSourceStatus
	GetAllZonePowerStatus
	GetVolumeLevel
	GetMuteStatus
	GetZoneName
	GetNetAudioStatus
	GetSurroundModeStatus
	GetCDStatus
	
	SetCDControl value: 00 , 01 play, 05 prev, 06 next
	*/
	public function sendPostCmd($cmd, $value = null, $stream = null){
		$url = new Url('http://'.$this->host);
		$url->concatPath('/goform/AppCommand.xml');
		
		$body = '<?xml version="1.0" encoding="utf-8" ?>';
		$body .= '<tx>';
		$body .= '<cmd id="1">';
		$body .= $cmd;
		$body .= '</cmd>';
		if(isset($value)){
			$body .= '<value>';
			$body .= $value;
			$body .= '</value>';
		}
		$body .= '</tx>';
		
		$response = Proxy::post($this->ething, $url, $body, array(), $stream);
		
	}
	
	
	
	
	
	// cf: http://www.php.net/manual/en/function.socket-create.php
	public function ping($timeout = 1) {
		$result = false;
			
		$url_info = parse_url($this->host);
		
		/* ICMP ping packet with a pre-calculated checksum */
		$package = "\x08\x00\x7d\x4b\x00\x00\x00\x00PingHost";
		/* create the socket, the last '1' denotes ICMP */
		if($socket  = @socket_create(AF_INET, SOCK_RAW, 1)){
			/* set socket receive timeout to 1 second */
			socket_set_option($socket, SOL_SOCKET, SO_RCVTIMEO, array('sec' => $timeout, 'usec' => 0));
			
			/* connect to socket */
			if(@socket_connect($socket, $url_info['host'], null)){
				$ts = microtime(true);
				if (@socket_send($socket, $package, strLen($package), 0) && @socket_read($socket, 255))
					$result = microtime(true) - $ts;
			}
			
			socket_close($socket);
		}
		else{
			$e = new Exception(socket_strerror(socket_last_error()));
			$this->ething->logger()->error($e);
			throw $e;
		}
		
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
	
	
	
	
	
	
	// create a new resource
	public static function create(Ething $ething, array $attributes, Resource $createdBy = null) {
		return parent::createDevice($ething, array_merge(self::$defaultAttr, $attributes), array(), $createdBy);
	}
	
	
	
}



