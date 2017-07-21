<?php
	

	/**
	 * @swagger-definition
	 * "RTSP":{ 
	 *   "type": "object",
	 *   "description": "RTSP Device resource representation, usually IP camera",
	 * 	 "allOf": [
	 * 		{
	 * 		   "$ref":"#/definitions/Device"
	 * 		},
	 * 		{  
	 * 		   "type": "object",
	 * 		   "properties":{
	 *             "url": {
	 * 		          "type":"string",
	 * 		          "description":"The URL of the device rtsp://... ."
	 * 		       },
	 *             "transport": {
	 * 		          "type":"string",
	 * 		          "description": "Lower transport protocol. Allowed values are the ones defined for the flags for rtsp_transport (see https://libav.org/avconv.html).",
	 * 		          "enum":["tcp","udp","http"]
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
use \Ething\Request;
use \Ething\Stream;
use \Ething\Helpers;

class RTSP extends Device
{	
	
	public static $validTransports = array('udp','tcp','http');
	
	public static $defaultAttr = array(
		'url' => null, // the url of the device
		'transport' => "tcp"
	);
	
	
	public static function validate($key, &$value, &$context) {
		$ret = false;
		switch($key){
			case 'url':
				if(is_string($value) && !empty($value)){
					
					$url = new Url($value, array(
						'scheme' => 'rtsp'
					));
					
					if($url->scheme !== 'rtsp'){
						throw new Exception('only rtsp protocol is allowed.');
					}
					
					$value = (string)$url;
					
					$ret = true;
				}
				break;
			case 'transport':
				if(!is_string($value) || !in_array($value, static::$validTransports))
					throw new Exception('invalid transport, must be one of the following '.implode(',', static::$validTransports));
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
			new Operation($this, 'snapshot', null, 'image/jpeg', 'get a snapshot', function($op, $stream, $data, $options){
					$img = $op->device()->snapshot();
					if(!$img) return false;
					$stream->contentType('image/jpeg');
					$stream->out($img);
					return true;
				}),
			/*new Operation($this, 'stream', Helpers::array_to_object_recursive(array(
					'type' => 'object',
					'additionalProperties' => false,
					'properties' => array(
						'duration' => array(
							'type' => 'integer',
							'minimum' => 0,
							'maximum' => 3600
						)
					)
				)), 'video/x-flv', 'return a video stream (flv)', function($op, $stream, $data, $options){
					//return $op->device()->sendStream(true);
					$data = array_merge(array('duration'=>0), $data);
					return $op->device()->stream($stream, 'flv', $data['duration']);
				}),*/
			new Operation($this, 'stream', Helpers::array_to_object_recursive(array(
					'type' => 'object',
					'additionalProperties' => false,
					'properties' => array(
						'duration' => array(
							'type' => 'integer',
							'minimum' => 0,
							'maximum' => 3600
						)
					)
				)), 'video/mp4', 'return a video stream (mp4)', function($op, $stream, $data, $options){
					$data = array_merge(array('duration'=>0), $data);
					return $op->device()->stream($stream, 'mp4', $data['duration']);
				}),
			new Operation($this, 'info', null, 'application/json', 'return information about the stream', function($op, $stream, $data, $options){
					$info = $op->device()->streamInfo();
					if(!$info) return false;
					$stream->out($info);
					return true;
				})
		);
	}
	
	
	public function snapshot(){
		$cmd = "avconv -rtsp_transport {$this->transport} -i {$this->url} -frames:v 1 -an -f image2 pipe:1";
		
		$output = shell_exec($cmd);
		
		if(empty($output)){
			return false;
		} else {
			$this->updateSeenDate();
			return $output;
		}
	}
	
	public function stream(Stream $stream, $format = 'flv', $duration = 0){
		
		$cmd = "avconv -rtsp_transport {$this->transport} -i {$this->url} -an ";
		
		switch($format){
			case 'flv':
				$cmd .= "-c copy -f flv";
				$contentType = 'video/x-flv';
				break;
			case 'mp4':
				$cmd .= "-c copy -f mp4 -movflags frag_keyframe+empty_moov";
				$contentType = 'video/mp4';
				break;
			default:
				throw new Exception("unknown format = {$format}");
		}
		
		if(!empty($duration) && is_numeric($duration) && intval($duration)>0)
			$cmd .= " -t {$duration}";
		
		$cmd .= " pipe:1";
		
		$fp = popen($cmd, "r");
		
		if(!$fp) return false;
		
		$stream->contentType($contentType);
		
		while(!feof($fp)) 
		{ 
			$stream->out(fread($fp, 1024));
		}
		
		pclose($fp); 
		
		return true;
	}
	
	public function streamInfo(){
		$cmd = "avprobe -show_format -show_streams -of json {$this->url}";
		
		$output = shell_exec($cmd);
		
		if(empty($output)){
			return false;
		} else {
			$info = \json_decode($output, true);
			return \json_last_error() === JSON_ERROR_NONE ? $info : false;
		}
	}
	
	public function sendStream($sendHeader = false){
		
		if($sendHeader) header('Content-Type: video/x-flv');
		
		$cmd = "avconv -rtsp_transport {$this->transport} -i {$this->url} -an -c copy -f flv pipe:1";
		
		passthru($cmd, $return_var);
		
		return $return_var==0;
	}
	
	
	// cf: http://www.php.net/manual/en/function.socket-create.php
	public function ping($timeout = 1) {
		$result = false;
		
		$url_info = parse_url($this->url);
		
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
			$this->ething->log($e);
			throw $e;
		}
			
		
		$online = ($result!==false);
		$previousState = boolval($this->getAttr('_ping'));
		if($previousState != $online){
			// the state changed
			if(!$online){
				// this device has been disconnected !
				$device->dispatchSignal(Event\DeviceUnreachable::emit($device));
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



