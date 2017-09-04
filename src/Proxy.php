<?php


namespace Ething;


/*
* cf. https://github.com/Athlon1600/php-proxy-app/blob/master/config.php
*
* todo : cookie, proxify location response header
*
*/


class Proxy {

	private $ething = null;
	public $request = null;
	public $response = null;
	public $stream = null;
	private $cancelled = false;
	
	
	private $on_response = null; // function($proxy)
	
	
	public static $deny_request_headers = array(
		'Referer',
		'Accept-Encoding',
		'Host'
	);
	
	public static $deny_request_query = array();
	
	public static $allow_response_headers = array(
		'content-type', 'content-length', 'accept-ranges', 'content-range', 'content-disposition', 'location', 'set-cookie',
		'last-modified', 'etag', 'cache-control', 'expires' // enable caching
	);
	
	public static $before_request = null;
	public static $response_transform = null;
	
	
	public function __construct(Ething $ething){
		$this->ething = $ething;
	}
	
	public function onResponse($on_response){
		$this->on_response = $on_response;
	}
	
	public function cancel(){
		$this->cancelled = true;
	}
	
	public function isCancelled(){
		return !empty($this->cancelled);
	}

	private function header_callback($ch, $headers){

		$parts = explode(":", $headers, 2);
		
		// extract status code
		if(preg_match('/HTTP\/1.\d+ (\d+)/', $headers, $matches)){
			
			$this->response->setHeaders(array()); // remove any previous header set, may happen on redirection
			$this->response->setStatus($matches[1]);
			
		
		} else if(count($parts) == 2){
			
			$name = strtolower($parts[0]);
			$value = trim($parts[1]);
			
			// filter some header
			if(in_array($name, static::$allow_response_headers)){
				$this->response->addHeader($name, $value);
			}
			
		} else {
			
			//end of headers
			$status = $this->response->getStatus();
			if($status != 301 && $status != 302){
				if(is_callable(static::$response_transform))
					call_user_func(static::$response_transform, $this);
				
				
				if($this->stream instanceof Stream){
					$this->stream->errCode($this->response->isSuccessful() ? 0 : $this->response->getStatus());
					$this->stream->contentType($this->response->contentType());
				}
				
				if(is_callable($this->on_response))
					call_user_func($this->on_response, $this);
				
				if(!$this->isCancelled()){
					if($this->stream === true){
						$this->response->sendHeader();
					}
				}
			}
		}
		
		return strlen($headers);
	}
	
	private function write_callback($ch, $str) {
		if($this->isCancelled())
			return 0;
		
		$len = strlen($str);
		
		if($this->stream === true){
			echo $str;
			flush();
		}
		else if($this->stream instanceof Stream){
			$this->stream->out($str, $this->response->isSuccessful() ? 1 : 2);
		}
		else if($this->stream !== false)
			$this->response->body .= $str;
		
		return $len;
	}
	
	// by default, the response content will be in the response object
	public function request(Request $request, $stream = null, $user = null, $password = null, $auth_mode = 'basic', $curl_options = null){
		
		$this->cancelled = false;
		$this->stream = $stream;
		
		$response = new Response();
		$url = $request->url;
		
		$this->request = $request;
		$this->response = $response;
		
		// remove any forbidden header
		foreach(static::$deny_request_headers as $name)
			$request->removeHeader($name);
		// remove any forbidden query parameters
		foreach(static::$deny_request_query as $name)
			$url->removeParam($name);
		
		if(is_callable(static::$before_request))
			call_user_func(static::$before_request, $this);
		
		// to be removed ?
		if($this->stream === true){
			// remove any buffer
			while(ob_get_level()) ob_end_clean();
		}
		
		// curl
		$ch = curl_init();
		
		
		curl_setopt_array($ch, array(
			CURLOPT_CONNECTTIMEOUT 	=> 10, // The number of seconds to wait while trying to connect
			CURLOPT_TIMEOUT			=> 0, // maximum number of seconds to allow cURL functions to execute
			
			// don't return anything - we have other functions for that
			//CURLOPT_RETURNTRANSFER	=> false, // return the transfer as a string of the return value of curl_exec() instead of outputting it out directly. NOTE: disable it when CURLOPT_WRITEFUNCTION is set.
			CURLOPT_HEADER			=> false, // include the header in the output
			
			// don't bother with ssl
			CURLOPT_SSL_VERIFYPEER	=> false, // FALSE to stop cURL from verifying the peer's certificate. Alternate certificates to verify against can be specified with the CURLOPT_CAINFO option or a certificate directory can be specified with the CURLOPT_CAPATH option.
			CURLOPT_SSL_VERIFYHOST	=> false,
			
			// we will take care of redirects
			CURLOPT_FOLLOWLOCATION	=> true,  // follow any "Location: " header that the server sends as part of the HTTP header
			CURLOPT_AUTOREFERER		=> false, // TRUE to automatically set the Referer: field in requests where it follows a Location: redirect.
			CURLOPT_MAXREDIRS       => 5,     // The maximum amount of HTTP redirections to follow.
			CURLOPT_POSTREDIR       => 3      // 3=follow redirect with the same type of request both for 301 and 302 redirects, necessary for a POST|PUT redirect request. Cf https://evertpot.com/curl-redirect-requestbody/
			
			//CURLOPT_FRESH_CONNECT   => true, // force the use of a new connection instead of a cached one
			//CURLOPT_FORBID_REUSE    => true // force the connection to explicitly close when it has finished processing, and not be pooled for reuse
		));
		
		curl_setopt($ch, CURLOPT_HEADERFUNCTION, array($this, 'header_callback'));
		curl_setopt($ch, CURLOPT_WRITEFUNCTION, array($this, 'write_callback'));
		
		curl_setopt($ch, CURLOPT_CUSTOMREQUEST, $request->getMethod()); // A custom request method to use instead of "GET" or "HEAD" when doing a HTTP request.
		curl_setopt($ch, CURLOPT_POSTFIELDS, $request->body); // The full data to post in a HTTP "POST" operation.
		
		
		// fill in headers
		$headers = array();
		foreach($request->getHeaders() as $name => $value){
			$headers[] = sprintf("%s: %s", $name, $value);
		}
		
		// tell target website that we only accept plain text without any transformations
		$headers[] = sprintf("%s: %s", 'Accept-Encoding', 'identity');
		$headers[] = sprintf("%s: %s", 'Host', $url->host);
		
		curl_setopt($ch, CURLOPT_HTTPHEADER, $headers);
		
		
		// proxy
		$proxySettings = $this->ething->config('proxy');
		$isLocalHost = !!preg_match('/^(localhost|127\.[\d]+\.[\d]+\.[\d]+)$/i',$url->host);
		
		if(!$isLocalHost && !empty($proxySettings) && !empty($proxySettings['host'])){
			$proxyAddress = $proxySettings['host'];
			if(!empty($proxySettings['port']))
				$proxyAddress .= ':'.$proxySettings['port'];
			curl_setopt($ch, CURLOPT_PROXY, $proxyAddress); // The HTTP proxy to tunnel requests through
			// proxy authentication
			if(!empty($proxySettings['user']) && !empty($proxySettings['password']))
				curl_setopt($ch, CURLOPT_PROXYUSERPWD, $proxySettings['user'].':'.$proxySettings['password']); // A username and password formatted as "[username]:[password]" to use for the connection to the proxy.
		}
		
		
		// authentication
		if(!empty($user) && !empty($password)){
			switch($auth_mode){
				case 'digest':
					curl_setopt($ch, CURLOPT_HTTPAUTH, CURLAUTH_DIGEST);
					curl_setopt($ch, CURLOPT_USERPWD, $user.':'.$password);
					break;
				case 'query':
					$url->insertParam('user', $user);
					$url->insertParam('password', $password);
					break;
				default: // basic to default
					curl_setopt($ch, CURLOPT_HTTPAUTH, CURLAUTH_BASIC);
					curl_setopt($ch, CURLOPT_USERPWD, $user.':'.$password);
					break;
			}
		}
		
		if(!empty($curl_options))
			curl_setopt_array($ch, $curl_options);
		
		curl_setopt($ch, CURLOPT_URL, (string)$url);
		
		$result = curl_exec($ch);
		
		if($this->stream instanceof Stream){
			
			if(!$result){
				$this->stream->close(404, "Failed to connect [{$url}]: ".curl_error($ch));
			} else {
				$this->stream->close();
			}
			
		} else if(!$result) {
			throw new Exception("Failed to connect [{$url}]: ".curl_error($ch),404);
		}

		curl_close($ch);
		
		return $response;
		
	}
	
	
	
	
	public static function get(Ething $ething, $url, $stream = null) {
		$request = new Request($url, 'GET');
		$proxy = new Proxy($ething);
		return $proxy->request($request, $stream);
	}
	
	public static function post(Ething $ething, $url, $body = '', $headers = array(), $stream = null) {
		$request = new Request($url, 'POST', $headers, $body);
		$proxy = new Proxy($ething);
		return $proxy->request($request, $stream);
	}

}



