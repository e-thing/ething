<?php
	

	/**
	 * @swagger-definition
	 * "Device\\Http":{ 
	 *   "type": "object",
	 *   "description": "Http Device resource representation",
	 * 	 "allOf": [
	 * 		{
	 * 		   "$ref":"#/definitions/Device"
	 * 		},
	 * 		{  
	 * 		   "type": "object",
	 * 		   "properties":{
	 *             "url": {
	 * 		          "type":"string",
	 * 		          "description":"The URL of the device, or null if there is none defined. No URL defined means that the device cannot be reached.
Only device with an URL set has a Swagger specification (see /device/<id>/specification endpoint).
The specification object define all the available HTTP requests this device accepts."
	 * 		       },
	 *             "scope": {
	 * 		          "type":"string",
	 * 		          "description":"
The allowed scopes for this device (space separated list). Restrict the Http api access.
Default to an empty string (no access).
"
	 * 		       },
	 *             "auth": {
	 *                "type":"object",
	 * 	              "properties":{  
	 * 	              	"type":{
	 * 	              	   "type":"string",
	 * 	              	   "enum":["basic","digest"],
	 * 	              	   "description":"the HTTP authentication method to use."
	 * 	              	},
	 * 	              	"user":{  
	 * 	              	   "type":"string",
	 * 	              	   "description":"the username to use for the authentication."
	 * 	              	},
	 * 	              	"password":{  
	 * 	              	   "type":"string",
	 * 	              	   "description":"the password to use for the authentication."
	 * 	              	}
	 *                },
	 * 		          "description":"An object describing the authentication method to use on HTTP request."
	 * 		       },
	 *             "apikey": {
	 * 		          "type":"string",
	 * 		          "description":"The apikey for authenticating this device.",
	 * 		          "readOnly": true
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

use \Ething\ApiKey;
use \Ething\Exception;
use \Ething\Ething;
use \Ething\Resource;
use \Ething\Event;
use \Ething\Scope;
use \Ething\Url;
use \Ething\Proxy;
use \Ething\Swagger;
use \Ething\Request;
use \Ething\Stream;
use \Ething\Helpers;
use \Ething\Net;

class Http extends Device
{
	
		
	
	
	public static $defaultAttr = array(
		'url' => null, // the url of the device
		'scope' => "",
		'auth' => null
	);
	
	public function apikey() {
		return $this->{'#apikey'};
	}
	
	public function isServer() {
		return isset($this->url);
	}
	
	public static function validate($key, &$value, &$context) {
		$ret = false;
		switch($key){
			case 'url':
				if(is_null($value)){
					$ret = true;
					$context['callbacks'][] = function($r){
						unset($r->_ping);// unset the '_ping' attribute since this device is not in server mode anymore
						$r->set(array(
							'auth' => null,
							'specification' => null
						));
					};
				}
				else if(is_string($value)){
					$ret = Url::validate($value);
				}
				break;
			case 'scope':
				$ret = (is_string($value) && Scope::validate($value)) || is_null($value);
				break;
			case 'specification':
				if(is_object($value) || is_array($value) || is_null($value) || is_string($value)){
					$spec = $value;
					if(!is_null($value)){
						self::checkSwaggerSpecification($context['ething'],$spec); // will throw an exception if an error occurs
					}
					
					$ret = true;
					if(!is_null($spec))
						$context['postfns'][] = function($r) {
							if(!$r->isServer())
								throw new Exception('an API specification cannot be set if the URL property is not set.');
						};
					
					$context['callbacks'][] = function($r) use ($spec) {
						
						$r->ething->fs->removeFile($r->getAttr('_specification'));
						$r->removeAttr('_specification');
						
						if(isset($spec)){
							
							if($spec->info->title=="untitled")
								$spec->info->title=$r->name();
							
							$r->setAttr('_specification', $r->ething->fs->storeFile('Device/'.$r->id().'/specification', json_encode($spec), array(
								'parent' => $r->id()
							)));
							
						}
						
						$r->resetOperations();
					};
				}
				unset($context['config'][$key]);// remove this key
				break;
			case 'auth':
				if(is_object($value))
					$value = (array)$value;
				if(is_array($value) && !empty($value['type']) && !empty($value['user']) && !empty($value['password']) && is_string($value['type']) && is_string($value['user']) && is_string($value['password'])){
					
					$authMode = strtolower($value['type']);
					$authUser = $value['user'];
					$authPwd = $value['password'];
					
					if($ret = in_array($authMode, Request::$validAuthModes)){
						$value = array(
							'type' => $authMode,
							'user' => $authUser,
							'password' => $authPwd
						);
						$context['postfns'][] = function($r) {
							if(!$r->isServer())
								throw new Exception('authentication is only available if the URL property is set.');
						};
					}
				}
				else if(is_null($value))
					$ret = true;
				break;
			default:
				$ret = parent::validate($key,$value,$context);
				break;
			
		}
		return $ret;
	}
	
	public function isAuthenticate() {
		return $this->hasAttr('auth');
	}
	public function authMode() {
		return $this->isAuthenticate() ? $this->getAttr('auth')['type'] : null;
	}
	public function authUser() {
		return $this->isAuthenticate() ? $this->getAttr('auth')['user'] : null;
	}
	public function authPassword() {
		return $this->isAuthenticate() ? $this->getAttr('auth')['password'] : null;
	}
	
	
	
	
	
	public function operations(){
		if(!$this->isServer())
			return array(); // this device is not accessible
		
		// parse the swagger specification
		$swagger = new Swagger\Client($this->getSpecification());
		$device = $this;
			
		$operations = array_map(function($swaggerOperation) use($device){
			
			$schema = null;
		
			if($swaggerOperation->parameters()){
				$schema = new \stdClass();
				$schema->type = 'object';
				$schema->required = array();
				$schema->additionalProperties = false;
				$schema->properties = new \stdClass();
				foreach( $swaggerOperation->parameters() as $swaggerParam){
					$schema->properties->{$swaggerParam->name()} = $swaggerParam->toJsonSchema();
					if($swaggerParam->isRequired())
						$schema->required[] = $swaggerParam->name();
				}
			}
			
			$response = null;
			$produces = $swaggerOperation->produces();
			if(count($produces))
				$response = $produces[0];
			
			return new HttpOperation($device, $swaggerOperation->name(), $schema, $response, $swaggerOperation->description());
		}, $swagger->operations());
		
		
		// add custom request
		$operations[] = new Operation($this, 'custom request', Helpers::array_to_object_recursive(array(
			'type' => 'object',
			'additionalProperties' => false,
			'required' => array('path', 'method'),
			'properties' => array(
				'method' => array(
					'enum' => array_map('strtoupper', Request::$validMethodes),
					'default' => "GET"
				),
				'path' => array(
					'type' => 'string'
				),
				'headers' => array(
					'type' => 'array',
					'items' => array(
						"type" => "object",
						'additionalProperties' => false,
						'required' => array('key', 'value'),
						'properties' => array(
							'key' => array(
								"type" => "string",
								'minLength' => 1
							),
							'value' => array(
								"type" => "string",
								'minLength' => 1
							)
						)
					)
				),
				'body' => array(
					'type' => 'string',
					'format' => 'binary'
				)
			)
		)), null, 'send a custom http request', function($op, $stream, $data, $options){
			
			// defaults
			$data = array_merge(
				array(
					'path' => '',
					'method' => 'GET',
					'headers' => array(),
					'body' => ''
				), $data
			);
			
			return $op->device()->request($data['path'], $data['method'], $data['headers'], $data['body'], $stream, $options);
		}); 
		
		
		$host = parse_url($this->url)['host'];
		
		if(!Net::isLocalhost($host)){
			$operations[] = new Operation($this, 'ping', null, 'application/json', 'send ping request', function($op, $stream, $data, $options){
				$device = $op->device();
				$host = parse_url($device->url)['host'];
				return $op->ething()->daemon('net.ping --host '.$host, $stream, $options);
			});
			
			
			if(Net::isLocalIp($host)){
				$operations[] = new Operation($this, 'wol', null, null, 'send Wake on Lan packet', function($op, $stream, $data, $options){
					$device = $op->device();
					$host = parse_url($device->url)['host'];
					return $op->ething()->daemon('net.wol --ip '.$host, $stream, $options);
				});
			}
		}
		
		return $operations;
	}
	
	
	
	public function request($path = '', $method = 'GET', array $headers = array(), $body = '', $stream = null, $options = array()){
		
		if(!$this->isServer())
			throw new Exception("this device is not accessible");
		
		// build the url
		$url = new Url($this->url);
		
		$partToUpdate = parse_url($path);
		if(!empty($partToUpdate['path'])){
			// check the path does not contains any .. parts
			if(preg_match('/(\/|^)\.\.([\/?#]|$)/',$partToUpdate['path']))
				throw new Exception("Invalid path (must not contain any ..)");
			// append the path
			$url->concatPath($partToUpdate['path']);
		}
		// insert the query parameters
		if(!empty($partToUpdate['query'])){
			parse_str($partToUpdate['query'], $params);
			foreach($params as $name => $value){
				$currentValue = $url->getParam($name);
				if(isset($currentValue) && $currentValue !== $value ){
					// we got a problem here, there is already a parameter with this value in the registered URL
					// it is forbidden to overwrite it !
					throw new Exception("The parameter {$name} cannot be overwritten");
				}
				$url->insertParam($name, $value);
			}
		}
		
		// build the request
		$request = new Request($url, $method, $headers, $body);
		
		
		// send the request
		$device = $this;
		$proxy = new Proxy($this->ething);
		$proxy->onResponse(function() use ($device){
			// on response
			$device->setReachableState(true);
		});
		$curl_options = array();
		if(isset($options['timeout']))
			$curl_options[CURLOPT_TIMEOUT] = $options['timeout'];
		$response = $proxy->request($request, $stream, $this->authUser(), $this->authPassword(), $this->authMode(), $curl_options);
		
		if(!$response) $this->setReachableState(false); // host not reachable
		
		return $response;
	}
	
	public function ping($timeout = 1) {
		
		if(!$this->isServer()) return false;
		
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
			'#apikey' => ApiKey::generate(),
			'reachable' => false
		), $createdBy);
	}
	
	
	
	/*
	swagger specification 
	*/
	
	public static function checkSwaggerSpecification(Ething $ething, &$swagger, $defaultTitle = null){
		
		// sanitize the specification
		if(is_string($swagger)){
			$swagger = json_decode($swagger);
			if(json_last_error() !== JSON_ERROR_NONE){
				throw new Exception('invalid swagger API specification');
			}
		}
		else if(is_array($swagger))
			$swagger = json_decode(json_encode($swagger)); // cast associative array into object
		
		if(is_object($swagger)){
			if(empty($swagger->swagger))
				$swagger->swagger = '2.0';
			if(!isset($swagger->info))
				$swagger->info = new \stdClass();
			if(is_object($swagger->info)){
				if(empty($swagger->info->version))
					$swagger->info->version = "unversioned";
				if(empty($swagger->info->title))
					$swagger->info->title = empty($defaultTitle) ? "untitled" : $defaultTitle;
			}
			if(!isset($swagger->paths))
				$swagger->paths = new \stdClass();
			
			
			
			$response = Proxy::post($ething, 'http://online.swagger.io/validator/debug', json_encode($swagger), array("Content-type" => "application/json", "Expect" => ""));
			
			if(!$response || !$response->isSuccessful())
				throw new Exception('unable to reach http://online.swagger.io/validator/debug',500);
			
			// the response must be valid JSON data containing an array of errors
			$result = json_decode($response->body,true);
			if(json_last_error()!==JSON_ERROR_NONE || !is_array($result) || !empty($result)){
				$message = is_array($result) && !empty($result['schemaValidationMessages']) ? $result['schemaValidationMessages'][0]['message'] : 'unknown error';
				throw new Exception('invalid swagger API specification: '.$message);
			}

		}
		else
			throw new Exception('invalid swagger API specification');
		
		return true;
	}
	
	
	public function setSpecification($swagger = null) {
		return $this->set('specification',$swagger);
	}
	
	
	public function getSpecification() {
		if(!$this->isServer())
			throw new Exception('this device has no API specification');
		$spec = $this->ething->fs->retrieveFile($this->getAttr('_specification'));
		return $spec ? json_decode($spec) : $this->defaultSpecification();
	}
	
	protected function defaultSpecification() {
		// return a minimal swagger object
		$d = new \stdClass();
		$d->swagger = '2.0';
		$d->info = new \stdClass();
		$d->info->title = $this->name();
		$d->info->version = '0.1.0';
		$d->paths = new \stdClass();
		return $d;
	}
	
	
	
	
	
	
}



