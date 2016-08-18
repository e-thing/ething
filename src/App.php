<?php
	
namespace Ething;

	/**
	 * @swagger-definition
	 * "App":{ 
	 *   "type": "object",
	 *   "description": "Application resource representation",
	 * 	 "allOf": [
	 * 		{
	 * 		   "$ref":"#/definitions/Resource"
	 * 		},
	 * 		{  
	 * 		   "type": "object",
	 * 		   "properties":{
	 *             "size": {
	 * 		          "type":"number",
	 * 		          "description":"The size of the application in bytes",
	 *                "readOnly": true
	 * 		       },
	 *             "hasIcon": {
	 * 		          "type":"boolean",
	 * 		          "description":"True if the application has an icon set. See the /app/<id>/icon endpoint for more details.",
	 *                "readOnly": true
	 * 		       },
	 *             "acceptedMime": {
	 * 		          "type":"array",
	 * 		          "items":{
	 *               	"type":"string"
	 *                },
	 * 		          "description":"A list of MIME types the application can consume",
	 *                "readOnly": true
	 * 		       }
	 * 		   }
	 * 		}
	 *   ]
	 * }
	 */
	 
	
	

class App extends Resource
{
	
	const VALIDATE_NAME = '/^[a-zA-Z0-9 !#$%&\'()+,\-.;=@^_`{}]{1,99}$/';
	const VALIDATE_MIME_TYPE = '/^[-\w*]+\/[-\w*]+$/'; // accept also * character -> image/* stands for all image mime type
	
	
	
	public function jsonSerialize() {
		$o = parent::jsonSerialize();
		$o['hasIcon'] = isset($this->_d['_icon']);
		return $o;
	}
	
	public static function validate(Ething $ething, $key,array &$attr,User $user,Resource $self = null) {
		$isConstructor = !isset($self);
		$value = &$attr[$key];
		$ret = false;
		switch($key){
			case 'name': // overwride default, only in the root filesystem (ie : no / allowed), no duplicate
				if(is_string($value) && preg_match(self::VALIDATE_NAME, $value)){
					if(!$self || $self->name() != $value){
						// check if a device already have this name
						if($ething->findOne(array(
								'user' => $user->id(),
								'type' => "App",
								'name' => $value
							)))
							throw new \Ething\Exception('an application already has this name');
					}
					$ret = true;
				}
				break;
			case 'content': // only available on creation
				if(!$isConstructor)
					break;
				if(is_string($value)){
					$content = base64_decode($value);
					if($content===false)
						throw new \Ething\Exception('invalid base64 data for the field "content"');
					$ret = function($r) use ($content) {
						$r->setScript($content);
					};
				}
				else if(is_null($value))
					$ret = true;
				unset($attr[$key]); // remove attribute 'content'
				break;
			case 'icon':
				if(is_string($value) || is_null($value)){
					$icon = base64_decode($value);
					if($icon===false)
						throw new \Ething\Exception('invalid base64 data for the field "icon"');
					$size = mb_strlen($icon, '8bit');
					if($size > 64000)
						throw new \Ething\Exception('The icon size must not exceed 64kb.');
					$ret = function($r) use ($icon) {
						$r->setIcon($icon);
					};
					unset($attr[$key]); // remove attribute 'icon'
				}
				break;
			case 'acceptedMime':
				if($isConstructor){
					if(is_null($value))
						$value = array();
					if(is_array($value) && (array_values($value) === $value)){ // is a sequential array ?
						// check that it is an array of mime type
						foreach($value as $i => $v){
							if(!preg_match(self::VALIDATE_MIME_TYPE,$v))
								throw new \Ething\Exception('invalid "acceptedMime" field : invalid mime-type');
						}
						$ret = true;
					}
				}
				
				break;
			default:
				$ret = parent::validate($ething,$key,$attr,$user,$self);
				break;
			
		}
		return $ret;
	}
	
	
	// create a new resource
	public static function create(Ething $ething, User $user, array $attributes, Resource $createdBy = null) {
		
		return parent::createRessource($ething, $user, array_merge(array(
			'acceptedMime' => array()
		), $attributes) , array(
			'size' => 0,
			'mime' => 'x-app/html',
			'hasIcon' => false
		), $createdBy);
		
	}
	
	public function remove() {
		
		// remove all the data from this resource
		$gridfs = $this->getEthingInstance()->db()->getGridFS();
		if(isset($this->_d['_icon']))
			$gridfs->delete($this->_d['_icon']);
		if(isset($this->_d['_content']))
			$gridfs->delete($this->_d['_content']);
		
		
		// remove the resource
		parent::remove();
		
	}
	
	public function setIcon($iconData) {
		$gridfs = $this->getEthingInstance()->db()->getGridFS();
		if(isset($this->_d['_icon'])){
			// remove that file if it exists
			$gridfs->delete($this->_d['_icon']);
			unset($this->_d['_icon']);
		}
		if(!empty($iconData))
			$this->_d['_icon'] = $gridfs->storeBytes($iconData, [
				'filename' => 'App/'.$this->name().'/icon',
				'parent' => $this->id()
			]);
		$this->_d['size'] = $this->computeSize();
		$this->update();
		return true;
	}
	
	
	public function setScript($content) {
		$gridfs = $this->getEthingInstance()->db()->getGridFS();
		if(isset($this->_d['_content'])){
			// remove that file if it exists
			$gridfs->delete($this->_d['_content']);
			unset($this->_d['_content']);
		}
		if(!empty($content)){
			$this->_d['_content'] = $gridfs->storeBytes($content, array(
				'filename' => 'App/'.$this->name().'/content',
				'parent' => $this->id()
			));
		}
		$this->_d['size'] = $this->computeSize();
		$this->update();
		return true;
	}
	
	private function computeSize(){
		$size = 0;
		$gridfs = $this->getEthingInstance()->db()->getGridFS();
		if(isset($this->_d['_content']))
			$size += $gridfs->get($this->_d['_content'])->getSize();
		if(isset($this->_d['_icon']))
			$size += $gridfs->get($this->_d['_icon'])->getSize();
		return $size;
	}
	
	
	public function readScript() {
		$f = isset($this->_d['_content']) ? $this->getEthingInstance()->db()->getGridFS()->get($this->_d['_content']) : null;
		return $f ? $f->getBytes() : '';
	}
	
	public function readIcon() {
		$f = isset($this->_d['_icon']) ? $this->getEthingInstance()->db()->getGridFS()->get($this->_d['_icon']) : null;
		return $f ? $f->getBytes() : null;
	}
	

}
