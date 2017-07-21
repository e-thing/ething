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
	
	
	
	const TIMESTAMP = 0;
	const TIMESTAMP_MS = 1;
	public static $dateFormat = \DateTime::RFC3339;
	// return an object
	private static function docSerialize($doc) {
		if(isset($doc['_id'])){
			$doc['id'] = $doc['_id'];
			unset($doc['_id']);
		}
		if(isset($doc['date'])){
			if(self::$dateFormat === self::TIMESTAMP){
				$doc['date'] = $doc['date']->toDateTime()->getTimestamp();
			} else if(self::$dateFormat === self::TIMESTAMP_MS){
				$doc['date'] = $doc['date']->toDateTime()->getTimestamp() * 1000;
			} else {
				$doc['date'] = $doc['date']->toDateTime()->format(self::$dateFormat);
			}
		}
		return (object)$doc;
	}
	
	public static function validate($key, &$value, &$context) {
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
			case 'content':
				if(is_array($value) || is_null($value)){
					
					$content = is_null($value) ? array() : $value;
					static::sanitizeData($content, $keys); // throw an exception on error
					
					$context['callbacks'][] = function($r) use ($content,$keys) {
						$r->importRaw($content,$keys);
					};
				}
				$ret = true;
				unset($context['config'][$key]);// remove this key
				break;
			default:
				$ret = parent::validate($key,$value,$context);
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
		$c = $this->ething->db()->selectCollection('tabledata');
		
		try {
			$c->deleteMany(array('_t' => $this->id()));
			
			$this->setAttr('length', 0);
			$this->setAttr('keys', array());
			$this->update();
		}
		catch(Exception $e){}
		
	}
	
	// is called regularly
	public function checkExpiredData() {
		
		// remove the expired data in the current table
		if($this->expireAfter){
			$c = $this->ething->db()->selectCollection('tabledata');
			$cursor = $c->find(array(
				'_t' => $this->id(),
				'date' => array(
					'$lt' => (new \MongoDB\BSON\UTCDateTime((time() - $this->expireAfter)*1000))
				)
			), array(
				'projection' => array('_id' => 1)
			));
			
			$idToBeRemoved = [];
			foreach ($cursor as $doc)
				$idToBeRemoved[] = $doc['_id'];
			
			if(count($idToBeRemoved))
				$this->remove_rows($idToBeRemoved);
		}
		
	}
	
	
	private function updateMeta() {
		
		$keys = [];
		$length = 0;
		
		$c = $this->ething->db()->selectCollection('tabledata');
		$cursor = $c->find(array('_t' => $this->id()),array(
			'projection' => array(
				'_id' => 0,
				'date' => 0,
				'_t' => 0
			)
		));
		
		foreach ($cursor as $doc) {
			foreach ($doc as $k => $v) {
				if(!isset($keys[$k])) $keys[$k]=0;
				$keys[$k]++;
			}
			$length++;
		}
		
		$this->setAttr('length', $length);
		$this->setAttr('keys', $keys);
		$this->update();
	}
	
	public function repair() {
		$this->updateMeta();
	}
	
	// return the number of document removed
	public function remove_rows(array $row_ids) {
		
		$nb = 0;
		
		if(!is_array($row_ids) && !($row_ids instanceof Traversable))
			$row_ids = [$row_ids];
		
		$c = $this->ething->db()->selectCollection('tabledata');
		
		$keys = $this->keys;
		
		foreach($row_ids as $row_id){
			
			try {
				$removedDoc = $c->findOneAndDelete(array(
					'_id' => $row_id,
					'_t' => $this->id()
				));
			
				// update the key count
				if($removedDoc){
					foreach($removedDoc as $field => $v){
						if(isset($keys[$field])){
							$keys[$field]--;
							if($keys[$field]<=0)
								unset($keys[$field]);
						}
					}
					
					$nb++;
				}
			}
			catch(Exception $e) {} // invalid id or unable to remove the document
		}
		
		if($nb){
			$this->setAttr('length', $this->length - $nb);
			$this->setAttr('keys', $keys);
			$this->update();
		}
		
		return $nb;
	}
	
	public function remove_row($row_id) {
		
		$c = $this->ething->db()->selectCollection('tabledata');
		
		$keys = $this->keys;
			
		try {
			$removedDoc = $c->findOneAndDelete(array(
				'_id' => $row_id,
				'_t' => $this->id()
			));
		
			// update the key count
			if($removedDoc){
				foreach($removedDoc as $field => $v){
					if(isset($keys[$field])){
						$keys[$field]--;
						if($keys[$field]<=0)
							unset($keys[$field]);
					}
				}
				
				$this->setAttr('length', $this->length - 1);
				$this->setAttr('keys', $keys);
				$this->update();
				
				return $removedDoc;
			}
		}
		catch(Exception $e) {} // invalid id or unable to remove the document
		
		return false;
	}
	
	public static function sanitizeData(array &$dataArray, &$keys = null, $invalidFields = self::INVALID_FIELD_RENAME, $skipError = true, $setDate = true){
		
		if(!is_array($keys))
			$keys = array();
		
		$length = 0;
		
		foreach($dataArray as $i => &$data){
			
			try{
				if(is_object($data))
					$data = (array)$data;
				else if(!is_array($data))
					throw new Exception('invalid data');
				
				
				// key/field validation
				unset($data['id']); // will be auto generated !
				foreach($data as $k => $v){
					
					if(!(is_int($v) || is_float($v) || is_string($v) || is_bool($v) || is_null($v)))
						throw new Exception('The value must either be a string or a number or a boolean or null.');
					
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
								throw new Exception('invalid key "'.$k.'", must only contain alphanumeric, underscore or dashes characters. Keys must not be empty');
							
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
								throw new Exception('invalid key "'.$k.'", must not be one of the following values '.implode(',',static::$reservedKeys));
							
						}
					}
					
					if($k=='date'){
						// check the format
						if($t = strtotime($v))
							$data[$k] = new \MongoDB\BSON\UTCDateTime($t*1000);
						else
							throw new Exception('Invalid date "'.$v.'"');
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
				if($setDate && !isset($data['date'])) $data['date'] = new \MongoDB\BSON\UTCDateTime(time()*1000); // add the insertion date for that document
				
				
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
			
			$keys = $this->keys;
			$length = $this->length;
			
			// sanitize the incoming data
			$dataArray = array($data);
			$length += static::sanitizeData($dataArray,$keys,$invalidFields,false);
			
			// add meta data
			foreach($dataArray as &$data){
				$data['_id'] = ShortId::generate();
				$data['_t'] = $this->id();
			}
			
			// insert the data
			$c = $this->ething->db()->selectCollection('tabledata');
			$c->insertOne($dataArray[0]);
			// remove extra row
			if( $this->maxLength && $length > $this->maxLength ){
				
				// remove the oldest document
				$removedDoc = $c->findOneAndDelete(array(
					'_t' => $this->id()
				),array(
					'sort' => array('date'=>1),
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
			
			$this->setAttr('length', $length);
			$this->setAttr('keys', $keys);
			$this->update(true);
			
			$doc = self::docSerialize($dataArray[0]);
			// generate an event
			$this->dispatchSignal(Event\TableDataAdded::emit($this, $doc));
			// mqtt publish
			$this->ething->mqttPublish("resource/table/{$this->id()}/data", $doc, true);
			
			return $doc;
		}
		
		return false;
	}
	
	
	public function import(array $dataArray = array(), $invalidFields = self::INVALID_FIELD_RENAME, $skipError = true){
		
		// remove extra row
		if( $this->maxLength && count($dataArray) > $this->maxLength ){
			$dataArray = array_slice($dataArray, - $this->maxLength);
		}
		
		
		// remove any previous content
		$this->clear();
		
		// sanitize the incoming data
		$this->setAttr('length', static::sanitizeData($dataArray,$this->keys,$invalidFields,$skipError));
		
		if(!empty($dataArray)){
			// add meta data
			foreach($dataArray as &$data){
				$data['_id'] = ShortId::generate();
				$data['_t'] = $this->id();
			}
			
			// insert the data
			$c = $this->ething->db()->selectCollection('tabledata');
			$c->insertMany($dataArray, array(
				'ordered' => false
			));
		}
		
		$this->update();
		
		return true;
	}
	
	// no sanitize is made, internal purpose only
	private function importRaw(array $dataArray, array $keys){
		if(empty($dataArray))
			return true;
		
		// remove extra row
		if( $this->maxLength && count($dataArray) > $this->maxLength ){
			$dataArray = array_slice($dataArray, - $this->maxLength);
		}
		
		// remove any previous content
		$this->clear();
		
		// add meta data
		foreach($dataArray as &$data){
			$data['_id'] = ShortId::generate();
			$data['_t'] = $this->id();
		}
		
		// insert the data
		$c = $this->ething->db()->selectCollection('tabledata');
		$c->insertMany($dataArray, array(
			'ordered' => false
		));
		
		// update the metadata
		$this->setAttr('length', count($dataArray));
		$keys_ = $this->getAttr('keys');
		foreach($keys as $k => $c){
			if(!isset($keys_[$k]))
				$keys_[$k] = 0;
			$keys_[$k] += $c;
		}
		$this->setAttr('keys', $keys_);
		$this->update();
		
		return true;
	}
	
	
	public function getRow($id, array $fields = null)
	{
		
		// return only specific fields
		$_fields = array();
		if(isset($fields)){
			$_fields['_id'] = 0; // by default, the '_id' field is shown
			foreach($fields as $field){
				// handle special key '_id' 
				if($field==='id')
					$_fields['_id'] = 1;
				else if(!in_array($field,static::$reservedKeys))
					$_fields[$field] = 1;
			}
		}
		else {
			// never show the table id
			$_fields['_t'] = 0;
		}
		
		
		$c = $this->ething->db()->selectCollection('tabledata');
		$r = $c->findOne(array('_id' => $id,'_t' => $this->id()),array( 'projection' => $_fields ));
		
		return (!is_null($r)) ? self::docSerialize($r) : null;
	}
	
	public function replaceRowById($row_id, array $data, $invalidFields = self::INVALID_FIELD_RENAME) {
		if(!empty($data)){
			
			$keys = $this->keys;
			
			// sanitize the incoming data
			$dataArray = array($data);
			static::sanitizeData($dataArray,$keys,$invalidFields,false);
			
			// add meta data
			$dataArray[0]['_id'] = $row_id;
			$dataArray[0]['_t'] = $this->id();
			
			// insert the data
			$c = $this->ething->db()->selectCollection('tabledata');
			$original = $c->findOneAndReplace(array('_id' => $row_id), $dataArray[0]);
			
			if($original){
				foreach($original as $field => $v){
					if(isset($keys[$field])){
						$keys[$field]--;
						if($keys[$field]<=0)
							unset($keys[$field]);
					}
				}
				
				$this->setAttr('keys', $keys);
				$this->update(true);
				
				return self::docSerialize($dataArray[0]);
			}
		}
		
		return false;
	}
	
	// replace only one row
	public function replaceRow($query, array $data, $invalidFields = self::INVALID_FIELD_RENAME, $upsert = false) {
		if(!empty($data)){
			
			$queries = array();
			$queries[] = array('_t' => $this->id());
			
			if(is_string($query)){
				// parse the query string
				$queries[] = $this->parser()->parse($query);
			}
			else if(is_array($query))
				$queries[] = $query;
			
			$c = $this->ething->db()->selectCollection('tabledata');
			
			$original = $c->findOne(array(
				'$and' => $queries
			));
			
			if($original){
				// the document was found !
				
				$keys = $this->keys;
				
				// sanitize the incoming data
				$dataArray = array($data);
				static::sanitizeData($dataArray,$keys,$invalidFields,false);
				
				// add meta data
				$dataArray[0]['_id'] = $original['_id']; // keep the same id !
				$dataArray[0]['_t'] = $this->id();
				
				//replace it !
				$c->replaceOne(array('_id' => $original['_id']), $dataArray[0]);
				
				foreach($original as $field => $v){
					if(isset($keys[$field])){
						$keys[$field]--;
						if($keys[$field]<=0)
							unset($keys[$field]);
					}
				}
				
				$this->setAttr('keys', $keys);
				$this->update(true);
				
				return self::docSerialize($dataArray[0]);
			} else {
				// not found !
				if($upsert){
					return $this->insert($data, $invalidFields);
				}
			}
		}
		
		return false;
	}
	
	public function parser(){
		if(!isset($this->_parser)){
			$this->_parser = new TableQueryParser();
		}
		return $this->_parser;
	}
	
	public function find($query){
		return $this->select(0,null,null,null,$query);
	}
	
	public function select($start = 0, $length = null, array $fields = null, $sort = null, $query = null)
	// If start is non-negative, the returned selection will start at the start'th position in the table, counting from zero.
	// If start is negative, the returned selection will start at the start'th position from the end of the table.
	// If length is given and is positive, the selection returned will contain at most length lines beginning from start.
	// If length is omitted, the selection starting from start until the end of the table will be returned.
	// $length >= 0
	{
		
		$c = $this->ething->db()->selectCollection('tabledata');
		
		$queries = array();
		$queries[] = array('_t' => $this->id());
		
		if(is_string($query)){
			// parse the query string
			$queries[] = $this->parser()->parse($query);
		}
		else if(is_array($query))
			$queries[] = $query;
		
		$q = array(
			'$and' => $queries
		);
		
		$opt = array();
		
		// sort
		if(is_string($sort) && preg_match('/^([+-]?)(.+)$/',$sort,$matches)){
			$sortField=$matches[2];
			$sortAsc=($matches[1]!=='-') ? 1 : -1;
			$opt['sort'] = array($sortField=>$sortAsc);
		}
		else
			// always sort by date
			$opt['sort'] = array('date'=>1);
		
		
		// define the start point and the length of the returning set
		if($start<0){
			$start = $this->length + $start;
			if($start < 0){
				if(isset($length)) $length+=$start;
				$start = 0;
			}
		}
		$opt['skip'] = $start;
		if(isset($length))
			$opt['limit'] = $length;
		
		
		// return only specific fields
		$_fields = array();
		if(isset($fields)){
			$_fields['_id'] = 0; // by default, the '_id' field is shown
			foreach($fields as $field){
				// handle special key '_id' 
				if($field==='id')
					$_fields['_id'] = 1;
				else if(!in_array($field,static::$reservedKeys))
					$_fields[$field] = 1;
			}
		}
		else {
			// never show the table id
			$_fields['_t'] = 0;
		}
		
		$opt['projection'] = $_fields;
		
		
		$cursor = $c->find($q, $opt);
		
		
		// iterate
		$items = [];
		foreach ($cursor as $doc) {
			$items[] = self::docSerialize($doc);
		}
		
		return $items;
	}
	
	
	// create a new resource
	public static function create(Ething $ething, array $attributes, Resource $createdBy = null) {
		return parent::createRessource($ething, array_merge(self::$defaultAttr, $attributes) , array('length' => 0,'keys' => []) , $createdBy );
	}
	
	public function computeStatistics($key, $query = null){
		
		$map = new \MongoDB\BSON\Javascript(str_replace('<KEY>',$key,file_get_contents(__DIR__.'/mongodb/statistics/map.js')));
		$reduce = new \MongoDB\BSON\Javascript(file_get_contents(__DIR__.'/mongodb/statistics/reduce.js'));
		$finalize = new \MongoDB\BSON\Javascript(file_get_contents(__DIR__.'/mongodb/statistics/finalize.js'));
		
		$queries = array();
		$queries[] = array(
			'_t' => $this->id(),
			$key => array('$exists' => true)
		);
		
		if(is_string($query)){
			// parse the query string
			$queries[] = $this->parser()->parse($query);
		}
		else if(is_array($query))
			$queries[] = $query;
		
		$res = $this->ething->db()->command(array(
			"mapreduce" => "tabledata",
			"map" => $map,
			"reduce" => $reduce,
			"finalize" => $finalize,
			"query" => array(
				'$and' => $queries
			),
			"out" => array("inline" => 1)
		));

		$res = $res->toArray()[0];
		
		$ok = !!$res['ok'];
		if($ok && count($res['results'])){
			//$time = $res['timeMillis'];
			return EThing::r_encode($res['results'][0]['value']);
		}

		return false;
	}
	
	
	
}


