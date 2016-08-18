<?php


	/**
	 * @swagger-definition
	 * "Table":{ 
	 *   "type": "object",
	 *   "description": "Table resource representation",
	 * 	 "allOf": [
	 * 		{
	 * 		   "$ref":"#/definitions/Resource"
	 * 		},
	 * 		{  
	 * 		   "type": "object",
	 * 		   "properties":{
	 *             "expireAfter": {
	 * 		          "type":"number",
	 * 		          "description":"The amount of time (in seconds) after which a records will be automatically removed. Set it to null or 0 to disable this feature."
	 * 		       },
	 *             "maxLength": {
	 * 		          "type":"number",
	 * 		          "description":"The maximum of records allowed in this table. When this number is reached, the oldest records will be removed to insert the new ones (first in, first out). Set it to null or 0 to disable this feature."
	 * 		       },
	 *             "length": {
	 * 		          "type":"number",
	 * 		          "description":"The number of records in the table",
	 *                "readOnly": true
	 * 		       },
	 *             "keys": {
	 * 		          "type":"object",
	 * 		          "description":"A key/value object where the keys correspond to the fields available in this table, and the corresponding value is the number of rows where the field is set. __The default keys ('_id' and 'date' are not listed)__",
	 *                "readOnly": true
	 * 		       }
	 * 		   }
	 * 		}
	 *   ]
	 * }
	 */

namespace Ething;


define('FIELD_VALID_CHAR','a-zA-Z0-9_\-');
define('VALIDATE_FIELD','/^['.FIELD_VALID_CHAR.']{1,64}$/');


class Table extends Resource
{
	public static $defaultAttr = [
		'maxLength' => 5000,
		'expireAfter' => null,
	];
	
	const FIELD_VALID_CHAR = FIELD_VALID_CHAR;
	const VALIDATE_FIELD = VALIDATE_FIELD;
	private static $reservedKeys = array('_t','_id');
	
	const INVALID_FIELD_NONE = 0;
	const INVALID_FIELD_RENAME = 1;
	const INVALID_FIELD_SKIP = 2;
	const INVALID_FIELD_STOP = 4;
	
	
	private $isDataDirty = false;
	
	
	public function length() {
		return $this->_d['length'];
	}
	
	public function maxLength() {
		return $this->_d['maxLength'];
	}
	
	public function expireAfter() {
		return $this->_d['expireAfter'];
	}
	
	public function keys() {
		return $this->_d['keys'];
	}
	
	
	public function jsonSerialize() {
		return array_merge(parent::jsonSerialize(),array(
			'keys' => $this->_d['keys']
		));
	}
	
	
	const TIMESTAMP = 0;
	public static $dateFormat = \DateTime::RFC3339;
	// return an object
	private static function docSerialize($doc) {
		if(isset($doc['_id'])){
			$doc['id'] = $doc['_id'];
			unset($doc['_id']);
		}
		if(isset($doc['date']))
			$doc['date'] = self::$dateFormat===self::TIMESTAMP ? $doc['date']->sec : date(self::$dateFormat, $doc['date']->sec);
		return (object)$doc;
	}
	
	public static function validate(Ething $ething, $key,array &$attr,User $user,Resource $self = null) {
		$isConstructor = !isset($self);
		$value = &$attr[$key];
		$ret = false;
		switch($key){
			case 'expireAfter':
				if($value===0) $value=null;
				$ret = is_null($value) || (is_int($value) && $value>0);
				break;
			case 'maxLength':
				if($value===0) $value=null;
				$ret = is_null($value) || (is_int($value) && $value>0);
				break;
			case 'content': // only available on creation
				if(!$isConstructor)
					break;
				if(is_array($value)){
					$content = $value;
					static::sanitizeData($content, $keys);
					$ret = function($r) use ($content,$keys) {
						$r->importRaw($content,$keys);
					};
				}
				else if(is_null($value))
					$ret = true;
				unset($attr[$key]); // remove attribute 'content'
				break;
			default:
				$ret = parent::validate($ething,$key,$attr,$user,$self);
				break;
		}
		return $ret;
	}
	
	
	public function remove() {
		
		// remove all the data from this table
		$this->clear();
		
		// remove the resource
		parent::remove();
		
	}
	
	public function clear() {
		
		// remove all the data from this table
		$c = $this->getEthingInstance()->db()->selectCollection($this->user()->dataCollectionName());
		
		try {
			$c->remove(array('_t' => $this->id()));
		}
		catch(Exception $e){}
		
		$this->_d['keys'] = array();
		$this->_d['length'] = 0;
		$this->update();
		
	}
	
	// is called regularly
	public function checkExpiredData() {
		
		// remove the expired data in the current table
		if($this->expireAfter()){
			$c = $this->getEthingInstance()->db()->selectCollection($this->user()->dataCollectionName());
			$cursor = $c->find(array(
				'_t' => $this->id(),
				'date' => array(
					'$lt' => (new \MongoDate(time() - $this->expireAfter()))
				)
			), array(
				'_id' => true
			));
			
			$idToBeRemoved = [];
			foreach ($cursor as $doc)
				$idToBeRemoved[] = $doc['_id'];
			
			if(count($idToBeRemoved))
				$this->remove_rows($idToBeRemoved);
		}
		
	}
	
	
	public function stats() {
		
		$keys = [];
		$length = 0;
		
		$c = $this->getEthingInstance()->db()->selectCollection($this->user()->dataCollectionName());
		$cursor = $c->find(array('_t' => $this->id()),array(
			'_id' => false,
			'date' => false,
			'_t' => false
		));
		
		foreach ($cursor as $doc) {
			foreach ($doc as $k => $v) {
				if($k[0]!='_'){
					if(!isset($keys[$k])) $keys[$k]=0;
					$keys[$k]++;
				}
			}
			//$keys = array_merge($keys,array_diff(array_keys($doc),$keys));
			$length++;
		}
		
		return [
			'keys' => $keys,
			'length' => $length
		];
	}
	
	// return the number of document removed
	public function remove_rows(array $row_ids) {
		
		$nb = 0;
		
		if(!is_array($row_ids) && !($row_ids instanceof Traversable))
			$row_ids = [$row_ids];
		
		$c = $this->getEthingInstance()->db()->selectCollection($this->user()->dataCollectionName());
		
		$keys = $this->_d['keys'];
		
		foreach($row_ids as $row_id){
			
			try {
				$removedDoc = $c->findAndModify(array(
					'_id' => $row_id,
					'_t' => $this->id()
				),null,null,array('remove'=>true));
			
				// update the key count
				foreach($removedDoc as $field => $v){
					if(isset($keys[$field])){
						$keys[$field]--;
						if($keys[$field]<=0)
							unset($keys[$field]);
					}
				}
				
				$nb++;
			}
			catch(Exception $e) {} // invalid id or unable to remove the document
		}
		
		if($nb){
			$this->_d['keys'] = $keys;
			$this->_d['length']-=$nb;
			$this->update();
		}
		
		return $nb;
	}
	
	
	
	private static function sanitizeData(array &$dataArray, &$keys = null, $invalidFields = self::INVALID_FIELD_RENAME, $skipError = true){
		
		if(!is_array($keys))
			$keys = array();
		
		$length = 0;
		
		foreach($dataArray as $i => &$data){
			
			try{
				if(is_object($data))
					$data = (array)$data;
				else if(!is_array($data))
					throw new \Ething\Exception('invalid data');
				
				
				// key/field validation
				unset($data['id']); // will be auto generated !
				foreach($data as $k => $v){
					
					if(!(is_int($v) || is_float($v) || is_string($v) || is_bool($v) || is_null($v)))
						throw new \Ething\Exception('The value must either be a string or a number or a boolean or null.');
					
					if(!preg_match(self::VALIDATE_FIELD,$k)){
						
						switch($invalidFields){
							
							case self::INVALID_FIELD_SKIP:
								unset($data[$k]);
								break;
							
							case self::INVALID_FIELD_RENAME:
								unset($data[$k]);
								$k = strlen($k) ? preg_replace('/[^'.self::FIELD_VALID_CHAR.']+/','_',$k) : '_';
								$data[$k] = $v;
								break;
								
							default:
								throw new \Ething\Exception('invalid key "'.$k.'", must only contain alphanumeric, underscore or dashes characters. Keys must not be empty');
							
						}
						
					}
					
					if(in_array($k,static::$reservedKeys)){
						switch($invalidFields){
							
							case self::INVALID_FIELD_SKIP:
								unset($data[$k]);
								break;
							
							case self::INVALID_FIELD_RENAME:
								unset($data[$k]);
								$k = $k.'_';
								$data[$k] = $v;
								break;
								
							default:
								throw new \Ething\Exception('invalid key "'.$k.'", must not be one of the following values '.implode(',',static::$reservedKeys));
							
						}
					}
					
					if($k=='date'){
						// check the format
						if($t = strtotime($v))
							$data[$k] = new \MongoDate($t);
						else
							throw new \Ething\Exception('Invalid date "'.$v.'"');
					}
					
				}
				
				// update the key count
				foreach(array_keys($data) as $k){
					switch($k){
						case 'date':
							break;
						default:
							if(!isset($keys[$k]))
								$keys[$k] = 0;
							$keys[$k]++;
							break;
					}
				}
				
				// add date if not already set
				if(!isset($data['date'])) $data['date'] = new \MongoDate(); // add the insertion date for that document
				
				
				$length++;
				
			}
			catch(\Exception $e){
				if(!$skipError){
					// forward the exception
					throw $e;
				}
				else {
					unset($dataArray[$i]);
				}
			}
		}
		
		
		return $length;
	}
	
	public function insert(array $data, $invalidFields = self::INVALID_FIELD_RENAME) {
		if(!empty($data)){
			
			// add the data into the tableData
			$keys = $this->_d['keys'];
			$length = $this->_d['length'];
			
			// sanitize the incoming data
			$dataArray = array($data);
			$length += static::sanitizeData($dataArray,$keys,$invalidFields,false);
			
			// add meta data
			foreach($dataArray as &$data){
				$data['_id'] = ShortId::generate();
				$data['_t'] = $this->id();
			}
			
			// insert the data
			$c = $this->getEthingInstance()->db()->selectCollection($this->user()->dataCollectionName());
			$c->insert($dataArray[0]);
			
			// remove extra row
			if( $this->maxLength() && $length > $this->maxLength() ){
				// remove the oldest document
				$removedDoc = $c->findAndModify(array(
					'_t' => $this->id()
				),null,null,array(
					'sort' => array('date'=>1),
					'remove'=>true
				));
				
				$length--;
				
				// update the key count
				foreach($removedDoc as $field => $v){
					if(isset($keys[$field])){
						$keys[$field]--;
						if($keys[$field]<=0)
							unset($keys[$field]);
					}
				}
			}
			
			$this->_d['length'] = $length;
			$this->_d['keys'] = $keys;
			$this->update();
			
			
			// generate an event
			$this->dispatchEvent('TableDataAdded',self::docSerialize($dataArray[0]));
			
		}
	}
	
	
	public function import(array $dataArray = array(), $invalidFields = self::INVALID_FIELD_RENAME, $skipError = true){
		
		// remove extra row
		if( $this->maxLength() && count($dataArray) > $this->maxLength() ){
			$dataArray = array_slice($dataArray, - $this->maxLength());
		}
		
		
		// remove any previous content
		$this->clear();
		
		// sanitize the incoming data
		$this->_d['length'] = static::sanitizeData($dataArray,$this->_d['keys'],$invalidFields,$skipError);
		
		if(!empty($dataArray)){
			// add meta data
			foreach($dataArray as &$data){
				$data['_id'] = ShortId::generate();
				$data['_t'] = $this->id();
			}
			
			// insert the data
			$c = $this->getEthingInstance()->db()->selectCollection($this->user()->dataCollectionName());
			$c->batchInsert($dataArray);
		}
		
		$this->update();
		
		return true;
	}
	
	// no sanitize is made, internal purpose only
	private function importRaw(array $dataArray, array $keys){
		if(empty($dataArray))
			return true;
		
		// remove extra row
		if( $this->maxLength() && count($dataArray) > $this->maxLength() ){
			$dataArray = array_slice($dataArray, - $this->maxLength());
		}
		
		// remove any previous content
		$this->clear();
		
		// add meta data
		foreach($dataArray as &$data){
			$data['_id'] = ShortId::generate();
			$data['_t'] = $this->id();
		}
		
		// insert the data
		$c = $this->getEthingInstance()->db()->selectCollection($this->user()->dataCollectionName());
		$c->batchInsert($dataArray);
		
		// update the metadata
		$this->_d['length'] = count($dataArray);
		foreach($keys as $k => $c){
			if(!isset($this->_d['keys'][$k]))
				$this->_d['keys'][$k] = 0;
			$this->_d['keys'][$k] += $c;
		}
		$this->update();
		
		return true;
	}
	
	
	public function get($id, array $fields = null)
	{
		
		// return only specific fields
		$_fields = array();
		if(isset($fields)){
			$_fields['_id'] = false; // by default, the '_id' field is shown
			foreach($fields as $field){
				// handle special key '_id' 
				if($field==='id')
					$_fields['_id'] = true;
				else if(!in_array($field,static::$reservedKeys))
					$_fields[$field] = true;
			}
		}
		else {
			// never show the table id
			$_fields['_t'] = false;
		}
		
		
		$c = $this->getEthingInstance()->db()->selectCollection($this->user()->dataCollectionName());
		$r = $c->findOne(array('_id' => $id,'_t' => $this->id()),$_fields);
		
		return (!is_null($r)) ? self::docSerialize($r) : null;
	}
	
	public function select($start = 0, $length = null, array $fields = null, $sort = null, $query = null)
	// If start is non-negative, the returned selection will start at the start'th position in the table, counting from zero.
	// If start is negative, the returned selection will start at the start'th position from the end of the table.
	// If length is given and is positive, the selection returned will contain at most length lines beginning from start.
	// If length is omitted, the selection starting from start until the end of the table will be returned.
	// $length >= 0
	{
		
		$c = $this->getEthingInstance()->db()->selectCollection($this->user()->dataCollectionName());
		$q = array('_t' => $this->id());
		
		
		// query string ?
		if(is_string($query)){
			
			// parse the query string
			try{
				$parseFields = array(
					'id' => array(
						'type' => 'string',
						'name' => '_id'
					),
					'date' => array(
						'type' => 'date'
					)
				);
				$keys = array_keys($this->keys());
				foreach($keys as $key)
					$parseFields[$key] = array(
						'type' => '*'
					);
				
				$parser = new Query\Parser($parseFields);
				
				$q = array_merge(
					$parser->parse($query),
					$q
				);
				
			}
			catch(Query\InvalidQueryException $e){
				throw new \Ething\Exception($e->getMessage(), 400, $e);
			}
			
		}
		
		
		$cursor = $c->find($q);
		
		// sort
		if(is_string($sort) && preg_match('/^([+-]?)(.+)$/',$sort,$matches)){
			$sortField=$matches[2];
			$sortAsc=($matches[1]!=='-') ? 1 : -1;
			$cursor->sort(array($sortField=>$sortAsc));
		}
		else
			// always sort by date
			$cursor->sort(array('date'=>1));
		
		
		// define the start point and the length of the returning set
		if($start<0){
			$start = $this->length() + $start;
			if($start < 0){
				if(isset($length)) $length+=$start;
				$start = 0;
			}
		}
		$cursor->skip($start);
		if(isset($length))
			$cursor = $cursor->limit($length);
		
		
		// return only specific fields
		$_fields = array();
		if(isset($fields)){
			$_fields['_id'] = false; // by default, the '_id' field is shown
			foreach($fields as $field){
				// handle special key '_id' 
				if($field==='id')
					$_fields['_id'] = true;
				else if(!in_array($field,static::$reservedKeys))
					$_fields[$field] = true;
			}
		}
		else {
			// never show the table id
			$_fields['_t'] = false;
		}
		
		$cursor->fields($_fields); 
		
		
		
		// iterate
		$items = [];
		foreach ($cursor as $doc) {
			$items[] = self::docSerialize($doc);
		}
		
		return $items;
	}
	
	
	// create a new resource
	public static function create(Ething $ething, User $user, array $attributes, Resource $createdBy = null) {
		return parent::createRessource($ething, $user, array_merge(self::$defaultAttr, $attributes) , array('length' => 0,'keys' => []) , $createdBy );
	}
	

}


