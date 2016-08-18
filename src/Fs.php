<?php
	
	
	namespace Ething;
	
	/*
	FileSystem class
	
	This class helps to browse resources of a specific user.
	*/
	class Fs {
		
		protected $ething = null;
		protected $user = null;
		protected $scope = array();
		protected $who = null;
		
		
		static protected function getParsingFields(){
			return array(
				'type' => array(
					'type' => 'string'
				),
				'name' => array(
					'type' => 'string'
				),
				'mime' => array(
					'type' => 'string'
				),
				'id' => array(
					'type' => 'string'
				),
				'location.latitude' => array(
					'type' => 'double'
				),
				'location.longitude' => array(
					'type' => 'double'
				),
				'location.altitude' => array(
					'type' => 'double'
				),
				'createdDate' => array(
					'type' => 'date'
				),
				'modifiedDate' => array(
					'type' => 'date'
				),
				'lastSeenDate' => array(
					'type' => 'date'
				),
				'createdBy.type' => array(
					'type' => 'string'
				),
				'createdBy.id' => array(
					'type' => 'string'
				),
				'length' => array(
					'type' => 'integer'
				),
				'size' => array(
					'type' => 'integer'
				),
				'description' => array(
					'type' => 'string'
				),
				'battery' => array(
					'type' => 'double'
				),
				'hasThumbnail' => array(
					'type' => 'bool',
					'compil' => function($op,$value){
						return $value ? array(
							'_thumb' => array( '$ne' => null )
						) : array(
							'_thumb' => null
						);
					}
				),
				'hasIcon' => array(
					'type' => 'bool',
					'compil' => function($op,$value){
						return $value ? array(
							'_icon' => array( '$ne' => null )
						) : array(
							'_icon' => null
						);
					}
				)
			);
		}
		
		public function __construct(Ething $ething, $who){
			$this->ething = $ething;
			$this->who = $who;
			if($who instanceof User)
				$this->user = $who;
			else if($who instanceof Device){
				$this->user = $who->user();
				if(!Scope::check(Scope::RESOURCE_ALL,$who)){
					$this->scope = Scope::check(Scope::RESOURCE_OWNDATA,$who) ? 
						array('createdBy.id' => $who->id()) : // limit access to resources created by this device
						false; // no access at all !!!
				}
			}
			else
				throw new InvalidArgumentException('Fs constructor only accept User or Device');
			
		}
		
		public function user(){
			return $this->user;
		}
		
		public function get($id) {
			return $this->findOne(array('_id'=>$id));
		}
		
		// if query is null, it selects all the available resource
		public function find(array $query = array(),$limit = null,$skip = null,$sort = null) {
			if($this->scope === false)
				return array();
			// only current user resources are shown
			return $this->ething->find(array_merge($query,array('user'=>$this->user->id()),$this->scope),$limit,$skip,$sort);
		}
		
		public function findOne($query){
			$r = $this->find($query,1);
			return count($r)==1 ? $r[0] : null;
		}
		
		function all($queryString = null,$limit = null,$skip = null,$sort = null) {
			
			if(is_string($queryString)){
				// parse the query string
				try{
					$parser = new Query\Parser(static::getParsingFields());
					if($this->who instanceof Resource)
						$parser->addConstant('me',(string)$this->who->id());
					$q = $parser->parse($queryString);
				}
				catch(Query\InvalidQueryException $e){
					throw new \Ething\Exception($e->getMessage(), 400, $e);
				}
			}
			else
				$q = array();
			
			return $this->find($q,$limit,$skip,$sort);
		}
		
		public function freeSpace() {
			$stat = $this->user->stats();
			$quota = $this->user->quota();
			return $quota ? ($quota - $stat['used']) : INF;
		}
		
		function stats() {
			return $this->user->stats();
		}
		
		public function create($class, array $attributes, Resource $createdBy = null) {
			return $this->ething->create($this->user, $class, $attributes, $createdBy);
		}
		
	}
	
	
	
	
	
	
	
	
	
	
	