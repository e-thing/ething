<?php
	

	/**
	 * @swagger-definition
	 * "Device":{ 
	 *   "type": "object",
	 *   "description": "Device resource representation",
	 * 	 "allOf": [
	 * 		{
	 * 		   "$ref":"#/definitions/Resource"
	 * 		},
	 * 		{  
	 * 		   "type": "object",
	 * 		   "properties":{
	 *             "url": {
	 * 		          "type":"string",
	 * 		          "description":"The URL of the device, or null if there is none defined. No URL defined means that the device cannot be reached.
Only device with an URL set has a descriptor object based on the Swagger specification (see /device/<id>/descriptor endpoint).
The descriptor object define all the available HTTP requests this device accepts."
	 * 		       },
	 *             "lastSeenDate": {
	 * 		          "type":"string",
	 * 		          "format":"date-time",
	 * 		          "readOnly": true,
	 * 		          "description":"Last time this device was reached or made a request (formatted RFC 3339 timestamp)."
	 * 		       },
	 *             "battery": {
	 * 		          "type":"number",
	 * 		          "description":"The battery level of this device (must be between 0 (empty) and 100 (full) , or null if the device has no battery information)."
	 * 		       },
	 *             "scope": {
	 * 		          "type":"string",
	 * 		          "enum":["resource","resource.readonly","resource.owndata","notification","profile","profile.readonly"],
	 * 		          "description":"
The allowed scopes for this device (space separated list).
Default to \"resource.owndata notification\".

 - resource: allow to read and write to any resource
 - resource.readonly: allow to read only to any resource
 - resource.owndata: allow this device to create resources and to read/write only those resources
 - notification: allow to send notification
 - profile: allow to edit the profile of this user
 - profile.readonly: allow to see the profile of this user"
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
	 * 		       }
	 * 		   }
	 * 		}
	 *   ]
	 * }
	 */

namespace Ething;


class Device extends Resource
{
	
	const BATTERY_EMPTY = 0;
	const BATTERY_LOW   =  10;
	const BATTERY_HALF  = 50;
	const BATTERY_FULL  = 100;
	
	
	const VALIDATE_URL = '/^(((www\.)?+[a-zA-Z0-9\.\-_]+(\.[a-zA-Z]{2,3})+)|(\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b))(:[0-9]{1,5})?(\/[a-zA-Z0-9_\-\s\.\/\?\%\#\&\=]*)?$/u';
	const VALIDATE_NAME = '/^[a-zA-Z0-9\-.\'_ ]{1,99}$/';
	
	public static $validAuthModes = array('basic', 'digest'); 
	
	public static $defaultAttr = array(
		'url' => null, // the url of the device
		'battery'   => null, // 0-100 : the battery level, if null it means that no battery information is provided
		'scope' => "resource.owndata notification",
		'auth' => null
	);
	
	public function apiKey() {
		return new ApiKey($this->_d['_apiKey']);
	}
	
	public function battery() {
		return isset($this->_d['battery']) ? $this->_d['battery'] : null;
	}
	
	public function url() {
		return $this->_d['url'];
	}
	
	public function isServer() {
		return isset($this->_d['url']);
	}
	
	public function lastSeenDate() {
		return isset($this->_d['lastSeenDate']) ? $this->_d['lastSeenDate']->sec : null;
	}
	
	public function updateSeenDate() {
		$this->_d['lastSeenDate'] = new \MongoDate();
		$this->update(false);
	}
	
	public function scope() {
		return $this->_d['scope'];
	}
	
	public static function validate(Ething $ething, $key,array &$attr,User $user,Resource $self = null) {
		$isConstructor = !isset($self);
		$value = &$attr[$key];
		$ret = false;
		switch($key){
			case 'url':
				if(is_null($value))
					$ret = true;
				else if(is_string($value)){
					// sanitize
					if(!preg_match('/^[a-z]+:\/\//',$value)) // set default schema if not set
						$value = 'http://'.$value;
					// validate
					if(filter_var($value, FILTER_VALIDATE_URL)!==false){
						$scheme = parse_url($value,PHP_URL_SCHEME);
						if(!in_array($scheme,['http','https']))
							throw new Exception("Invalid protocol '${scheme}'. Only http or https accepted.");
						$ret = true;
					}
				}
				break;
			case 'battery':
				if(is_int($value) || is_float($value)){
					if($value<0) $value=0;
					else if($value>100) $value=100;
					
					$ret = ($value < self::BATTERY_LOW) ? function($r) {
						$r->dispatchEvent('LowBatteryDevice');
					} : true;
				}
				else
					$ret = is_null($value);
				break;
			case 'name': // overwride default, only in the root filesystem (ie : no / allowed), no duplicate
				if(is_string($value) && preg_match(self::VALIDATE_NAME, $value)){
					if(!$self || $self->name() != $value){
						// check if a device already have this name
						if($ething->findOne(array(
							'user' => $user->id(),
							'type' => "Device",
							'name' => $value
						)))
							throw new \Ething\Exception('a device already has this name.');
					}
					$ret = true;
				}
				break;
			case 'scope':
				$ret = Scope::valide($value);
				break;
			case 'descriptor':
				if(is_object($value) || is_array($value) || is_null($value) || is_string($value)){
					$descriptor = $value;
					$ret = function($r) use ($descriptor) {
						$r->setDescriptor($descriptor);
					};
				}
				break;
			case 'auth':
				if(is_object($value))
					$value = (array)$value;
				if(is_array($value) && !empty($value['type']) && !empty($value['user']) && !empty($value['password']) && is_string($value['type']) && is_string($value['user']) && is_string($value['password'])){
					$value['type'] = strtolower($value['type']);
					$ret = in_array($value['type'], static::$validAuthModes);
				}
				else if(is_null($value))
					$ret = true;
				break;
			default:
				$ret = parent::validate($ething,$key,$attr,$user,$self);
				break;
			
		}
		return $ret;
	}
	
	public function isAuthenticate() {
		return !empty($this->_d['auth']);
	}
	public function authMode() {
		return $this->isAuthenticate() ? $this->_d['auth']['type'] : null;
	}
	public function authUser() {
		return $this->isAuthenticate() ? $this->_d['auth']['user'] : null;
	}
	public function authPassword() {
		return $this->isAuthenticate() ? $this->_d['auth']['password'] : null;
	}
	
	
	public function forward($path = null, $proxifier = null) {
		if(!$this->isServer())
			return false;
				
		$url = $this->url();
		if(!empty($path)){
			// extract the query string
			$qi = strpos($url,'?');
			$query = '';
			if($qi!==false){
				$query = substr($url,$qi);
				$url = substr_replace($url,'',$qi);
			}
			if(!preg_match('/\/$/',$url))
				$url .= '/';
			$url .= $path;
			// does the path contains a query string ?
			$qi = strpos($path,'?');
			if($qi===false)
				$url .= $query;
			else
				$url .= '&'.substr($query, 1);
		}
		
		if($this->isAuthenticate()){
			$curl_options = array();
			
			switch($this->authMode()){
				case 'basic':
					$curl_options[CURLOPT_HTTPAUTH] = CURLAUTH_BASIC; // The HTTP authentication method(s) to use.
					break;
				case 'digest':
					$curl_options[CURLOPT_HTTPAUTH] = CURLAUTH_DIGEST; // The HTTP authentication method(s) to use.
					break;
				default:
					$curl_options[CURLOPT_HTTPAUTH] = CURLAUTH_ANY; // The HTTP authentication method(s) to use.
					break;
			}
			
			$curl_options[CURLOPT_USERPWD] = $this->authUser().':'.$this->authPassword();
		}
		else
			$curl_options = null;
		
		// throw an error if the connection could not be made
		$device = $this;
		$p = new Proxy($this->getEthingInstance());
		$p->onResponse(function() use ($device){
			// on response
			$device->updateSeenDate();
		});
		
		if(is_callable($proxifier)){
			$p->setUrlProxify(function($url) use ($device,$proxifier){
				
				$url_info = parse_url($url);
				$device_url_info = parse_url($device->url());
				
				$path = '';
				
				if(!empty($device_url_info['path']) && !empty($url_info['path']))
					$path = preg_replace('/^'.preg_quote($device_url_info['path'],'/').'(?=(\?|\#|\/|$))/','',$url_info['path']); // remove the common path
				if(!empty($device_url_info['query']) && !empty($url_info['query'])){
					// remove the common query parameters
					parse_str($device_url_info['query'], $paramsToRemove);
					parse_str($url_info['query'], $params);
					foreach($paramsToRemove as $key => $value){
						unset($params[$key]);
					}
					$path .= '?'.http_build_query($params);
				}
				
				return call_user_func($proxifier, $path, $device);
			});
		}
		
		$p->forward($url, $curl_options);
		
	}
	
	// create a new resource
	public static function create(Ething $ething, User $user, array $attributes, Resource $createdBy = null) {
		return parent::createRessource($ething, $user, array_merge(self::$defaultAttr, $attributes), array(
			'_apiKey' => ApiKey::generate()->data(),
			'lastSeenDate' => null
		), $createdBy);
	}
	
	
	public function setDescriptor($swagger = null) {
		if(!$this->isServer())
			throw new Exception('this device does not allow a descriptor');
		
		// sanitize the descriptor
		if(is_string($swagger)){
			$swagger = json_decode($swagger);
			if(json_last_error() !== JSON_ERROR_NONE){
				throw new Exception('invalid swagger descriptor');
			}
		}
		else if(is_array($swagger))
			$swagger = json_decode(json_encode($swagger)); // cast associative array into object
		
		if(is_object($swagger)){
			if(empty($swagger->swagger))
				$swagger->swagger = '2.0';
			if(!isset($swagger->info))
				$swagger->info = new stdClass();
			if(is_object($swagger->info)){
				if(empty($swagger->info->version))
					$swagger->info->version = "0.0.0";
				if(empty($swagger->info->title) && !empty($defaultTitle))
					$swagger->info->title = $defaultTitle;
			}
			if(!isset($swagger->paths))
				$swagger->paths = new stdClass();
			
			
			// validate the swagger description object
			$url = 'http://online.swagger.io/validator/debug';
			$content = json_encode($swagger);

			//open connection
			$ch = curl_init();

			//set the url, number of POST vars, POST data
			curl_setopt($ch,CURLOPT_URL, $url);
			curl_setopt($ch,CURLOPT_POST, true);
			curl_setopt($ch,CURLOPT_POSTFIELDS, $content);
			curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
			curl_setopt($ch, CURLOPT_HTTPHEADER, array("Content-type: application/json",'Expect:')); // see http://stackoverflow.com/questions/463144/php-http-post-fails-when-curl-data-1024
			curl_setopt ($ch, CURLOPT_FAILONERROR, true);
			
			// proxy
			$proxySettings = $this->getEthingInstance()->config('proxy');
			if(!empty($proxySettings) && !empty($proxySettings['host'])){
				$proxyAddress = $proxySettings['host'];
				if(!empty($proxySettings['port']))
					$proxyAddress .= ':'.$proxySettings['port'];
				curl_setopt($ch, CURLOPT_PROXY, $proxyAddress); // The HTTP proxy to tunnel requests through
				// proxy authentication
				if(!empty($proxySettings['user']) && !empty($proxySettings['password']))
					curl_setopt($ch, CURLOPT_PROXYUSERPWD, $proxySettings['user'].':'.$proxySettings['password']); // A username and password formatted as "[username]:[password]" to use for the connection to the proxy.
			}
					
			//execute post
			$result = curl_exec($ch);
			
			//close connection
			curl_close($ch);
			
			if(!is_string($result))
				throw new Exception('unable to reach http://online.swagger.io/validator/debug',500);
			
			// the response must be valid JSON data containing an array of errors
			$result = json_decode($result,true);
			if(json_last_error()!==JSON_ERROR_NONE || !is_array($result) || !empty($result))
				throw new Exception('invalid swagger description object');

		}
		else if(!is_null($swagger))
			throw new Exception('invalid swagger descriptor');
		
		
		
		
		
		// ok the descriptor is valid or null
		$gridfs = $this->getEthingInstance()->db()->getGridFS();
		if(isset($this->_d['_descriptor'])){
			// remove that file if it exists
			$gridfs->delete($this->_d['_descriptor']);
			unset($this->_d['_descriptor']);
		}
		
		if(isset($swagger)){
			
			$this->_d['_descriptor'] = $gridfs->storeBytes(json_encode($swagger), [
				'filename' => 'Device/'.$this->name().'/descriptor',
				'parent' => $this->id()
			]);
			
		}
		
		$this->update();
		return true;
	}
	
	
	public function getDescriptor() {
		if(!$this->isServer())
			return false;
		$f = isset($this->_d['_descriptor']) ? $this->getEthingInstance()->db()->getGridFS()->get($this->_d['_descriptor']) : null;
		return $f ? json_decode($f->getBytes()) : $this->defaultDescriptor();
	}
	
	protected function defaultDescriptor() {
		// return a minimal swagger object
		$d = new stdClass();
		$d->swagger = '2.0';
		$d->info = new stdClass();
		$d->info->title = "{$this->name()}";
		$d->info->version = '0.1.0';
		$d->paths = new stdClass();
		return $d;
	}
	
	// cf: http://www.php.net/manual/en/function.socket-create.php
	public function ping($timeout = 1) {
		$result = false;
		
		if($this->isServer()){
			
			$url_info = parse_url($this->url());
			
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
			else
				throw new Exception(socket_strerror(socket_last_error()));
			
		}

		return $result;
	}
	
}



