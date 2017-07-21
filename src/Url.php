<?php


namespace Ething;



class Url {
	
	private $dirty = true;
	private $url;
	private $parsed;
	
	
	public function __construct($url, array $default = array()){
		
		$parsed = parse_url($url);
		
		if($parsed === false)
			throw \InvalidArgumentException("invalid URL: {$url}");
		
		$this->parsed = array_merge( array(
			'scheme' => 'http',
			'host' => 'localhost',
			'port' => null,
			'user' => null,
			'pass' => null,
			'query' => '',
			'fragment' => ''
		), $default, $parsed);
		
	}
	
	
	public function __get($name)
    {
		if($name == 'query' && is_array($this->parsed['query']))
			$this->parsed['query'] = http_build_query($this->parsed['query']);
        return isset($this->parsed[$name]) ? $this->parsed[$name] : '';
    }

    public function __set($name, $value)
    {
		$this->dirty = true;
        $this->parsed[$name] = $value;
    }
	
	
	
	public function __toString () {
		if($this->dirty){
			$parsed = $this->parsed;
			
			$url = empty($parsed['scheme']) ? 'http' : $parsed['scheme'];
			$url .= "://";
			if(!empty($parsed['user'])){
				$url .= $parsed['user'];
				if(!empty($parsed['pass']))
					$url .= ":{$parsed['pass']}";
				$url .= "@";
			}
			$url .= empty($parsed['host']) ? 'localhost' : $parsed['host'];
			if(!empty($parsed['port'])){
				$url .= ":{$parsed['port']}";
			}
			if(!empty($parsed['path'])){
				$url .= $parsed['path'];
			}
			if(!empty($parsed['query'])){
				$url .= '?'.(is_string($parsed['query']) ? $parsed['query'] : http_build_query($parsed['query']));
			}
			if(!empty($parsed['fragment'])){
				$url .= '#'.$parsed['fragment'];
			}
			
			$this->dirty = false;
			$this->url = $url;
		}
		
		return $this->url;
	}
	
	
	public function insertParam($name, $value){
		$this->dirty = true;
		// parse query string into an array
		if(is_string($this->parsed['query']))
			parse_str($this->parsed['query'], $this->parsed['query']);
		
		$this->parsed['query'][$name] = $value;
	}
	
	public function getParam($name){
		// parse query string into an array
		if(is_string($this->parsed['query']))
			parse_str($this->parsed['query'], $this->parsed['query']);
		
		return isset($this->parsed['query'][$name]) ? $this->parsed['query'][$name] : null;
	}
	
	public function removeParam($name){
		$this->dirty = true;
		// parse query string into an array
		if(is_string($this->parsed['query']))
			parse_str($this->parsed['query'], $this->parsed['query']);
		
		unset($this->parsed['query'][$name]);
	}
	
	
	public function concatPath($path){
		$p = $this->path;
		
		if(empty($p) || $p[strlen($p)-1] == '/')
			$p = substr($p, 0, -1);
		if(!empty($path) && $path[0] != '/')
			$path = '/'.$path;
		
		$this->path = $p.$path;
	}
	
	
	// allows only http and https URLs
	static public function validate(&$url){
		
		if(!is_string($url)) return false;
		
		// sanitize
		if(!preg_match('/^[a-z]+:/',$url)){ // set default schema if not set
			if(!preg_match('/^\/\//',$url)) $url = '//'.$url;
			$url = 'http:'.$url;
		}
		// validate
		if(filter_var($url, FILTER_VALIDATE_URL)!==false){
			$scheme = parse_url($url,PHP_URL_SCHEME);
			if(in_array($scheme,['http','https']))
				return true;
		}
		
		return false;
	}
	
	
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
	
	static function current(){
		$url = isset($_SERVER['HTTPS']) && 'on' === $_SERVER['HTTPS'] ? 'https' : 'http';
		$url .= '://'.$_SERVER['SERVER_NAME'];
		$url .= in_array((string)$_SERVER['SERVER_PORT'], array('80', '443')) ? '' : ':'.$_SERVER['SERVER_PORT'];
		$url .= $_SERVER['REQUEST_URI'];
		
		return $url;
	}

}

