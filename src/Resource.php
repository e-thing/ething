<?php
	
namespace Ething;

	/**
	 * @swagger-definition
	 * "Resource":{ 
	 *   "type": "object",
	 *   "description": "The base representation of a resource object",
	 *   "required":["name"],
	 * 	 "properties":{
	 * 		"id":{  
	 * 		   "type":"string",
	 * 		   "description":"The id of the resource.",
	 *         "readOnly": true
	 * 		},
	 * 		"user":{  
	 * 		   "$ref": "#/definitions/User",
	 * 		   "description":"The owner of the resource.",
	 *         "readOnly": true
	 * 		},
	 * 		"name":{  
	 * 		   "type":"string",
	 * 		   "description":"The name of the resource."
	 * 		},
	 * 		"type":{  
	 * 		   "type":"string",
	 * 		   "description":"The type of the resource.",
	 *         "readOnly": true
	 * 		},
	 * 		"mime":{  
	 * 		   "type":"string",
	 * 		   "description":"The MIME type of the resource.",
	 *         "readOnly": true
	 * 		},
	 * 		"createdDate":{  
	 * 		   "type":"string",
	 * 		   "format":"date-time",
	 * 		   "description":"Create time for this resource (formatted RFC 3339 timestamp).",
	 *         "readOnly": true
	 * 		},
	 * 		"modifiedDate":{  
	 * 		   "type":"string",
	 * 		   "format":"date-time",
	 * 		   "description":"Last time this resource was modified (formatted RFC 3339 timestamp).",
	 *         "readOnly": true
	 * 		},
	 * 		"createdBy":{  
	 * 		   "type":"object",
	 * 	       "properties":{  
	 * 	       	"type":{  
	 * 	       	   "type":"string",
	 * 	       	   "description":"type."
	 * 	       	},
	 * 	       	"id":{  
	 * 	       	   "type":"string",
	 * 	       	   "description":"id."
	 * 	       	}
	 *         },
	 * 		   "description":"The id of the resource responsible of the creation of this resource.",
	 *         "readOnly": true
	 * 		},
	 *      "location": {
	 *         "type":"object",
	 *         "required":["latitude","longitude"],
	 * 	       "properties":{  
	 * 	       	"latitude":{  
	 * 	       	   "type":"number",
	 * 	       	   "description":"the latitude"
	 * 	       	},
	 * 	       	"longitude":{  
	 * 	       	   "type":"number",
	 * 	       	   "description":"the longitude"
	 * 	       	},
	 * 	       	"altitude":{  
	 * 	       	   "type":"number",
	 * 	       	   "description":"the altitude"
	 * 	       	}
	 *         },
	 * 		   "description":"The location of this resource."
	 * 		},
	 * 		"description":{  
	 * 		   "type":"string",
	 * 		   "description":"A description of this resource. Limited to 4096 characters"
	 * 		}
	 * 	 }
	 * }
	 */

	 
interface ResourceInterface {
	static public function create(Ething $ething, User $user, array $attributes, Resource $createdBy = null);
}

abstract class Resource implements \JsonSerializable, ResourceInterface
{
	
	const VALIDATE_NAME = '/^[a-zA-Z0-9 !#$%&\'()+,\-.;=@^_`{}]+(\\/[a-zA-Z0-9 !#$%&\'()+,\-.;=@^_`{}]+)*$/';
	
	private $ething = null;
	
	private $updatePrevented = false;
	
	protected $_d = null; // the mongodb document associated to the current resource
	
	public static $defaultAttr = array(
		'name'   => null,
		'data'       => null,
		'description'=> null,
		'rules' => array(),
		'location' => null // the location of this resource
	);
	
	public function __construct(Ething $ething, $doc)
	{
		$this->ething = $ething;
		$this->_d = $doc;
	}
	
	public function getEthingInstance(){
		return $this->ething;
	}
	
	public function id() {
		return $this->_d['_id'];
	}
	
	public function user() {
		return $this->ething->findOneUserById($this->_d['user']);
	}
	
	public function mime() {
		return $this->_d['mime'];
	}
	
	public function createdBy() {
		return (isset($this->_d['createdBy'])) ? $this->ething->get($this->_d['createdBy']['id']) : null;
	}
	
	public function name() {
		return basename($this->_d['name']);
	}
	
	public function type() {
		return $this->_d['type'];
	}
	
	public function createdDate() {
		return $this->_d['createdDate']->sec;
	}
	
	public function modifiedDate() {
		return $this->_d['modifiedDate']->sec;
	}
	
	public function rules() {
		$rules = array();
		foreach($this->_d['rules'] as &$ruledata)
			$rules[] = new Rule($ruledata, $this);
		return $rules;
	}
	
	public function dispatchEvent($eventType, array $customData = array()) {
		if(!empty($this->_d['rules'])){
			
			if($this->ething->isEventsDelayed()){
				$this->ething->delayEvent($this,$eventType,$customData);
			}
			else {
				$eventClass = 'Ething\\Event\\'.$eventType;
				if(class_exists($eventClass)){
					$event = new $eventClass($this,$customData);
					$rules = $this->rules();
					foreach($rules as $rule){
						$rule->execute($event, $errors);
						$this->ething->dispatchEventException($errors);
					}
				}
				else
					throw new Exception('Unknown event "'.$eventType.'"');
			}
		}
	}
	
	public function location() {
		return $this->_d['location'];
	}
	
	public function jsonSerialize() {
		return array_merge(self::r_encode($this->_d),array(
			'id' => (string)$this->_d['_id'],
			'user' => $this->user()
		));
	}
	
	
	// validate the value at the key $key in an associative array $attr
	// this function is used in validation of constructing and setting (that's why it is a static function)
	// if $self is set, it means that this function is called for updating the property, else this function is called for constructing the resource
	protected static function validate(Ething $ething, $key,array &$attr,User $user,Resource $self = null) {
		//$isConstructor = !isset($self);
		$value = &$attr[$key];
		$ret = false; // return false by default
		switch($key){
			case 'name':
				$ret = (is_string($value) && preg_match(self::VALIDATE_NAME, $value));
				break;
			case 'data':
				if(strlen(json_encode($value)) > 4096)
					throw new \Ething\Exception("the field '{$key}' is too big.");
				$ret = true;
				break;
			case 'description':
				if(is_null($value))
					$ret = true;
				else if(is_string($value)){
					if(strlen($value) > 4096)
						throw new \Ething\Exception("the field '{$key}' is limited to 4096 characters.");
					$ret = true;
				}
				break;
			case 'rules':
				// sanitize
				if(is_null($value))
					$value = array();
				
				if(is_array($value)){
					$rules = $value;
					$ret = function($r) use ($rules) {
						foreach($rules as $k => &$rule){
							$rule = json_decode(json_encode($rule), true); // cast object into associative array
							if(!is_array($rule) || !Rule::check($rule,$r)){
								throw new Exception("Invalid rules #{$k}");
							}
						}
						return $rules;
					};
				}
				break;
			case 'location':
				if(is_object($value))
					$value = (array)$value;
				if(is_array($value) && isset($value['longitude']) && isset($value['latitude'])){
					foreach($value as $key => $v){
						switch($key){
							case 'longitude':
							case 'latitude':
							case 'altitude':
								if(!(is_int($v) || is_float($v)))
									throw new \Ething\Exception("invalid 'location.{$key}' field, must be a number");
								break;
							default:
								throw new \Ething\Exception("invalid 'location.{$key}' field");
						}
					}
					$ret = true;
				}
				else if(is_null($value)){
					$ret = true;
				}
				break;
			default:
				throw new \Ething\Exception('invalid field "'.$key.'"');
		}
		return $ret;
	}
	
	public function set($name, $value = null) {
		
		$props = is_array($name) ? $name : array( $name => $value );
		
		$s = true;
		$callbacks = array();
		$keys = array_keys($props);
		$user = $this->user();
		foreach($keys as $key){
			
			$res=false;
			try {
				$res = static::validate($this->ething,$key,$props,$user,$this);
				if(!$res)
					throw new Exception('Invalid value');
			}
			catch(Exception $e){
				throw new Exception("[{$key}] ".$e->getMessage(),$e->getCode(),$e);
			}
			
			if(is_callable($res))
				$callbacks[$key] = $res;
		}
		$this->_d = array_merge($this->_d,$props);
		
		// post treatment
		$this->updatePrevented = true;
		try {
			foreach($callbacks as $key => $callback){
				$res = $callback($this);
				if(isset($res)) $this->_d[$key] = $res;
			}
		} catch (\Exception $e) {
			$this->updatePrevented = false;
			throw new Exception("[{$key}] ".$e->getMessage(),$e->getCode(),$e);
		}
		
		// update only if every thing is successfull
		$this->updatePrevented = false;
		$this->update();
		
		return true;
	}
	
	public function remove() {
		
		$c = $this->ething->db()->selectCollection("resources");
		$c->remove(array('_id' => $this->id()), array('justOne' => true));
		$this->_d = null;
		
	}
	
	public function update($tsUpdate = true) {
		if($this->updatePrevented) return;
		if($tsUpdate) $this->_d['modifiedDate'] = new \MongoDate(); // update the modification time
		$c = $this->ething->db()->selectCollection("resources");
		$c->save($this->_d);
	}
	
	// create a new resource
	// the values of the $meta associative array will not be validated unlike the $attr associative array
	// so the $meta array is intended only for internal purpose
	protected static function createRessource(Ething $ething, User $user, array $attr, array $meta=array(), Resource $createdBy = null) {
		$now = new \MongoDate();
		$class = get_called_class();
		$type = preg_replace('/^Ething\\\/','',$class); // remove the namespace
		
		$attr = array_merge(self::$defaultAttr,$attr);
		
		$callbacks = array();
		
		// validation of the attributes 
		$keys = array_keys($attr);
		foreach($keys as $key){
			
			$res=false;
			try {
				$res = call_user_func_array($class.'::validate',array($ething,$key,&$attr,$user,null));
				if(!$res)
					throw new Exception('Invalid value');
			}
			catch(Exception $e){
				throw new Exception("[{$key}] ".$e->getMessage(),$e->getCode(),$e);
			}
			
			if(is_callable($res))
				$callbacks[$key] = $res;
		}
		
		$mime = 'x-'.strtolower($type).'/x-'.strtolower($type);
		
		$attr = array_merge($attr,array(
			'user'       => $user->id(),
			'type'       => $type,
			'createdBy' => isset($createdBy) ? array('id'=>$createdBy->id(),'type'=>$createdBy->type()) : null,
			'createdDate' => $now,
			'modifiedDate' => $now,
			'mime' => $mime
		),$meta);
		
			
		$c = $ething->db()->selectCollection("resources");
		
		$err = false;
		try {
			$attr['_id'] = ShortId::generate();
			$c->insert($attr);
		}
		catch(\Exception $e) {
			//echo "message d'erreur : ".$e->getMessage()."\n";
			//echo "code de l'erreur : ".$e->getCode()."\n";
			// code 11000 on duplicate error
			throw new \Ething\Exception('internal error');
		}
		
		$instance = new $class($user->getEthingInstance(),$attr);
		
		// post treatment
		try {
			foreach($callbacks as $key => $callback){
				$res = $callback($instance);
				if(isset($res)) $instance->_d[$key] = $res;
			}
		} catch (\Exception $e) {
			// remove this resource on error
			$instance->remove();
			throw new Exception("[{$key}] ".$e->getMessage(),$e->getCode(),$e);
		}
		
		return $instance;
	}
	
	private static function r_encode(array $data){
		$o=array();
		foreach($data as $k => $v)
			if($k[0] != '_'){
				if($v instanceof \MongoDate)
					$o[$k] = date(\DateTime::RFC3339, $v->sec);
				else if(is_array($v))
					$o[$k] = self::r_encode($v);
				else
					$o[$k] = $v;
			}
		return $o;
	}

}
