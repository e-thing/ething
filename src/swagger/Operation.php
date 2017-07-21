<?php

namespace Ething\Swagger;



class Operation {
	
	private $data;
	private $path;
	private $method;
	
	public function __construct($method, $data, $path) {
		$this->data = $data;
		$this->path = $path;
		$this->method = $method;
		
		if(!isset($this->data->operationId)){
		
			// generate a unique operation id
			
			$opId = $this->method . '_' . $this->path->path();
			
			$opId = preg_replace('/[\s!@#$%^&*()_+=\[{\]};:<>|.\/?,\'"-]/', '_', $opId);
			$opId = preg_replace('/((_){2,})/', '_', $opId);
			$opId = preg_replace('/^_*/', '', $opId);
			$opId = preg_replace('/_*$/', '', $opId);
			
			$this->data->operationId = $opId;
		}
	}
	
	
	public function name() {
		return $this->data->operationId;
	}
	
	
	public function method() {
		return $this->method;
	}
	
	public function description() {
		return empty($this->data->description) ? '' : $this->data->description;
	}
	
	public function path() {
		return $this->path;
	}
	
	public function swagger() {
		return $this->path->swagger();
	}
	
	public function produces() {
		$produces = isset($this->data->produces) ? $this->data->produces : $this->swagger()->produces();
		return $produces;
	}
	
	public function consumes() {
		$comsumes = isset($this->data->consumes) ? $this->data->consumes : $this->swagger()->consumes();
		if(empty($comsumes))
			$comsumes = array('application/json'); // default to json
		return $comsumes;
	}
	
	public function parameters() {
		
		if(!isset($this->parameters_)){
			$parameters = $this->path->parameters();
			
			if(!empty($this->data->parameters)) {
				foreach($this->data->parameters as $param){
					
					if(isset($param->{'$ref'})){
						// resolve the reference
						$param = $this->swagger()->getRef($param->{'$ref'});
					}
					
					$parameters[] = $param->in == 'body' ? new BodyParameter($this, $param) : new StandardParameter($this, $param);
				}
			}
			
			$this->parameters_ = $parameters;
		}
		
		return $this->parameters_;
	}
	
	
	
	public function createRequest(array $data = null, array $options = array()) {
		
		// build the url
		$schemes = isset($this->data->schemes) ? $this->data->schemes : $this->swagger()->schemes();
		if(empty($schemes))
			$schemes = array('http');
		$scheme = (!empty($options['scheme']) && in_array($options['scheme'], $schemes)) ? $options['scheme'] : $schemes[0];
		
		$url = $scheme .'://' . $this->swagger()->host() .  $this->swagger()->basePath(). $this->path->path();
		
		$method = $this->method;
		$query = array();
		$formData = array();
		$headers = array();
		$body = null;
		$hasFiles = false;
		$hasContentTypeHeader = false;
		$hasBody = false;
		
		$consumes = $this->consumes();
		
		$contentType = !empty($options['requestContentType']) ? $options['requestContentType'] : (in_array('application/json', $consumes) ? 'application/json' : $consumes[0]);
		
		
		foreach( $this->parameters() as $param){
			
			$hasValue = isset($data) && isset($data[$param->name()]);
			
			$hasDefault = ($param instanceof StandardParameter) && $param->hasDefault();
			
			if($hasValue){
				$value = $data[$param->name()];
			}
			else {
				if($param->isRequired()){
					if($hasDefault){
						$value = $param->geDefaultValue();
					} else {
						throw new Exception("missing required param: '{$param->name()}'");
					}
				}
				else
					continue;
			}
			
			// validate the incomming data
			if(!$param->validate($value))
				throw new Exception("invalid param: '{$param->name()}'");
			
			
			$in = $param->in();
			switch($in){
				
				case 'formData' : 
					
					if($param->type() == 'file'){
						if(!isset($finfo))
							$finfo = new \finfo(FILEINFO_MIME);
						$formData[$param->name()] = array(
							"type" => "file",
							"content" => $value,
							"filename" => 'file'.count($files),
							"mime" => $finfo->buffer($value)
						);
						
						$hasFiles = true;
					} else {
						$formData[$param->name()] = array(
							"type" => "text",
							"content" => $value
						);
					}
					
					break;
					
				case 'query' : 
					
					$el = '';
					if(is_array($value) && $param->collectionFormat() == 'multi'){
						if($param->collectionFormat() == 'multi'){
							$p = array();
							foreach($value as $qp)
								$p[] = urlencode($param->name()) . '=' . urlencode($qp);
							$el = implode('&', $p);
						} else {
							$el = http_build_query( array( $param->name() => $value ) );
						}
					}
					else 
						$el = urlencode($param->name()) . '=' . urlencode($value);
					
					if(!empty($el)){
						$query[] = $el;
					}
					
					break;
					
				case 'header' : 
					
					if(preg_match('/^content-type$/i', $param->name())){
						$contentType = $value;
						$hasContentTypeHeader = true;
					}
					
					$headers[$param->name()] = $value;
					
					break;
					
				case 'path' : 
					$url = preg_replace('/\{'.$param->name().'\}/i', urlencode($value), $url);
					break;
					
				case 'body' : 
					
					$hasBody = true;
					$body = $value;
					
					break;
			}
			
			
			
		}
		
		
		$query = implode('&', $query);
		
		
		
		if(!empty($query)){
			$url .= strpos($url, '?')===false ? '?'.$query : '&'.$query;
		}
		
		
		// prepare the body
		if(!empty($formData)){
			// there is a form data
			
			// check if the consumes mime type are compatible
			$ph = array_intersect($consumes, array('application/x-www-form-urlencoded','multipart/form-data'));
			if(!empty($ph))
				$contentType = $ph[0];
			else
				$contentType = 'application/x-www-form-urlencoded'; // default
			
			
			if($hasFiles)
				$contentType = 'multipart/form-data'; // no choice !
			
			
			if($contentType === 'multipart/form-data'){
				// multipart form ...
				$boundary=md5(time());
				$contentType .= '; boundary=' . $boundary;
				$body = static::generateMultipartFormDataBody($formData, $boundary);
			}
			else {
				$body = implode('&', $formData);
			}
			
		}
		else if($hasBody){
			
			if(preg_match('/json/i', $contentType)){
				
				if(empty($body))
					$body = '{}';
				
				if(!is_string($body))
					$body = json_encode($body, JSON_PRETTY_PRINT);
				
			}
			else {
				throw new Exception("unable to encode the body data into '{$contentType}'");
			}
			
		}
		
		if(!$hasContentTypeHeader && $hasBody)
			$headers['Content-Type'] = $contentType;
		
		
		return array(
			'method' => strtoupper($method),
			'url' => $url,
			'headers' => $headers,
			'body' => $body
		);
		
		
	}
	
	
	
	private static function generateMultipartFormDataBody($data, $boundary){
		
		$body = '';
		$eol = "\r\n";
		
		foreach($data as $name => $d){
			
			$body .= '--' . $boundary . $eol;
			
			if($d['type']==='file'){
				$body .= 'Content-Disposition: form-data; name="'. $name .'"; filename="'. $d['filename'] .'"' . $eol;
				$body .= 'Content-Type: ' . $d['mime'] . $eol;
				$body .= $d['content'] . $eol;
			} else {
				$body .= 'Content-Disposition: form-data; name="'. $name .'"' . $eol . $eol;
				$body .= $d['content'] . $eol;
			}
		}
		
		$body .= "--" . $boundary . "--" . $eol . $eol;
		
		return $body;
	}

	
}
