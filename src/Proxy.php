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
	private $response_code = null;
	private $response_headers = array();
	private $on_response = null;
	private $url_proxify = null;
	private $url = null;
	
	
	public static $blackListHeaders = array(
		'Referer',
		'Accept-Encoding',
		'Host',
		'X-ACCESS-TOKEN',
		'X-API-KEY'
	);
	
	public static $blackListQuery = array(
		'access_token',
		'api_key'
	);
	
	
	public function __construct(Ething $ething){
		$this->ething = $ething;
	}
	
	public function onResponse($on_response){
		$this->on_response = $on_response;
	}
	
	public function setUrlProxify($handler){
		$this->url_proxify = $handler;
	}
	
	public static function getQuery($filter = null){
		
		$filteredQueryStringParam = array();
		
		foreach($_GET as $k=>$v) {
			
			if(in_array(strtolower($k), array_map('strtolower', static::$blackListQuery)))
				continue;
			
			if(is_array($filter)){
				if(in_array(strtolower($k), array_map('strtolower', $filter)))
					continue;
			}
			else if(is_callable($filter)){
				if(!$filter($k))
					continue;
			}
			
			$filteredQueryStringParam[$k] = $v;
		}
		
		return http_build_query($filteredQueryStringParam);
	}

	private function sendHeaders(){

		if(headers_sent()){
			return;
		}
		
		http_response_code($this->response_code);
		
		// we need content-encoding (in case server refuses to serve it in plain text)
		$forward_headers = array(
			'content-type', 'content-length', 'accept-ranges', 'content-range', 'content-disposition', 'location', 'set-cookie',
			'last-modified', 'etag', 'cache-control', 'expires' // enable caching
		);
		
		foreach($this->response_headers as $name => $value){
			
			// is this one of the headers we wish to forward back to the client?
			if(in_array($name, $forward_headers)){
				
				if($name == 'location'){
					// proxify this header for the redirection to work
					
					$value = static::rel2abs($value,$this->url);
					
					if(is_callable($this->url_proxify))
						$value = call_user_func($this->url_proxify, $value);
					
				}
				
				header(sprintf("%s: %s", $name, $value));
			}
		}
	}

	private function header_callback($ch, $headers){

		$parts = explode(":", $headers, 2);
		
		// extract status code
		if(preg_match('/HTTP\/1.\d+ (\d+)/', $headers, $matches)){
			
			//echo "status code : ".$matches[1];
			
			$this->response_code = intval($matches[1]);
			
			$this->response_headers = array(); // remove any previous headers when a new header bloc arrives
			
			if(is_callable($this->on_response))
				call_user_func($this->on_response, $this->response_code);
		
		} else if(count($parts) == 2){
			
			$name = strtolower($parts[0]);
			$value = trim($parts[1]);
			
			$this->response_headers[$name] = $value;
			
			// this must be a header: value line
			//echo "header : ".$name." : ".$value;
			
			
		} else {
			
			//echo "end of headers";
			//exit;
			
			$this->sendHeaders();
			
		}
		
		return strlen($headers);
	}

	private function write_callback($ch, $str){
		$len = strlen($str);
		
		echo $str;
		flush();
		
		return $len;
	}


	public function forward($url, $curl_options = null){
		
		// remove any buffer
		while(ob_get_level()) ob_end_clean(); 
		
		// curl
		$ch = curl_init();
		
		
		curl_setopt_array($ch, array(
			CURLOPT_CONNECTTIMEOUT 	=> 10, // The number of seconds to wait while trying to connect
			CURLOPT_TIMEOUT			=> 0, // maximum number of seconds to allow cURL functions to execute
			
			// don't return anything - we have other functions for that
			CURLOPT_RETURNTRANSFER	=> false, // return the transfer as a string of the return value of curl_exec() instead of outputting it out directly
			CURLOPT_HEADER			=> false, // include the header in the output
			
			// don't bother with ssl
			CURLOPT_SSL_VERIFYPEER	=> false, // FALSE to stop cURL from verifying the peer's certificate. Alternate certificates to verify against can be specified with the CURLOPT_CAINFO option or a certificate directory can be specified with the CURLOPT_CAPATH option.
			CURLOPT_SSL_VERIFYHOST	=> false,
			
			// we will take care of redirects
			CURLOPT_FOLLOWLOCATION	=> false, // follow any "Location: " header that the server sends as part of the HTTP header
			CURLOPT_AUTOREFERER		=> false//,
			
			//CURLOPT_FRESH_CONNECT   => true, // force the use of a new connection instead of a cached one
			//CURLOPT_FORBID_REUSE    => true // force the connection to explicitly close when it has finished processing, and not be pooled for reuse
		));
		
		curl_setopt($ch, CURLOPT_HEADERFUNCTION, array($this, 'header_callback'));
		curl_setopt($ch, CURLOPT_WRITEFUNCTION, array($this, 'write_callback'));
		
		curl_setopt($ch, CURLOPT_CUSTOMREQUEST, $_SERVER['REQUEST_METHOD']); // A custom request method to use instead of "GET" or "HEAD" when doing a HTTP request.
		curl_setopt($ch, CURLOPT_POSTFIELDS, file_get_contents('php://input')); // The full data to post in a HTTP "POST" operation.
		
		
		// fill in headers
		$notsend_headers = array_map('strtolower', static::$blackListHeaders);
		$headers = array();
		foreach($_SERVER as $name => $value){
		
			if(strpos($name, 'HTTP_') === 0){
				$name = substr($name, 5);
				$name = str_replace('_', ' ', $name);
				$name = ucwords(strtolower($name));
				$name = str_replace(' ', '-', $name);
				
				if(!in_array(strtolower($name), $notsend_headers))
					$headers[] = sprintf("%s: %s", $name, $value);
			}
		}
		
		// tell target website that we only accept plain text without any transformations
		$headers[] = sprintf("%s: %s", 'Accept-Encoding', 'identity');
		$headers[] = sprintf("%s: %s", 'Host', parse_url($url, PHP_URL_HOST));
		
		curl_setopt($ch, CURLOPT_HTTPHEADER, $headers);
		
		
		
		// proxy
		$proxySettings = $this->ething->config('proxy');
		$isLocalHost = !!preg_match('/^(localhost|127\.[\d]+\.[\d]+\.[\d]+)$/i',parse_url($url,PHP_URL_HOST));
		
		if(!$isLocalHost && !empty($proxySettings) && !empty($proxySettings['host'])){
			$proxyAddress = $proxySettings['host'];
			if(!empty($proxySettings['port']))
				$proxyAddress .= ':'.$proxySettings['port'];
			curl_setopt($ch, CURLOPT_PROXY, $proxyAddress); // The HTTP proxy to tunnel requests through
			// proxy authentication
			if(!empty($proxySettings['user']) && !empty($proxySettings['password']))
				curl_setopt($ch, CURLOPT_PROXYUSERPWD, $proxySettings['user'].':'.$proxySettings['password']); // A username and password formatted as "[username]:[password]" to use for the connection to the proxy.
		}
		
		
		if(is_array($curl_options))
			curl_setopt_array($ch, $curl_options);
		
		curl_setopt($ch, CURLOPT_URL, $url);
		
		$this->url = $url;
		
		$result = curl_exec($ch);
		
		
		if(!$result){
			throw new Exception("Failed to connect [{$url}]: ".curl_error($ch),404);
		}

		curl_close($ch);
		
		exit();
		
	}
	
	
	// helpers
	
	static public function rel2abs($rel, $base)
	{
		if (strpos($rel, "//") === 0) {
			return "http:" . $rel;
		}
		
		if($rel == ""){
			return "";
		}
		
		/* return if  already absolute URL */
		if (parse_url($rel, PHP_URL_SCHEME) != '') return $rel;
		/* queries and  anchors */
		if ($rel[0] == '#' || $rel[0] == '?') return $base . $rel;
		/* parse base URL  and convert to local variables:
		$scheme, $host,  $path */
		extract(parse_url($base));
		/* remove  non-directory element from path */
		@$path = preg_replace('#/[^/]*$#', '', $path);
		/* destroy path if  relative url points to root */
		if ($rel[0] == '/') $path = '';
		/* dirty absolute  URL */
		$abs = "$host$path/$rel";
		/* replace '//' or  '/./' or '/foo/../' with '/' */
		$re = array(
			'#(/\.?/)#',
			'#/(?!\.\.)[^/]+/\.\./#'
		);
		for ($n = 1; $n > 0; $abs = preg_replace($re, '/', $abs, -1, $n)) {}

		/* absolute URL is  ready! */
		return $scheme . '://' . $abs;
	}

}



