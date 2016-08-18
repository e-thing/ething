<?php

namespace Ething\Event;

class TableDataAdded extends Event {
	
	public function __construct(\Ething\Resource $target, $addedData){
		parent::__construct($target, array(
			'value' => (array)$addedData
		));
	}
	
	public function description(){
		return "a new dataset is added to the table '{$this->target()->name()}'";
	}
	
	static public function check($resourceTypeName){
		return $resourceTypeName == 'Table';
	}
}
