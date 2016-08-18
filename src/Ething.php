<?php
	
	namespace Ething;
	
	
	class Ething {
		
		
		const VERSION = '0.1.0';
		
		
		private $mongoDB = null;
		
		private $_config = array(
			
			// mongoDB server
			'server' => array(
				'host' => 'localhost',
				'port' => 27017,
				'user' => null,
				'password' => null,
				'database' => "ething"
			),
			
			// mail (set to false to disable this feature)
			'mail' => false,
			
			// if your server is behind a proxy, set the proxy address here (e.g. proxy.example.com:5100)
			// necessary for swagger specification validation
			'proxy' => false
			
		);
		
		public function __construct($config = array())
		{
			$this->config($config);
			
			if(!extension_loaded('mongo')){
				throw new Exception('the extension "mongo" is not installed');
			}
			
			try {
				
				$serverSettings = $this->config('server');
				
				$server = 'mongodb://' . $serverSettings['host'] . ':' . $serverSettings['port'];
				$options = array(
					"connect" => true
				);
				
				if(!empty($serverSettings['user']) && !empty($serverSettings['password'])){
					$options['username'] = $serverSettings['user'];
					$options['password'] = $serverSettings['password'];
				}
				
				$mongoClient = new \MongoClient($server,$options);
				$this->mongoDB = $mongoClient->selectDB($serverSettings['database']);
				if(empty($this->mongoDB))
					throw new Exception('unable to connect to the database');
				
				
			} catch(\MongoConnnectionException $e) {
				throw new Exception('unable to connect to the database ['.$e->getMessage().']');
			}
			
		}
		
		
		/**
		 * Configure Ething Settings
		 *
		 * This method defines application settings and acts as a setter and a getter.
		 *
		 * If only one argument is specified and that argument is a string, the value
		 * of the setting identified by the first argument will be returned, or NULL if
		 * that setting does not exist.
		 *
		 * If only one argument is specified and that argument is an associative array,
		 * the array will be merged into the existing application settings.
		 *
		 * If two arguments are provided, the first argument is the name of the setting
		 * to be created or updated, and the second argument is the setting value.
		 *
		 * @param  string|array $name  If a string, the name of the setting to set or retrieve. Else an associated array of setting names and values
		 * @param  mixed        $value If name is a string, the value of the setting identified by $name
		 * @return mixed        The value of a setting if only one argument is a string
		 */
		public function config($name, $value = null)
		{
			if (is_array($name)) {
				$this->_config = array_replace_recursive($this->_config, $name);
			} elseif (func_num_args() === 1) {
				$path = explode('.',$name);
				$p = &$this->_config;
				foreach($path as $k){
					if(is_array($p) && isset($p[$k]))
						$p = &$p[$k];
					else
						return null;
				}
				return $p;
				//return isset($this->_config[$name]) ? $this->_config[$name] : null;
			} else {
				$this->_config[$name] = $value;
			}
		}
		
		
		public function db(){
			return $this->mongoDB;
		}
		
		
		
		
		/*
		* Resource methods
		*/
		
		public function find(array $query = array(),$limit = null,$skip = null,$sort = null) {
			$c = $this->db()->selectCollection("resources");
			
			$resources = array();
			
			$cursor = $c->find($query);
			if(is_int($limit))
				$cursor->limit($limit);
			if(is_int($skip))
				$cursor->skip($skip);
			if(is_string($sort) && preg_match('/^([+-]?)(.+)$/',$sort,$matches)){
				$sortField=$matches[2];
				$sortAsc=($matches[1]!=='-') ? 1 : -1;
				$cursor->sort(array($sortField=>$sortAsc));
			}
			else
				$cursor->sort(array('modifiedDate'=>-1));
			foreach ($cursor as $doc) {
				$class = 'Ething\\'.$doc['type'];
				if(class_exists($class))
					$resources[] = new $class($this,$doc);
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
		
		public function create(User $user, $class, array $attributes, Resource $createdBy = null){
			$nsclass = 'Ething\\'.$class;
			if(!class_exists($nsclass) || !method_exists($nsclass, 'create'))
				throw new Exception("The resource type '{$class}' does not exist or is invalid");
			return $nsclass::create($this, $user, $attributes, $createdBy);
		}
		
		
		
		/*
		* User methods
		*/
		
		public function findUsers(array $query = array()) {
			$users = [];
			$c = $this->db()->selectCollection("users");
			$cursor = $c->find($query);
			foreach ($cursor as $doc) {
				$users[] = new User($this, $doc);
			}
			return $users;
		}
		
		public function findOneUser(array $query = array()) {
			$u = $this->findUsers($query);
			return count($u) ? $u[0] : null;
		}
		
		public function findOneUserById($id) {
			return $this->findOneUser(array('_id' => $id));
		}
		
		public function findOneUserByName($name) {
			return $this->findOneUser(array('name' => $name));
		}
		
		public function createUser(array $attr) {
			return User::create($this,$attr);
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
		
		
		
		
		
		
		
		
		
		private $delayEventEnabled = false;
		private $pendingEvents = array();
		
		
		function setDelayEvents($enable = true){
			$this->delayEventEnabled = !!$enable;
		}
		
		function isEventsDelayed(){
			return $this->delayEventEnabled;
		}
		
		function hasPendingEvents(){
			return count($this->pendingEvents)>0;
		}
		
		function delayEvent( Resource $target, $eventType, $customData = null ){
			$this->pendingEvents[] = array(
				'target' => $target,
				'event' => $eventType,
				'data' => $customData
			);
		}
		
		function dispatchPendingEvents(){
			$_savedState = $this->isEventsDelayed();
			$this->setDelayEvents(false);
			foreach( $this->pendingEvents as $e ){
				$e->target->dispatchEvent( $e->event, $e->data );
			}
			$this->pendingEvents = array();
			$this->setDelayEvents($_savedState);
		}
		
		
		private $eventExceptionHandler = null;
		
		function setEventExceptionHandler($handler){
			$this->eventExceptionHandler = is_callable($handler) ? $handler : null;
		}
		
		function dispatchEventException($exception){
			if($this->eventExceptionHandler===null) return;
			
			if(!is_array($exception))
				$exception = array($exception);
			foreach($exception as $e){
				call_user_func($this->eventExceptionHandler, $e);
			}
		}
		
	}
	
	
	spl_autoload_register("\Ething\Ething::autoload");
	
	
	
	
	
	
	