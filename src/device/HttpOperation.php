<?php

namespace Ething\Device;

use \Ething\Stream;
use \Ething\Swagger;

class HttpOperation extends Operation {
	
	/*
	 options:
		- scheme : override default scheme in the swagger file
		- requestContentType : select the returned mime type if there are multiple mimes defined in the swagger file
		- timeout : request timeout
	*/
	public function call(Stream $stream = null, array $data = null, array $options = array()) {
		
		$swagger = new Swagger\Client($this->device()->getSpecification());
		
		$operation = $swagger->findOperationById($this->name());
		
		if(!$operation)
			throw new Exception("unknown operation {$this->name()}");
		
		$reqInfo = $operation->createRequest($data, $options);
		
		$reponse =  $this->device()->request(
			preg_replace('/^[^\/]*\/\/[^\/]+/', '', $reqInfo['url']), // remove the scheme + hostname
			$reqInfo['method'],
			$reqInfo['headers'],
			$reqInfo['body'],
			$stream,
			$options
		);
		
		return $reponse->isSuccessful();
	}
	
}
