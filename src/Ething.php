<?php
	
/**
 * @author Adrien Mezerette <a.mezerette@gmail.com>
 * @version 0.1.0
 * @package ething
 */
	namespace Ething;
	
	
	class Ething {
		
		
		const VERSION = '0.1.0';
		
		
		private $mongoDB = null;
		
		private $logger = null;
		
		public $config;
		public $daemon;
		
		public $fs;
		
		private $name = 'ething';
		
		public function __construct($configFilename = null)
		{
			$this->config = new Config($configFilename);
			if(!$this->config->load()){
				throw new Exception("unable to read or empty config file '{$configFilename}'");
			}
			$this->daemon = new Daemon($this);
			$this->fs = new DbFs($this);
		}
		
		public function setName($name){
			$this->name = $name;
		}
		
		public function getName(){
			return $this->name;
		}
		
		public function resetDbClient(){
			$this->mongoDB = null;
		}
		
		public function db(){
			
			if(empty($this->mongoDB)){
				try {
					
					if(!extension_loaded('mongodb')){
						throw new Exception('the extension "mongodb" is not installed');
					}
					
					$serverSettings = $this->config('db');
					
					$server = 'mongodb://' . $serverSettings['host'] . ':' . $serverSettings['port'];
					$options = array();
					
					if(!empty($serverSettings['user']) && !empty($serverSettings['password'])){
						$options['username'] = $serverSettings['user'];
						$options['password'] = $serverSettings['password'];
					}
					
					$mongoClient = new \MongoDB\Client($server,$options,array(
						'typeMap' => array(
							'root' => 'array',
							'document' => 'array',
							'array' => 'array',
						)
					));
					$this->mongoDB = $mongoClient->selectDatabase($serverSettings['database']);
					if(empty($this->mongoDB))
						throw new Exception('unable to connect to the database');
					
					
				} catch(\MongoDB\Exception\Exception $e) {
					throw new Exception('unable to connect to the database ['.$e->getMessage().']');
				}
			}
			
			return $this->mongoDB;
		}
		
		
		public function config()
		{
			$config = $this->config;
			return call_user_func_array(array($config, 'attr'), func_get_args());
		}
		
		public function daemon($command, Stream &$stream = null, $options = array())
		{
			return $this->daemon->exec($command, $stream, $options);
		}
		
		
		/*
		* Resource methods
		*/
		
		public function resourceQueryParser() {
			if(!isset($this->_resourceQueryParser)){
				$this->_resourceQueryParser = new ResourceQueryParser($this);
			}
			return $this->_resourceQueryParser;
		}
		
		public function find($query = null,$limit = null,$skip = null,$sort = null) {
			
			if(!isset($query))
				$query = array();
			
			if(is_string($query)){
				// parse the query string
				$query = $this->resourceQueryParser()->parse($query);
			}
			
			$c = $this->db()->selectCollection("resources");
			
			$resources = array();
			
			$opt = array();
			
			if(is_int($limit))
				$opt['limit'] = $limit;
			if(is_int($skip))
				$opt['skip'] = $skip;
			
			if(is_string($sort) && preg_match('/^([+-]?)(.+)$/',$sort,$matches)){
				$sortField=$matches[2];
				$sortAsc=($matches[1]!=='-') ? 1 : -1;
				$opt['sort'] = array($sortField=>$sortAsc);
			}
			else
				$opt['sort'] = array('modifiedDate'=>-1);
			
			$cursor = $c->find($query, $opt);
			
			foreach ($cursor as $doc) {
				$class = 'Ething\\'.$doc['type'];
				if(class_exists($class))
					$resources[] = new $class($this,(array)$doc);
			}
			
			return $resources;
		}
		
		public function findOne($query){
			$r = $this->find($query,1);
			return count($r)==1 ? $r[0] : null;
		}
		
		public function get($id) {
			return $this->findOne(array('_id' => $id));
		}
		
		public function create($class, array $attributes, Resource $createdBy = null){
			$nsclass = 'Ething\\'.$class;
			if(!class_exists($nsclass) || !is_subclass_of($nsclass, 'Ething\\Resource'))
				throw new Exception("The resource type '{$class}' does not exist or is invalid");
			return $nsclass::create($this, $attributes, $createdBy);
		}
		
		
		public function stats(){
			
			// table
			$tbinfo = array(
				'count' => 0,
				'size' => 0
			);

			foreach( $this->db()->listCollections() as $collInfo){
				$name = $collInfo->getName();
				
				if(preg_match('/^tb\./', $name)){
					
					try {
						$i = $this->db()->command(array('collStats' => $name))->toArray()[0];
						
						$tbinfo['count'] += $i['count'];
						$tbinfo['size'] += $i['size'];
					} catch(\Exception $e){}
				}
				
			}
			
			// other
			$c = $this->db()->selectCollection("resources");
			$results = $c->aggregate(
				array(
					array(
						'$match' => array(
							"size" => array('$exists' => true)
						)
					),
					array(
						'$group' => array(
							"_id" => null,
							"size" => array('$sum' => '$size')
						)
					)
				), array(
					'useCursor' => false
				)
			);
			
			$resource_size = !empty($results["result"]) ? $results[0]["size"] : 0;
			
			return array(
				'used' => ($resource_size + $tbinfo['size'])
			);
		}
		
		
		public function repair($simulate = false){
			
			// check that files in the FS collection has a parent that still exists
			foreach( $this->fs->listFiles() as $file ){
				if(isset($file['metadata']['parent'])){
					// does the parent exist ?
					$parent = $this->get($file['metadata']['parent']);
					if(!$parent){
						$this->logger()->debug("repair: the parent of the file {$file['filename']} does not exist anymore -> removed");
						if(!$simulate) $this->fs->removeFile($file['_id']);
					}
				}
			}
			
			// table data unassociated
			foreach( $this->db()->listCollections() as $collInfo){
				
				$name = $collInfo->getName();
				
				if(preg_match('/^tb\.(.+)/', $name, $matches)){
					$id = $matches[1];
					// does the table exist ?
					$table = $this->get($id);
					if(!$table){
						// remove this table
						$this->logger()->debug("repair: drop table {$name} -> no resource associated");
						if(!$simulate) $this->db()->selectCollection($name)->drop();
					}
				}
				
			}
			
			// check parent
			foreach( $this->find(array("createdBy" => array( '$ne' => null ))) as $r){
				$parent = $r->createdBy();
				if(!$parent){
					$this->logger()->debug("repair: the parent of the resource {$r} does not exist anymore");
					if(!$simulate) $r->removeParent();
				}
			}
			
			
			return;
		}
		
		
		/*
		rules
		*/
		
		
		public function findRules(array $query = array()) {
			$rules = [];
			$c = $this->db()->selectCollection("rules");
			$cursor = $c->find($query, array(
				'sort' => array('priority'=>-1)
			));
			foreach ($cursor as $doc) {
				$rules[] = new Rule($this, (array)$doc);
			}
			
			return $rules;
		}
		
		public function getRule($id) {
			$r = $this->findRules(array(
				'_id' => $id
			));
			return count($r) ? $r[0] : null;
		}
		
		public function createRule(array $attr) {
			return Rule::create($this,$attr);
		}
		
		
		private $delaySignalsEnabled = true;
		private $signalsDispatcher = null;
		
		function setDelaySignals($enable = true){
			$this->delaySignalsEnabled = !!$enable;
		}
		
		function isSignalsDelayed(){
			return $this->delaySignalsEnabled;
		}
		
		function setSignalsDispatcher($handler){
			$this->signalsDispatcher = is_callable($handler) ? $handler : null;
		}
		
		function dispatchSignal( Event\Signal $signal, $delaySignal = null){
			
			$this->logger()->debug("signal {$signal->getName()} dispatched");
			
			if(!isset($delaySignal)) $delaySignal = $this->delaySignalsEnabled;
			if($delaySignal){
				
				if($this->signalsDispatcher !== null){
					$res = call_user_func($this->signalsDispatcher, $signal);
					return;
				}
				
				try {
					$this->daemon('signal.dispatch '.\base64_encode(\serialize($signal)), $stream, array(
						'interactive' => false
					));
				} catch(\Exception $e){
					$this->logger()->error($e);
				} // do not fire an exception if the daemon process is not started
				return;
			}
			
			// get all the rules enabled and with the correct type/name
			$query = array(
				'events.type' => $signal->getName(),
				'enabled' => true
			);
			
			// get all the rules of the event type
			$rules = $this->findRules($query);
			
			foreach($rules as $rule){
				$rule->trigger($signal);
			}
			
		}
		
		
		
		/*
		helpers
		*/
		
		static public $showPrivateField = true;
		
		public static function r_encode(array $data){
			$o=array();
			foreach($data as $k => $v){
				
				if($k === '_id') $k = 'id';
				
				if($k[0] != '_'){
					
					if($k[0] == '#'){ // show the hidden field (apikey ...)
						if(! static::$showPrivateField) continue;
						$k = substr($k,1);
					}
					
					if($v instanceof \MongoDB\BSON\UTCDateTime)
						$o[$k] = $v->toDateTime()->format(\DateTime::RFC3339);
					else if(is_array($v))
						$o[$k] = self::r_encode($v);
					else
						$o[$k] = $v;
				}
			}
			return $o;
		}
		
		
		public static function autoload($class){
			if(preg_match('/^Ething\\\/',$class)){
				
				$parts = preg_split('#\\\#', $class);
				
				array_shift($parts);

				$classname = array_pop($parts);
				
				$filepath = __DIR__;
				if(count($parts)>0)
					$filepath .= DIRECTORY_SEPARATOR.strtolower(implode(DIRECTORY_SEPARATOR, $parts));
				
				$filepath .= DIRECTORY_SEPARATOR.$classname.'.php';
				
				if (file_exists($filepath)) {
					require $filepath;
				}
			}
		}
		
		
		/*
		LOG
		*/
		
		public function logger(){
			if(!isset($this->logger)){
				$logConf = $this->config('log');
				if(is_array($logConf)){
					if(isset($logConf['file']) && is_string($logConf['file'])){
						$this->logger = new RollingFileLogger($this, $this->name, $logConf['file'], $logConf['level']);
					} else {
						$this->logger = new DbLogger($this, $this->name, $logConf['level']);
					}
				} else {
					$this->logger = new NullLogger($this, $this->name);
				}
			}
			return $this->logger;
		}
		
		
		/*
		NOTIFICATION (email, smtp)
		*/
		
		
		
		
		public function notify($subject,$message = null,$attachments = array()){
			$mail = new Mail($this);
			return $mail->send($subject,$message,$attachments);
		}
		
		
		
		
		/*
		MQTT
		*/
		
		public function mqttPublish($topic, $payload, $retain = false){
			
			if(!is_string($payload)){
				$payload = \json_encode($payload);
			}
					
			try {
				$this->daemon('mqtt.publish "'.\addslashes($topic).'" "'.\base64_encode($payload).'" '.($retain?'1':'0'), $stream, array(
					'interactive' => false
				));
			} catch(\Exception $e){
				$this->logger()->error($e);
				return false;
			} // do not fire an exception if the daemon process is not started
			
			return true;
		}
		
		
	}
	
	
	spl_autoload_register("\Ething\Ething::autoload");
	
	
	
	
	
	
	