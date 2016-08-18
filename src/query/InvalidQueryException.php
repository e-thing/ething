<?php

namespace Ething\Query;



class InvalidQueryException extends \Exception {

	public function __construct($message, Stream $stream){
		parent::__construct("(near position {$stream->previousIndex()}) {$message}");
	}

}

