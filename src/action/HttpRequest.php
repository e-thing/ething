<?php


namespace Ething\Action;


use \Ething\Url;
use \Ething\Proxy;
use \Ething\Request;
use \Ething\Response;
use \Ething\StreamBuffer;


class HttpRequest extends Action {
	
	static public function validate(array &$attributes, array $context){
		
		$attributes = array_merge(
			array( 
				'url' => null,
				'method' => null,
				'auth' => null,
				'headers' => array(),
				'body' => null,
				'output' => null
			),
			$attributes
		);
		
		foreach(array_keys($attributes) as $key){
			
			switch($key){
				
				case 'url':
					
					if(!Url::validate($attributes[$key]))
						throw new \Exception("field '{$key}' is not a valid url.");
					
					break;
				
				case 'method':
					
					if(!is_string($attributes[$key]) || !in_array(strtolower($attributes[$key]), Request::$validMethodes))
						throw new \Exception("field '{$key}' is not a valid method.");
					
					break;
					
				case 'headers':
					
					if(is_null($attributes[$key]))
						$attributes[$key] = array();
					
					if(is_object($attributes[$key]))
						$attributes[$key] = (array)$attributes[$key];
					
					if(!is_array($attributes[$key]))
						throw new \Exception("field '{$key}' is invalid.");
					
					foreach($attributes[$key] as $key => $value){
						if(!is_string($key) || !is_string($value) || empty($value))
							throw new \Exception("field '{$key}.{$key}' must be a non empty string.");
					}
					
					break;
				
				case 'auth':
					
					$value = &$attributes[$key];
					
					if(is_object($value))
						$value = (array)$value;
					
					if(is_array($value) && !empty($value['type']) && !empty($value['user']) && !empty($value['password']) && is_string($value['type']) && is_string($value['user']) && is_string($value['password'])){
						
						$authMode = strtolower($value['type']);
						$authUser = $value['user'];
						$authPwd = $value['password'];
						
						if(in_array($authMode, Request::$validAuthModes)){
							$value = array(
								'type' => $authMode,
								'user' => $authUser,
								'password' => $authPwd
							);
						} else {
							throw new \Exception("field '{$key}' : invalid auth mode.");
						}
					}
					else if(!is_null($value))
						throw new \Exception("field '{$key}' is invalid.");
					
					break;
					
				case 'body':
					
					$value = &$attributes[$key];
					
					if(is_string($value)){
						$value = array(
							'type' => 'plain',
							'value' => $value
						);
					}
					
					if(is_object($value))
						$value = (array)$value;
					
					if(is_array($value) && !empty($value['type']) && !empty($value['value']) && is_string($value['type']) && is_string($value['value'])){
						
						$bodyMode = strtolower($value['type']);
						$bodyContent = $value['value'];
						
						$value = array(
							'type' => $bodyMode,
							'value' => $bodyContent
						);
						
						switch($bodyMode){
							case 'plain':
								
								if(!is_string($bodyContent) || strlen($bodyContent) > 1024)
									throw new \Exception("field '{$key}.value' must be a string with a maximum size of 1024 characters.");
								
								break;
								
							case 'binary':
								
								if(!is_string($bodyContent) || strlen($bodyContent) > 65536 || base64_decode($bodyContent) === false)
									throw new \Exception("field '{$key}.value' must be a base64 encoded string with a maximum size of 64 kbytes.");
								
								break;
							case 'resource': 
								
								if(!is_string($bodyContent))
									throw new \Exception("field '{$key}.value' must be an id.");
								
								$resource = $context['ething']->get($bodyContent);
								if(!$resource)
									throw new \Exception("the resource with id '{$bodyContent}' does not exist.");
								
								if(!in_array($resource->type(), array('Table','File')))
									throw new \Exception("the resource with id '{$bodyContent}' must be a Table or a File.");
								
								break;
							
							default:
								throw new \Exception("field '{$key}.type' : unknown body type.");
								
						}
						
					}
					else if(!is_null($value))
						throw new \Exception("field '{$key}' is invalid.");
					
					break;
				
				case 'output':
					
					if(!((is_string($attributes[$key]) || !empty($attributes[$key])) || is_null($attributes[$key])))
						throw new \Exception("field '{$key}' must be a non empty string or unset.");
					
					break;
					
				default:
					throw new \Exception("field '{$key}' unknown.");
			}
			
		}
		
		return true; 
	}
	
	
	protected function call(\Ething\Event\Signal $signal){
		
		$body = null;
		$contentType = null;
		
		if(!is_null($this->body)){
			switch($this->body['type']){
				case 'plain':
					$body = $this->body['value'];
					$contentType = 'text/plain';
					break;
				
				case 'binary':
					$body = base64_decode($this->body['value']);
					$contentType = 'application/octet-stream';
					break;
				
				case 'resource': 
					
					$src = $this->ething()->get( $this->body['value'] );
					if(!$src)
						throw new \Ething\InvalidRuleException("The resource #{$this->body['value']} does not exist any more");
					
					if($src instanceof \Ething\File){
						$body = $src->read();
						$contentType = $src->mime;
					}
					else if($src instanceof \Ething\Table){
						$body = \json_endode( $src->select(), JSON_PRETTY_PRINT|JSON_UNESCAPED_SLASHES);
						$contentType = 'application/json';
					}
					else if($src instanceof \Ething\App){
						$body = $src->readScript();
						$contentType = 'text/html';
					}
					
					break;
					
			}
		}
		
		
		
		$request = new Request($this->url, $this->method, $this->headers, $body);
		
		if($contentType && !$request->contentType())
			$request->addHeader('content-type', $contentType);
		
		$authMode = isset($this->auth['type']) ? $this->auth['type'] : null;
		$authUser = isset($this->auth['user']) ? $this->auth['user'] : null;
		$authPwd = isset($this->auth['password']) ? $this->auth['password'] : null;
		
		
		// send the request
		$proxy = new Proxy($this->ething());
		$buffer = new StreamBuffer();
		
		$response = $proxy->request($request, $buffer, $authUser, $authPwd, $authMode, array(
			CURLOPT_TIMEOUT => 20 // in secondes
		));
		
		if(!$response){
			throw new \Exception("unable to connect to the host");
		}
		
		if(!$response->isSuccessful()){
			throw new \Exception( sprintf("status: %d", $response->getStatus()) );
		}
		
		if(!is_null($this->output) && $buffer->length()){	
			//create a new file
			if($file = $this->ething()->create('File', array( 'name' => $this->output ))){
				$file->write( $buffer->data() ); // put the content in it !
			}
		}
		
	}
	
}


