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
	 *             "scope": {
	 * 		          "type":"string",
	 * 		          "description":"
The allowed scopes for this application (space separated list).
No permissions by default.
"
	 * 		       },
	 *             "apikey": {
	 * 		          "type":"string",
	 * 		          "description":"The apikey for authenticating this app."
	 * 		       },
	 *             "version": {
	 * 		          "type":"string",
	 * 		          "description":"The version of this application"
	 * 		       },
	 * 		       "contentModifiedDate":{  
	 * 		          "type":"string",
	 * 		          "format":"date-time",
	 * 		          "description":"Last time the conten of this resource was modified (formatted RFC 3339 timestamp).",
	 *                "readOnly": true
	 * 		       }
	 * 		   }
	 * 		}
	 *   ]
	 * }
	 */
	 
	
	

class App extends Resource
{
	
	
	public static $defaultAttr = array(
		'scope' => ""
	);
	
	public function apikey() {
		return $this->{'#apikey'};
	}
	
	public function jsonSerialize() {
		$o = parent::jsonSerialize();
		$o['hasIcon'] = $this->hasAttr('_icon');
		return $o;
	}
	
	public static function validate($key, &$value, &$context) {
		$ret = false;
		switch($key){
			/*case 'name': // overwride default, no duplicate
				if(parent::validate($key,$value,$context)){
					
					// check if a device already have this name
					$context['postfns'][] = function($r) {
						// check if there is no other gateway with the same port
						if(count($r->ething->find(array(
							'type' => 'App',
							'name' => $r->get('name'),
							'_id' => array( '$ne' => $r->id() )
						)))>0)
							throw new Exception('an application already has this name');
					};
					
					$ret = true;
				}
				break;*/
			case 'content':
				
				if(is_string($value) || is_null($value)){
					
					$scriptData = base64_decode($value);
					if($scriptData===false)
						throw new Exception('invalid base64 data for the field "content"');
					
					$context['callbacks'][] = function($r) use ($scriptData) {
						$r->setScript($scriptData);
					};
					
					$ret = true;
				}
				unset($context['config'][$key]);// remove this key
				break;
			case 'icon':
				if(is_string($value) || is_null($value)){
					
					$iconData = base64_decode($value);
					if($iconData===false)
						throw new Exception('invalid base64 data for the field "icon"');
					if(mb_strlen($iconData, '8bit') > 128000)
						throw new Exception('The icon size must not exceed 128kb.');
					
					$context['callbacks'][] = function($r) use ($iconData) {
						$r->setIcon($iconData);
					};
					
					$ret = true;
				}
				unset($context['config'][$key]);// remove this key
				break;
			case 'scope':
				$ret = (is_string($value) && Scope::validate($value)) || is_null($value);
				break;
			case 'version':
				if(is_float($value) || is_int($value)) $value = (string) $value;
				$ret = (is_string($value) && strlen($value) < 128) || is_null($value);
				break;
			default:
				$ret = parent::validate($key,$value,$context);
				break;
			
		}
		return $ret;
	}
	
	
	// create a new resource
	public static function create(Ething $ething, array $attributes, Resource $createdBy = null) {
		
		return parent::createRessource($ething, array_merge(self::$defaultAttr, $attributes) , array(
			'size' => 0,
			'mime' => 'x-app/html',
			'#apikey' => ApiKey::generate(),
			'contentModifiedDate' => new \MongoDB\BSON\UTCDateTime()
		), $createdBy);
		
	}
	
	public function remove($removeChildren = false) {
		
		// remove all the data from this resource
		$this->ething->fs->removeFile($this->getAttr('_icon'));
		$this->ething->fs->removeFile($this->getAttr('_content'));
		
		// remove the resource
		parent::remove($removeChildren);
		
	}
	
	
	public function setIcon($iconData) {
		// remove that file if it exists
		$this->ething->fs->removeFile($this->getAttr('_icon'));
		$this->removeAttr('_icon');
		
		if(!empty($iconData)){
			$this->setAttr('_icon', $this->ething->fs->storeFile('App/'.$this->id().'/icon', $iconData, array(
				'parent' => $this->id()
			)));
		}
		$this->setAttr('size', $this->computeSize());
		$this->update();
		return true;
	}
	
	
	public function setScript($content) {
		
		// remove that file if it exists
		$this->ething->fs->removeFile($this->getAttr('_content'));
		$this->removeAttr('_content');
		
		if(!empty($content))
			$this->setAttr('_content', $this->ething->fs->storeFile('App/'.$this->id().'/content', $content, array(
				'parent' => $this->id()
			)));
		$this->setAttr('contentModifiedDate', new \MongoDB\BSON\UTCDateTime());
		$this->setAttr('size', $this->computeSize());
		$this->update();
		return true;
	}
	
	private function computeSize(){
		$size = 0;
		
		$size += $this->ething->fs->getFileSize($this->getAttr('_content'));
		$size += $this->ething->fs->getFileSize($this->getAttr('_icon'));
		
		return $size;
	}
	
	
	public function readScript() {
		$contents = $this->ething->fs->retrieveFile($this->getAttr('_content'));
		return isset($contents) ? $contents : '';
	}
	
	public function readIcon() {
		return $this->ething->fs->retrieveFile($this->getAttr('_icon'));
	}
	

}
