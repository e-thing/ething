<?php


namespace Session;

$rootDir = __DIR__.'/..';

// composer
require_once $rootDir.'/vendor/autoload.php';


require_once $rootDir.'/src/Ething.php';
$ething = new \Ething\Ething();




/*
* session management
*/

function isAuthenticated($checkCsrf = null) {
	global $ething;
	
	$cookieName = $ething->config('session.cookie_name');
	
	if( !empty($_COOKIE[$cookieName]) && !empty($_COOKIE['Csrf-token']) && (!$checkCsrf || checkCsrf()) ){
			
		// ok
		
		// decode the JWT token !
		try {
			$sessionData = \Firebase\JWT\JWT::decode($_COOKIE[$cookieName], $ething->config('session.secret'), array('HS256'));
			if(isset($sessionData->sessionId)){
				return $sessionData;
			}
		} catch( \Exception $e ){ /* invalid JWT */ }
		
		
	}
	
	return false;
}

function checkCsrf() {
	// Csrf control
	$csrfToken = isset($_COOKIE['Csrf-token']) ? $_COOKIE['Csrf-token'] : null;
	if( $csrfToken ){
		
		$csrfToken2 = isset($_GET['csrf_token']) ? $_GET['csrf_token'] : null; // check in the query string
		if(!$csrfToken2)
			$csrfToken2 = isset($_SERVER['HTTP_X_CSRF_TOKEN']) ? $_SERVER['HTTP_X_CSRF_TOKEN'] : null; // check in the header
		
		return $csrfToken === $csrfToken2;
	}
	return false;
}

function authenticate($password) {
	global $ething;
	
	if($ething->config('auth.localonly') && !\Ething\Helpers::isLocalClient()){
		return false;
	}
	
	if( $ething->config('auth.password') === $password ){
	
		// set session cookie (httponly)
		$expireAt = time () + intval($ething->config('session.expiration'));
		$path = preg_replace('#/session/.*$#','',$_SERVER['REQUEST_URI']);
		$secure = isset($_SERVER['HTTPS']) && 'on' === $_SERVER['HTTPS'];
		$sessionData = array(
			'sessionId' => uniqid('',true),
			'iat' => time(),
			'exp' => $expireAt
		);
		$csrf_token = hash_hmac("md5", $sessionData['sessionId'], $ething->config('session.secret'));
		
		$jwt = \Firebase\JWT\JWT::encode($sessionData, $ething->config('session.secret'));
		
		setCookie($ething->config('session.cookie_name'), $jwt, $expireAt, $path, null, $secure, true);
		setCookie('Csrf-token', $csrf_token, $expireAt, $path, null, $secure, false);
		
		return (object)$sessionData;
	} else {
		return false;
	}
}

function unauthenticate() {
	global $ething;
	$path = preg_replace('#/session/.*$#','',$_SERVER['REQUEST_URI']);
	// remove the session cookie
	$cookieSessionName = $ething->config('session.cookie_name');
	setcookie($cookieSessionName, "", time() - 3600, $path);
	setcookie('Csrf-token', "", time() - 3600, $path);
	unset($_COOKIE[$cookieSessionName]);
	unset($_COOKIE['Csrf-token']);
}

