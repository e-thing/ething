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
	 * 		       },
	 *             "reachable": {
	 * 		          "type":"boolean",
	 * 		          "description":"Set to false when the device is unreachable.",
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
use \Ething\Url;
use \Ething\Request;
use \Ething\Stream;
use \Ething\Helpers;
use \Ething\Net;

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
		$cmd = "avconv -rtsp_transport {$this->transport} -i {$this->url} -frames:v 1 -an -f image2 pipe:1 2>/dev/null";
		
		$output = shell_exec($cmd);
		
		$this->setReachableState(!empty($output));
		
		return empty($output) ? false : $output;
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
		
		$this->setReachableState($fp);
		
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
		$cmd = "avprobe -show_format -show_streams -of json {$this->url} 2>/dev/null";
		
		exec($cmd, $output, $returnCode);
		
		$this->setReachableState($returnCode===0);
		
		if($returnCode===0){
			$info = \json_decode(implode('', $output), true);
			return \json_last_error() === JSON_ERROR_NONE ? $info : false;
		}
		
		return false;
	}
	
	public function sendStream($sendHeader = false){
		
		if($sendHeader) header('Content-Type: video/x-flv');
		
		$cmd = "avconv -rtsp_transport {$this->transport} -i {$this->url} -an -c copy -f flv pipe:1";
		
		passthru($cmd, $return_var);
		
		return $return_var==0;
	}
	
	
	public function ping($timeout = 1) {
		
		$url_info = parse_url($this->url);
		
		$result = Net::ping($url_info['host'], $timeout);
		$online = ($result!==false);
		
		$this->setReachableState($online);

		return $result;
	}
	
	protected function setReachableState($reachable){
		
		$change = $this->setAttr('reachable', boolval($reachable));
		
		if($reachable){
			$this->updateSeenDate();
		} else {
			$this->update();
		}
		
		if($change){
			$this->dispatchSignal($reachable ? \Ething\Event\DeviceReachable::emit($this) : \Ething\Event\DeviceUnreachable::emit($this));
		}
		
	}
	
	// create a new resource
	public static function create(Ething $ething, array $attributes, Resource $createdBy = null) {
		return parent::createDevice($ething, array_merge(self::$defaultAttr, $attributes), array(
			'reachable' => false
		), $createdBy);
	}
	
	
	
	
	
	
}



