<?php
	
namespace Ething;

	/**
	 * @swagger-definition
	 * "Resource":{ 
	 *   "type": "object",
	 *   "description": "The base representation of a resource object",
	 *   "required":["name"],
	 *   "discriminator": "type",
	 * 	 "properties":{
	 * 		"id":{  
	 * 		   "type":"string",
	 * 		   "description":"The id of the resource.",
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
	 * 		   "description":"The id of the resource responsible of the creation of this resource, or null.",
	 *         "readOnly": true
	 * 		},
	 * 		"description":{  
	 * 		   "type":"string",
	 * 		   "description":"A description of this resource. Limited to 4096 characters"
	 * 		},
	 * 		"data":{  
	 * 		   "type":"object",
	 * 		   "description":"A collection of arbitrary key-value pairs. Entries with null values are cleared in update. The keys must not be empty or longer than 64 characters, and must contain only the following characters : letters, digits, underscore and dash. Values must be either a string or a boolean or a number"
	 * 		},
	 * 		"public":{  
	 * 		   "type":"boolean",
	 * 		   "description":"False: this resource is not publicly accessible. 'readonly': this resource is accessible for reading by anyone. 'readwrite': this resource is accessible for reading and writing by anyone."
	 * 		}
	 * 	 }
	 * }
	 */

	 
interface ResourceInterface {
	static public function create(Ething $ething, array $attributes, Resource $createdBy = null);
}

abstract class Resource implements \JsonSerializable, ResourceInterface
{
	
	const VALIDATE_NAME = '/^[a-zA-Z0-9 !#$%&\'()+,\-.;=@^_`{}]+(\\/[a-zA-Z0-9 !#$%&\'()+,\-.;=@^_`{}]+)*$/';
	
	public $ething = null;
	
	private $_d = null; // the mongodb document associated to the current resource
	
	private $dirtyFields = array();
	
	private $updateDisabled = 0;
	
	protected static $defaultAttr = array(
		'name'   => null,
		'data'       => null,
		'description'=> null
	);
	
	public function __construct(Ething $ething, $doc)
	{
		$this->ething = $ething;
		$this->_d = $doc;
		$this->_d['data'] = (object) $this->_d['data'];
	}
	
	public function __toString(){
		return sprintf("%s {#%s}", $this->name(), $this->id());
	}
	
	public function id() {
		return $this->_d['_id'];
	}
	
	public function createdBy() {
		return $this->ething->get($this->_d['createdBy']['id']);
	}
	
	public function name() {
		return $this->_d['name'];
	}
	
	public function type() {
		return $this->_d['type'];
	}
	
	public function baseType() {
		$pt = explode('\\', $this->_d['type']);
		return $pt[0];
	}
	
	public function isTypeof($type) {
		return \is_a($this, '\\Ething\\'.$type);
	}
	
	public function jsonSerialize() {
		return Ething::r_encode($this->_d);
	}
	
	public function dispatchSignal(Event\Signal $signal) {
		$this->ething->dispatchSignal($signal);
	}
	
	protected function getAttr($name) {
		return isset($this->_d[$name]) ? $this->_d[$name] : null;
	}
	
	protected function hasAttr($name) {
		return isset($this->_d[$name]);
	}
	
	protected function setAttr($name, $value) {
		if(!isset($this->_d[$name]) || $this->_d[$name] !== $value || is_object($value) || is_array($value)){
			$this->_d[$name] = $value;
			$this->setDirtyAttr($name);
			return true;
		}
		return false;
	}
	
	protected function removeAttr($name) {
		if(isset($this->_d[$name])){
			unset($this->_d[$name]);
			$this->setDirtyAttr($name);
		}
	}
	
	protected function setDirtyAttr($name) {
		if(!in_array($name, $this->dirtyFields))
			$this->dirtyFields[] = $name;
	}
	
	/*
	
	the validation is a 3 steps process :
	  - validate each field separately (call the static 'validate' function), the validation stops if an exception is thrown or if false is returned
	  - execute the 'postfns' functions, the validation stops if an exception is thrown or if false is returned
	  - the validation has succeeded, the callback functions are executed and the resource is updated !
	
	$context is an associative array containing the following properties :
	  'ething' : the ething instance
	  'resourceType' : the type of the resource to be modified/created
	  'resource' : only available when setting a property on an existing resource
	  'createdBy' : only available on resource creation validation
	  'postfns' : {function($resource)[]} a collection of functions that are executed after validating every fields. Never execute update() inside those functions (use instead the 'callbacks' property). If these functions throw an error, the validation process fail.
	  'callbacks' : {function($resource)[]} a collection of functions that are executed only once the validation has succeeded. Should never fail.
	  'config' : the options to be validated.
	*/
	protected static function validate($key, &$value, &$context) {
		$ret = false; // return false by default
		switch($key){
			case 'name':
				$ret = (is_string($value) && preg_match(self::VALIDATE_NAME, $value));
				break;
			case 'data':
				
				$reset = !isset($context['resource']);
				
				if($value === null){
					$reset = true;
					$value = new \stdClass();
				}
				if(is_array($value))
					$value = (object)$value;
				if(!is_object($value))
					throw new Exception('must be an associative array');
				
				$keysToRemove = array();
				
				// check the key value
				foreach(get_object_vars($value) as $k => $v){
					
					// check the key
					if(!preg_match('/^[a-zA-Z0-9_\-]{1,64}$/',$k))
						throw new Exception("the keys of the attribute 'data' must not be empty or longer than 64 characters, and must contain only the following characters : letters, digits, underscore and dash.");
					
					if($v===null){
						// remove that key
						$keysToRemove[] = $k;
						unset($value->$k);
						continue;
					}
					
					// check the value, only scalara value accepted
					if(!(is_int($v) || is_string($v) || is_bool($v) || is_float($v)))
						throw new Exception("invalid value for key'{$k}'");
				}
				
				$ret = true;
				
				if($reset){
					// set the values as is
				} else {
					// extend the current values
					$currentValues = $context['resource']->data;
					
					foreach($keysToRemove as $k){
						unset($currentValues->$k);
					}
					$extendedValues = (object)array_merge((array)$currentValues, (array)$value);
					$value = $extendedValues;
				}
				
				break;
			case 'description':
				if(is_null($value))
					$ret = true;
				else if(is_string($value)){
					if(strlen($value) > 4096)
						throw new Exception("the field '{$key}' is limited to 4096 characters.");
					$ret = true;
				}
				break;
			case 'public':
				$ret = in_array($value, array(false,"readonly","readwrite"), true);
				break;
			default:
				throw new Exception('unknown field "'.$key.'"');
		}
		return $ret;
	}
	
	
	public function get($name, $default = null) {
		if($name[0] == '_') return $default;
		if($name === 'id') $name = '_id';
		if($this->hasAttr($name)){
			$v = $this->getAttr($name);
			if($v instanceOf \MongoDB\BSON\UTCDateTime)
				return $v->toDateTime()->getTimestamp();
			return $v;
		} else return $default;
	}
	
	public function __get ( $name ){
		return $this->get($name);
	}
	
	public function __isset ( $name ){
		if($name === 'id') $name = '_id';
		return $this->hasAttr($name) && $name[0] != '_';
	}
	
	public function set($name, $value = null) {
		
		$props = is_array($name) ? $name : array( $name => $value );
		
		$keys = array_keys($props);
		$context = array(
			'ething' => $this->ething,
			'resourceType' => $this->type,
			'resource' => $this,
			'postfns' => array(),
			'callbacks' => array(),
			'config' => &$props
		);
		
		// field validation
		foreach($keys as $key){
			if(!isset($props[$key]) && !is_null($props[$key])) continue;
			
			try {
				if(!static::validate($key,$props[$key],$context))
					throw new Exception('Invalid value');
			}
			catch(Exception $e){
				throw new Exception("[{$key}] ".$e->getMessage(),$e->getCode(),$e);
			}
		}
		$save = $this->_d;
		$this->_d = array_merge($this->_d,$props);
		
		// post checks
		try {
			foreach($context['postfns'] as $fn){
				if($fn($this,$context)===false) throw new Exception('Invalid value');
			}
			
			$this->dirtyFields = array_unique(array_merge($this->dirtyFields,Helpers::array_diff($save,$this->_d)));
			
		} catch (\Exception $e) {
			$this->_d = $save;
			throw new Exception("[{$key}] ".$e->getMessage(),$e->getCode(),$e);
		}
		
		$this->update();
		
		// callbacks
		foreach($context['callbacks'] as $fn){
			$fn($this,$context);
		}
		
		return true;
	}
	
	/* internal data getter/setter */
	
	public function getData($name, $default = null){
		return isset($this->data->$name) ? $this->data->$name : $default;
	}
	
	public function setData($name, $value = null){
		return $this->set('data',is_array($name) ? $name : array(
			$name => $value
		));
	}
	
	public function hasData($name){
		return isset($this->data->$name);
	}
	
	public function removeData($name){
		return $this->set('data',array(
			$name => null
		));
	}
	
	public function removeParent(){
		$child->setAttr('createdBy', null);
		$child->update();
	}
	
	
	public function remove($removeChildren = false) {
		
		$id = $this->id();
		
		$c = $this->ething->db()->selectCollection("resources");
		$c->deleteOne(array('_id' => $id));
		
		$this->ething->dispatchSignal(Event\ResourceDeleted::emit($this));
		
		$this->_d = null;
		
		$children = $this->ething->find(array(
			'createdBy.id' => $id
		));
		
		foreach($children as $child){
			if($removeChildren===true){
				$child->remove($removeChildren);
			} else {
				// remove the relationship
				$child->removeParent();
			}
		}
		
	}
	
	protected function setUpdateEnableState($enable){
		if($enable){
			if($this->updateDisabled>0) $this->updateDisabled--;
		} else {
			$this->updateDisabled++;
		}
	}
	
	protected function update($force = false) {
		if($this->updateDisabled===0 && ($force || count($this->dirtyFields))){
			$this->setAttr('modifiedDate', new \MongoDB\BSON\UTCDateTime()); // update the modification time
			$c = $this->ething->db()->selectCollection("resources");
			$c->replaceOne(array('_id' => $this->id()), $this->_d);
			$this->ething->dispatchSignal(Event\ResourceMetaUpdated::emit($this, $this->dirtyFields));
			/*$this->ething->dispatchSignal(Event\ResourceMetaUpdated::emit($this, array_filter($this->dirtyFields,function($f){
				return $f[0]!=='_';
			})));*/
			$this->dirtyFields = array();
		}
	}
	
	// create a new resource
	// the values of the $meta associative array will not be validated unlike the $attr associative array
	// so the $meta array is intended only for internal purpose
	protected static function createRessource(Ething $ething, array $attr, array $meta=array(), Resource $createdBy = null) {
		$now = new \MongoDB\BSON\UTCDateTime();
		$class = get_called_class();
		$type = preg_replace('/^Ething\\\/','',$class); // remove the namespace
		
		$attr = array_merge(self::$defaultAttr,$attr);
		
		$context = array(
			'ething' => $ething,
			'resourceType' => $class,
			'createdBy' => $createdBy,
			'postfns' => array(),
			'callbacks' => array(),
			'config' => &$attr
		);
		
		// validation of the attributes 
		$keys = array_keys($attr);
		foreach($keys as $key){
			if(!array_key_exists($key, $attr)) continue;
			try {
				if(!call_user_func_array($class.'::validate',array($key,&$attr[$key],&$context)))
					throw new Exception('Invalid value');
			}
			catch(Exception $e){
				throw new Exception("[{$key}] ".$e->getMessage(),$e->getCode(),$e);
			}
		}
		
		$attr = array_merge($attr,array(
			'type'       => $type,
			'createdBy' => isset($createdBy) ? array('type'=>$createdBy->type(), 'id'=>$createdBy->id()) : null,
			'createdDate' => $now,
			'modifiedDate' => $now
		),$meta);
		
		
		$attr['_id'] = ShortId::generate();
		$instance = new $class($ething,$attr);
		
		// post checks
		try {
			foreach($context['postfns'] as $fn){
				if($fn($instance,$context)===false) throw new Exception('Invalid value');
			}
		} catch (\Exception $e) {
			throw new Exception("[{$key}] ".$e->getMessage(),$e->getCode(),$e);
		}
		
		// insertion
		$c = $ething->db()->selectCollection("resources");
		$err = false;
		try {
			$c->insertOne($instance->_d);
		}
		catch(\Exception $e) {
			// code 11000 on duplicate error
			throw new Exception('internal error');
		}
		
		
		// callbacks
		foreach($context['callbacks'] as $fn){
			$fn($instance,$context);
		}
		
		$instance->update();
		
		$ething->dispatchSignal(Event\ResourceCreated::emit($instance));
		
		return $instance;
	}
	
	
	public function match($expression){
		return boolval( $this->ething->findOne( array(
			'$and' => array(
				array( '_id' => $this->id() ),
				$this->ething->resourceQueryParser()->parse($expression) // use the parser because of the 'me' constant !
			)
		) ) );
	}
	
	public function refresh($keepDirtyFields = false){
		$c = $this->ething->db()->selectCollection("resources");
		$doc = (array)$c->findOne(array('_id' => $this->id()));
		$doc['data'] = (object) $doc['data'];
		
		if($keepDirtyFields){
			foreach($this->dirtyFields as $field){
				unset($doc[$field]);
			}
			$this->_d = array_merge($this->_d, $doc);
		} else {
			$this->dirtyFields = array();
			$this->_d = $doc;
		}
		
	}
	
}
