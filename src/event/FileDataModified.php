<?php

namespace Ething\Event;


class FileDataModified extends Event {
	
	public function description(){
		return "the content of the file '{$this->target()->name()}' is modified";
	}
	
	static public function check($resourceTypeName){
		return $resourceTypeName == 'File';
	}
}

