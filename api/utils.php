<?php
	
	namespace Utils;
		
	const CHK_STRING = 4;
	const CHK_LOGIC = 10;
	const CHK_INT = 13;
	const CHK_UNSIGNED_INT = 15;
	const CHK_URL = 19;
	const CHK_ID = 20;
	const CHK_STRING_ARRAY = 34;
	const CHK_FORMAT = 35;
	const CHK_DATEFORMAT = 36;
	const CHK_INVALIDFIELDMODE = 38;
	
	
	//const URL = '/^https?:\/\/(((www\.)?+[a-zA-Z0-9\.\-_]+(\.[a-zA-Z]{2,3})+)|(\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b))(:[0-9]{1,5})?(\/[a-zA-Z0-9_\-\s\.\/\?\%\#\&\=]*)?$/u';
	const URL = '/^https?:\/\/([0-9a-zA-Z\.-]+)(:[0-9]+)?(\/[a-zA-Z0-9_\-\s\.\/\?\%\#\&\=]*)?$/';
	const MONGOID = '/^[0-9a-zA-Z\-_]+$/';
	
	
	const FMT_JSON = 1;
	const FMT_JSON_PRETTY = 2;
	const FMT_CSV  = 5;
	const FMT_CSV_NOHEADER = 6;

	
	/*
	UTILS
	*/
	
	
	function jsonEncodeFilterByFields($resources,$fields){
		if(is_array($fields)){
			$fields = array_flip($fields);
			if(is_array($resources)){
				$out = array();
				foreach($resources as $resource){
					$out[] = array_intersect_key($resource->jsonSerialize(), $fields);
				}
			} else {
				$out = array_intersect_key($resources->jsonSerialize(), $fields);
			}
		} else {
			$out = $resources;
		}
		return json_encode($out,JSON_PRETTY_PRINT|JSON_UNESCAPED_SLASHES);
	}
	
	function validBoolean(&$bool)
	{
		if($bool === true || $bool === 1 || $bool === 'true' || $bool === '1')
			$bool = true;
		else if($bool === false || $bool === 0 || $bool === 'false' || $bool === '0')
			$bool = false;
		else
			return false;
		return true;
	}
	
	function validFormat(&$fmt) {
		$fmt=strtolower($fmt);
		if($fmt=="json")
			$fmt=FMT_JSON;
		else if($fmt=="json_pretty")
			$fmt=FMT_JSON_PRETTY;
		else if($fmt=="csv")
			$fmt=FMT_CSV;
		else if($fmt=="csv_no_header")
			$fmt=FMT_CSV_NOHEADER;
		else
			return false;
		return true;
	}
	
	function validDateFormat(&$fmt) {
		$fmt=strtolower($fmt);
		if($fmt=="timestamp")
			$fmt=\Ething\Table::TIMESTAMP;
		else if($fmt=="timestamp_ms")
			$fmt=\Ething\Table::TIMESTAMP_MS;
		else if($fmt=="rfc3339")
			$fmt=\DateTime::RFC3339;
		else if($fmt=="iso8601")
			$fmt=\DateTime::ISO8601;
		else if($fmt=="rss")
			$fmt=\DateTime::RSS;
		else
			return false;
		return true;
	}
	
	function validInvalidFieldMode(&$v) {
		$v=strtolower($v);
		if($v=="rename")
			$v=\Ething\Table::INVALID_FIELD_RENAME;
		else if($v=="stop")
			$v=\Ething\Table::INVALID_FIELD_STOP;
		else if($v=="skip")
			$v=\Ething\Table::INVALID_FIELD_SKIP;
		else if($v=="none")
			$v=\Ething\Table::INVALID_FIELD_NONE;
		else
			return false;
		return true;
	}
	
	function validId($id) {
		return is_string($id) && preg_match(MONGOID,$id);
	}
	
	
	/*
	DATA INPUT GETTERs
	*/
	
	// get a value of an array by its key with an insensitive case search (return NULL if not found)
	function getByInsensitiveCaseKey($key)
	{
		$key = strtolower($key);
		foreach($_GET as $k => $v){
			if( strtolower($k) === $key )
				return $v;
		}
		return null;
	}
	
	function check($checker,&$value,$info="")
	{
		switch($checker){
			
			case CHK_ID:
				if(!validId($value)){
					throw new Exception("Not regular resource identifier ('{$value}'){$info}.");
				}
				break;
			case CHK_LOGIC:
				if(!validBoolean($value)){
					throw new Exception("Not regular boolean ('{$value}'){$info}.");
				}
				break;
			case CHK_INT:
			case CHK_UNSIGNED_INT:
				if( !is_numeric($value) ){
					throw new Exception("Not regular numeric value ('{$value}'){$info}.");
				}
				$value = intval($value);
				if($checker===CHK_UNSIGNED_INT && $value<0){
					throw new Exception("Must be positive ('{$value}'){$info}.");
				}
				break;
			
			case CHK_URL: // accept empty string
				if($value!=='' && !preg_match(URL,$value)){
					throw new Exception("Not regular url ('{$value}'){$info}.");
				}
				break;
			case CHK_STRING:
				break;
			case CHK_STRING_ARRAY: // accept comma separated values
				if(!is_array($value)){
					$value = explode(',',$value);
				}
				break;
			case CHK_FORMAT:
				if(!validFormat($value)) {
					throw new Exception("Unknown format '{$value}' {$info}");
				}
				break;
			case CHK_DATEFORMAT:
				if(!validDateFormat($value)) {
					throw new Exception("Unknown date format '{$value}' {$info}");
				}
				break;
			case CHK_INVALIDFIELDMODE:
				if(!validInvalidFieldMode($value)) {
					throw new Exception("Unknown mode '{$value}' {$info}");
				}
				break;
			default:
				throw new \Exception();
		}
	}
	
	function getResource($auth, $id, $typeCheck = null) {
		
		if($id === 'me'){
			// special case, needs api key auth
			$r = $auth->originator();
		} else {
			check(CHK_ID,$id);
			$r = $auth->ething->get($id);
		}
		
		if($r){
			if(is_null($typeCheck) || preg_match('/^'.str_replace('\\', '\\\\', $typeCheck).'$/', $r->type()))
				return $r;
			else {
				throw new Exception('The resource is not a '.$typeCheck);
			}
		}
		else {
			throw new Exception('Unknown resource',404);
		}
	}
	
	function getResourceByName($auth, $filename, $type, $throwExceptionOnFail = true) {
		
		$filter = array(
			'name' => $filename,
			'type' => $type
		);
		
		if($originator = $auth->originator()){
			$filter['createdBy.id'] = $originator->id();
		} else {
			$filter['createdBy'] = null;
		}
		
		$r = $auth->ething->findOne($filter);
		
		if(!$r && $throwExceptionOnFail){
			throw new Exception('Unknown resource',404);
		}
		
		return $r;
	}
	
	function getParameter($key,$checker,$optionnal = false, $defaultValue = null)
	{
		$value = getByInsensitiveCaseKey($key);
		
		if( !isset($value) && !$optionnal ){
			throw new Exception('The key "'.$key.'" is mandatory.');
		}
		
		if(isset($value) && $value!==""){
			check($checker,$value,"[key='{$key}']");
		}
		else {
			// set the default value here
			$value = $defaultValue;
		}
		
		return $value;
	}
	
	function getJSON($app, $assoc = false){
		if($app->request->getMediaType() === 'application/json'){
			$props = \json_decode($app->request->getBody(), $assoc);
			if(json_last_error() === JSON_ERROR_NONE){
				return $props;
			}
			else {
				throw new Exception('Invalid JSON: '.json_last_error_msg());
			}
		}
		else {
			throw new Exception('only JSON data is accepted');
		}
	}
	
	
	
	
	/*
	FORMAT 
	*/
	
	const csv_separator = ",";
	const csv_eol = "\n";
	
	// if $fields is not set, it is automatically computed from the $data
	// print the result in the standard output
	function csv_encode($data,$fields=null,$print_header=true)
	{
		if(!isset($fields)){
			// build the key list from the data
			$fields = [];
			foreach ($data as $d) {
				$dk = array_keys(get_object_vars($d));
				foreach ($dk as $k)
					if(!in_array($k,$fields))
						$fields[] = $k;
			}
		}
		
		if($print_header){
			echo implode(csv_separator,$fields).csv_eol;
		}
		
		
		foreach ($data as $d) {
			$i=0;
			foreach($fields as $key){
				if($i>0)
					echo csv_separator;
				if(isset($d->$key)){
					if(is_string( $d->$key))
						$value = '"'.str_replace(array('\\','"'),array('\\\\','\\"'), $d->$key).'"';
					else if(is_bool( $d->$key))
						$value =  $d->$key ? 'true' : 'false';
					else
						$value = $d->$key;
				}
				else
					$value = '';
				
				echo $value;
				$i++;
			}
			echo csv_eol;
		}
		
	}
	
	
	/*
	READ MULTIPART 
	*/
	
	function readMultipartRelated(){
		
		$parse = array();
		
		// Get the MIME boundary string
		if(isset($_SERVER['CONTENT_TYPE']) && preg_match('#^multipart\/related\s*;\s*boundary="?([^"]+)"?$#i',$_SERVER['CONTENT_TYPE'],$matches)){
			
			list(, $boundary) = $matches;
			
			// get the body
			$body = @file_get_contents('php://input');
			
			if (!empty($boundary)){
				
				if(!function_exists('http_parse_headers')){
					function http_parse_headers($header){
						$retVal = array();
						$fields = preg_split("/\r?\n/", preg_replace('/\x0D\x0A[\x09\x20]+/', ' ', $header));
						foreach( $fields as $field ) {
							if( preg_match('/([^:]+): (.+)/m', $field, $match) ) {
								$match[1] = preg_replace_callback('/(?<=^|[\x09\x20\x2D])./', function ($matches) {
												return strtoupper($matches[0]);
											}, strtolower(trim($match[1])));
								if( isset($retVal[$match[1]]) ) {
									$retVal[$match[1]] = array($retVal[$match[1]], $match[2]);
								} else {
									$retVal[$match[1]] = trim($match[2]);
								}
							}
						}
						return $retVal;
					}
				}
				
				// Split the body into segments
				$segments = preg_split("/\r?\n--".$boundary."/", "\r\n".$body);
				array_shift($segments); // drop everything before the first boundary
				
				
				foreach($segments as $segment){
					if(substr($segment,0,2)=='--')
						break; // end of the body
					$sepi = strpos($segment,"\r\n\r\n");
					$sepilength=2;
					if($sepi===false){
						$sepi = strpos($segment,"\n\n"); // more robust !
						$sepilength=1;
					}
					if($sepi!==false){
						// headers found
						$headers = http_parse_headers(substr($segment,0,$sepi+$sepilength));
						$subbody = substr($segment,$sepi+(2*$sepilength));
						$parse[] = array(
							'headers' => $headers,
							'body'=> $subbody
						);
					}
					else {
						throw new Exception("Invalid multipart/related content");
					}
				}
				
				
			}
			else
				throw new Exception("Invalid multipart/related content");
			
		}
		
		return count($parse) ? $parse : null;
	}
	
	
	function getMediaType($contentType)
    {
        if ($contentType) {
            $contentTypeParts = preg_split('/\s*[;,]\s*/', $contentType);

            return strtolower($contentTypeParts[0]);
        }
        return null;
    }
	
	
	class Exception extends \Exception {
		// default return code is 400 (= Bad Request)
		public function __construct($message, $code = 400, \Exception $previous = null) {
			parent::__construct($message, $code, $previous);
		}
	}
	
	
	function hostname() {
		
		$hn = isset($_SERVER['HTTPS']) && 'on' === $_SERVER['HTTPS'] ? 'https' : 'http';
		$hn .= '://'.$_SERVER['SERVER_NAME'];
		$hn .= in_array((string)$_SERVER['SERVER_PORT'], array('80', '443')) ? '' : ':'.$_SERVER['SERVER_PORT'];
		
		return $hn;
		
	}
	
	function url() {
		
		return hostname() . $_SERVER['REQUEST_URI'];
		
	}
	