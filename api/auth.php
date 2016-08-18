<?php
/**
 * HTTP Basic Authentication
 */
namespace Auth;




class HttpAuth extends \Slim\Middleware
{
	private $_ething = null;
	private $_user = null;
	private $_device = null;
	private $_fs = null;
	private $_mode = 'unauthenticated';
	
	private $_opt = array(
		'secret' => 'taupesecretstring',
		'expiration' => 86400 // in seconds, the time after wich the token is expired
	);
	
	public function __construct(\Ething\Ething $ething, array $options = array())
    {
        $this->_ething = $ething;
		$this->_opt = array_replace_recursive($this->_opt, $options);
    }
	
	
	private static $noRestrictedResourceUri = array(
		'POST' => array('/auth/authorize','/user'),
		'GET' => array('/swagger.json')
	);
	
	private static $scopeMap = array(
		'#^/(resources|file|table|app|device|usage)(/|$)#' => array(
				'GET' => \Ething\Scope::RESOURCE_READ,
				'*' => \Ething\Scope::RESOURCE_WRITE
			),
		'#^/profile(/|$)#' => array(
				'GET' => \Ething\Scope::PROFILE_READ,
				'*' => \Ething\Scope::PROFILE_WRITE
			),
		'#^/notification(/|$)#' => array('*' => \Ething\Scope::NOTIFICATION)
	);
	
	
	
	public function user() {
		return $this->_user;
	}
	
	public function device() {
		return $this->_device;
	}
	
	public function fs() {
		return $this->_fs;
	}
	
	public function isAuthenticated() {
		return !is_null($this->_user);
	}
	
	// 'unauthenticated' , 'api' , 'token' or 'apikey'
	public function mode(){
		return $this->_mode;
	}
	
	public function authenticate(\Ething\User $user = null){
		if($user){
			$this->_mode = 'api';
			$this->_user = $user;
			$this->_fs = new \Ething\Fs($this->_ething,$user);
		}
		else {
			$this->_mode = 'unauthenticated';
			$this->_user = null;
			$this->_fs = null;
			$this->_device = null;
		}
	}
	
	public function generateToken(){
		$issuedAt   = time();
		return $this->isAuthenticated() ? 
			\Firebase\JWT\JWT::encode(array(
				'iat' => $issuedAt,
				'exp' => $issuedAt + $this->_opt['expiration'],
				'user' => $this->user()
			), $this->_opt['secret']) :
			null;
	}
	
	
    /**
     * Call
     *
     * This method will check the HTTP request headers for previous authentication. If
     * the request has already authenticated, the next middleware is called. Otherwise,
     * a 401 Authentication Required response is returned to the client.
     */
    public function call()
    {
		
		$req = $this->app->request();
		$method = $req->getMethod();
		$uri = $req->getResourceUri();
		
		if(isset(static::$noRestrictedResourceUri[$method]) && in_array($uri,static::$noRestrictedResourceUri[$method],true)){
			// unrestricted route
			$this->next->call();
		}
		else {
			try {
				if(($token = $req->headers('HTTP_X_ACCESS_TOKEN')) || ($token = $req->get('access_token'))){
					// a token was provided
					
					try{ // try to decode it !
						$decodedJwt = \Firebase\JWT\JWT::decode($token, $this->_opt['secret'], array('HS256'));
					}
					catch(\Exception $e){
						// the token is invalid
						throw new \Exception('invalid JSON web token',401);
					}
					
					if($user = $this->_ething->findOneUserById($decodedJwt->user->id)){
						$this->_mode = 'token';
						$this->_user = $user;
						$this->_fs = new \Ething\Fs($this->_ething,$user);
						
						$this->next->call(); // ok
					}
					else {
						// the user does not exist any more !
						throw new \Exception('not authenticated',401);
					}
					
				}
				else if(($apiKey = $req->headers('HTTP_X_API_KEY')) || ($apiKey = $req->get('api_key'))){
					// is there an API key ?
					
					if( $device = $this->_ething->findOne(array(
							'_apiKey.key' => $apiKey,
							'type' => 'Device'
						)) ){
						
						$device->updateSeenDate();
						
						/*
							look for 'X-DEV-PROP' headers
							ie:  X-DEV-PROP: {"bat"=45,"loc":{"latitude":1.45,"longitude":-45.5}}
						*/
						$devProps = $req->headers('HTTP_X_DEV_PROP');
						if($devProps){
							// parsing JSON
							$props = \json_decode($devProps, true);
							if(json_last_error() === JSON_ERROR_NONE && !empty($props)){
								try{
									$device->set($props);
								}
								catch(\Exception $e){}
							}
						}
						
						/*
							scope control
						*/
						$scope = null;
						$matches = array();
						foreach(static::$scopeMap as $routeRegEx => $methods){
							if(preg_match($routeRegEx, $uri)){
								$scope = isset($methods[$method]) ? $methods[$method] : $methods['*'];
								break;
							}
						}
						
						if(empty($scope) || !\Ething\Scope::check($scope, $device))
							throw new \Exception('Forbidden', 403);
						
						
						
						
						$this->_mode = 'apikey';
						$this->_user = $device->user();
						$this->_device = $device;
						$this->_fs = new \Ething\Fs($this->_ething,$device);
						
						
						$this->next->call();
					}
					else 
						// unknown api key
						throw new \Exception('not authenticated',401);
					
				}
				else
					throw new \Exception('not authenticated',401);
				
				
			} catch(\Exception $e){
				try {
					$this->app->error($e); // call the error handler, will emit a Slim\Exception\Stop
				} catch(\Exception $e){}
				
			}
		}
		
		
		
    }
}

