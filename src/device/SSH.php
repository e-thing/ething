<?php
	

	/**
	 * @swagger-definition
	 * "Device\\SSH":{ 
	 *   "type": "object",
	 *   "description": "SSH Device resource representation",
	 * 	 "allOf": [
	 * 		{
	 * 		   "$ref":"#/definitions/Device"
	 * 		},
	 * 		{  
	 * 		   "type": "object",
	 * 		   "properties":{
	 *             "host": {
	 * 		          "type":"string",
	 * 		          "description":"The ip address or hostname of the device to connect to."
	 * 		       },
	 *             "port": {
	 * 		          "type":"number",
	 * 		          "description":"The port number of the device to connect to. The default port number is 22."
	 * 		       },
	 *             "auth": {
	 *                "type":"object",
	 * 	              "properties":{  
	 * 	              	"user":{  
	 * 	              	   "type":"string",
	 * 	              	   "description":"the username to use for the authentication."
	 * 	              	},
	 * 	              	"password":{  
	 * 	              	   "type":"string",
	 * 	              	   "description":"the password to use for the authentication."
	 * 	              	}
	 *                },
	 * 		          "description":"An object describing the credentials to use."
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
use \Ething\Event;
use \Ething\Stream;
use \Ething\Helpers;
use \Ething\Net;

class SSH extends Device
{
	
		
	
	
	public static $defaultAttr = array(
		'host' => null, // the url of the device
		'port' => 22,
		'auth' => null
	);
	
	public static function validate($key, &$value, &$context) {
		$ret = false;
		switch($key){
			case 'host':
				if(is_string($value) && !empty($value)){
					$ret = true;
				}
				break;
			case 'port':
				if(is_int($value) && $value>=0 && $value<= 65535){
					$ret = true;
				}
				break;
			case 'auth': // mandatory
				if(is_object($value))
					$value = (array)$value;
				if(is_array($value) && !empty($value['user']) && !empty($value['password']) && is_string($value['user']) && is_string($value['password'])){
					$ret = true;
					
					$authUser = $value['user'];
					$authPwd = $value['password'];
					
					$value = array(
						'user' => $authUser,
						'password' => $authPwd
					);
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
			new Operation($this, 'execute', Helpers::array_to_object_recursive(array(
					'type' => 'object',
					'additionalProperties' => false,
					'required' => array('command'),
					'properties' => array(
						'command' => array(
							'type' => 'string',
							"minLength" => 1
						)
					)
				)), 'text/plain', 'execute a command.', function($op, $stream, $data, $options){
					$data = array_merge(array(
						'command' => ''
					), $data);
					return $op->device()->execute($data['command'], $stream, $options);
				})
		);
	}
	
	public function execute($commands, Stream $stream = null, $options = array()){
		
		if(extension_loaded('ssh2')){
			$connection = \ssh2_connect($this->host, $this->port);
			if($connection) {
				if(\ssh2_auth_password($connection, $this->auth['user'], $this->auth['password'])){
					
					if(is_string($commands)) $commands = array($commands);
					
					if(is_array($commands)){
						
						foreach($commands as $cmd){
							$stdout_stream = \ssh2_exec($connection, $cmd);
							
							stream_set_blocking($stdout_stream, true);
							$result = stream_get_contents($stdout_stream);
							
							/*$err_stream = \ssh2_fetch_stream($stdout_stream, SSH2_STREAM_STDERR);
							$dio_stream = \ssh2_fetch_stream($stdout_stream, SSH2_STREAM_STDDIO);
							
							stream_set_blocking($err_stream, true);
							stream_set_blocking($dio_stream, true);
							
							$result_err = stream_get_contents($err_stream);
							$result_dio = stream_get_contents($dio_stream);*/
							
							if($stream) {
								$stream->out($result, Stream::STDOUT);
							}
						}
						
						$closesession = \ssh2_exec($connection, 'exit');
						stream_set_blocking($closesession, true);
						stream_get_contents($closesession);
						
						$stream->close();
						
						return true;
					}
					
				} else {
					if($stream) $stream->close(401, 'bad authentication');
				}
			} else {
				if($stream) $stream->close(400, 'unable to connect');
			}
		} else {
			if($stream) $stream->close(400, 'ssh2 is not installed');
		}
		return false;
	}
	
	public function ping($timeout = 1) {
		
		$result = Net::ping($this->host, $timeout);
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



