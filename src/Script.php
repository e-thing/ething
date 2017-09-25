<?php
	
namespace Ething;

	/**
	 * @swagger-definition
	 * "Script":{ 
	 *   "type": "object",
	 *   "description": "Script resource representation. Inherit File class.",
	 * 	 "allOf": [
	 * 		{
	 * 		   "$ref":"#/definitions/File"
	 * 		},
	 * 		{  
	 * 		   "type": "object",
	 * 		   "properties":{
	 *             "scope": {
	 * 		          "type":"string",
	 * 		          "description":"
The allowed scopes for this script (space separated list).
No permissions by default.
"
	 * 		       },
	 *             "apikey": {
	 * 		          "type":"string",
	 * 		          "description":"The apikey for authenticating this script."
	 * 		       }
	 * 		   }
	 * 		}
	 *   ]
	 * }
	 */
	 
	
	

class Script extends File
{
	
	
	public static $defaultAttr = array(
		'scope' => ""
	);
	
	public function apikey() {
		return $this->{'#apikey'};
	}
	
	public static function validate($key, &$value, &$context) {
		$ret = false;
		switch($key){
			case 'scope':
				$ret = (is_string($value) && Scope::validate($value)) || is_null($value);
				break;
			default:
				$ret = parent::validate($key,$value,$context);
				break;
			
		}
		return $ret;
	}
	
	
	// create a new resource
	public static function create(Ething $ething, array $attributes, Resource $createdBy = null) {
		
		return parent::createRessource($ething, array_merge(parent::$defaultAttr, self::$defaultAttr, $attributes) , array(
			'size' => 0,
			'isText' => true, // will be updated through the 'name' validator callback !
			'mime' => '' // will be updated through the 'name' validator callback !
			'#apikey' => ApiKey::generate()
		), $createdBy);
		
	}
	
	
	public function execute($arguments = ''){
		return ScriptEngine\runFromFile($this, $arguments);
	}

}
