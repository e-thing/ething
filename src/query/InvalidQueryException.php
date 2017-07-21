<?php

namespace Ething\Query;



class InvalidQueryException extends \Exception {

	public function __construct($message, Stream $stream = null){
		parent::__construct(isset($stream) ? "(near position {$stream->previousIndex()}) {$message}" : $message);
	}

}

