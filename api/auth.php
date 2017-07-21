<?php
/**
 * HTTP Basic Authentication
 */
namespace Auth;


require_once __DIR__.'/../session/session.php';

class HttpAuth extends \Slim\Middleware
{
	public $ething = null;
	private $_originator = null; // only available for apikey authentication, return the resource of the apikey
	private $_scope = null;
	private $_mode = 'unauthenticated';
	
	
	public function __construct(\Ething\Ething $ething)
    {
        $this->ething = $ething;
    }
	
	
	private static $noRestrictedResourceUri = array(
		'GET' => array('/swagger.json')
	);
	
	public function originator() {
		return $this->_originator;
	}
	
	public function scope() {
		return $this->_scope;
	}
	
	public function isAuthenticated() {
		return $this->_mode !== 'unauthenticated';
	}
	
	// 'unauthenticated' , 'api' , 'session' , 'apikey' , 'basic', 'public'
	public function mode(){
		return $this->_mode;
	}
	
	private function authenticate($mode, $scope = null, $originator = null){
		if($mode){
			$this->_mode = $mode;
			$this->_scope = $scope;
			$this->_originator = $originator;
		}
		else {
			$this->_mode = 'unauthenticated';
			$this->_scope = null;
			$this->_originator = null;
		}
	}
	
	public function unauthenticate(){
		$this->authenticate(null);
	}
	
	
    /**
     * Call
     *
     * This method will check the HTTP request for previous authentication. If
     * the request has already authenticated, the next middleware is called. Otherwise,
     * a 401 Authentication Required response is returned to the client.
     */
    public function call()
    {
		
		$this->authenticate(null);
		
		if($this->ething->config('auth.localonly') && !\Ething\Helpers::isLocalClient()){
			$this->app->error(new \Exception('not authenticated',401));
		}
		
		$req = $this->app->request();
		$method = $req->getMethod();
		$uri = $req->getResourceUri();
		
		if(isset(static::$noRestrictedResourceUri[$method]) && in_array($uri,static::$noRestrictedResourceUri[$method],true)){
			// unrestricted route
			$this->next->call();
		}
		else {
			try {
				
				/*
				* SESSION AUTH
				*/
				if( $session = \Session\isAuthenticated(true) ){
					
					$this->_mode = 'session';
					
				}
				/*
				* APIKEY AUTH
				*/
				else if(($apiKey = $req->headers('HTTP_X_API_KEY')) || ($apiKey = $req->get('api_key'))){
					// is there an API key ?
					
					if( $originator = $this->ething->findOne(array(
							'#apikey' => $apiKey
						)) ){
						
						if($originator instanceof \Ething\Device\Device){
							$originator->updateSeenDate();
							
							$devBat = $req->headers('HTTP_X_DEV_BAT');
							if(is_numeric($devBat)) $devBat = floatval($devBat);
							else if($devBat==="null") $devBat = null;
							else $devBat = false;
							if($devBat!==false){
								$originator->set(array(
									'battery' => $devBat
								));
							}
							
						}
						
						$this->authenticate('apikey', $originator->scope, $originator);
						
					}
					
				}
				/*
				* BASIC AUTH
				*/
				
				else if( isset($_SERVER['PHP_AUTH_USER']) && isset($_SERVER['PHP_AUTH_PW']) ){
					
					$username = $_SERVER['PHP_AUTH_USER'];
					$password = $_SERVER['PHP_AUTH_PW'];
					
					if( $username === 'ething' && $this->ething->config('auth.password') === $password){
						$this->authenticate('basic');
					}
					
				}
				
				/*
				* PUBLIC ACCESS
				*/
				else if(preg_match('@/([^/]+)/([a-zA-Z0-9_-]{7})($|/|\\?)@',$uri,$matches)){
					if($r = $this->ething->get($matches[2])){
						$publicMode = $r->get('public');
						switch($publicMode){
							case 'readonly':
								$this->authenticate('public', 'resource:read');
								break;
							case 'readwrite':
								$this->authenticate('public', 'resource:read resource:write');
								break;
						}
					}
				}
				
				
				if($this->isAuthenticated()){
					
					
					
					if($this->_originator)
						$this->ething->resourceQueryParser()->addConstant('me',(string)$this->_originator->id());
					
					// global scope
					$scopes = $this->scope();
					if( $scopes !== null ){
						if( !in_array('resource:admin', explode(' ', $scopes)) )
							\Ething\Ething::$showPrivateField = false;
					}
					
					$this->next->call();
				}
				else
					throw new \Exception('not authenticated',401); // auth fallback
					
				
			} catch(\Exception $e){
				try {
					$this->app->error($e); // call the error handler, will emit a Slim\Exception\Stop
				} catch(\Exception $e){}
				
			}
		}
		
		
		
    }
	
	
	public function hasPermission($permission){
		$permissions = $this->scope();
		if($permissions !== null){
			if(!in_array($permission, explode(' ', $permissions)))
				return false;
		}
		return true;
	}
	
	public function checkPermission($permission){
		if(!$this->hasPermission($permission))
			throw new \Exception('access denied',403);
	}
	
	/*
	* return a slim route middleware function that validate the permission.
	* 
	* $allowedPermissions : allowed permissions of the route
	*/
	public function permissions($allowedPermissions){
		$auth = $this;
		
		return function () use ( $allowedPermissions, $auth ) {
			
			$permissions = $auth->scope();
			
			if($permissions !== null){
				
				$allowedPermissions = explode(' ', $allowedPermissions);
				$permissions = explode(' ', $permissions);
				
				// check if the given permissions is able to execute this route
				
				$npass = 0;
				
				foreach($permissions as $permission){
					
					if(empty($permission)) continue;
					
					if(in_array($permission, $allowedPermissions)){
						$npass++;
					}
					
				}
				
				if($npass === 0)
					throw new \Exception('access denied',403);
				
			}
			
		};
		
	}
}

