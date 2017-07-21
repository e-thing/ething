<?php


namespace Ething\Action;
	
class ResourceRemove extends AbstractResourceAction {
	
	
	
	protected function call(\Ething\Event\Signal $signal){
		
		$resources = $this->getResources($signal);
		
		foreach($resources as $r){
			$r->remove();
		}
		
	}
	
}


