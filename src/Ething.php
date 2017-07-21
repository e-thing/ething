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
		
		public $config;
		
		public $fs;
		
		public function __construct($configFilename = null)
		{
			$this->config = new Config($configFilename);
			if(!$this->config->load()){
				$this->logErr("unable to read or empty config file '{$configFilename}'", $this->config);
			}
			$this->fs = new DbFs($this);
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
		
		
		public function freeSpace() {
			$stat = $this->stats();
			return $stat['quota_size'] ? ($stat['quota_size'] - $stat['used']) : INF;
		}
		
		public function stats(){
			$data_stats = $this->db()->command(array('collStats' => 'tabledata'))->toArray();
			
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
				'quota_size' => $this->config('quota'),
				'used' => ($resource_size + ( empty($data_stats) ? 0 : $data_stats[0]['size']))
			);
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
			
			if(!isset($delaySignal)) $delaySignal = $this->delaySignalsEnabled;
			if($delaySignal){
				
				if($this->signalsDispatcher !== null){
					$res = call_user_func($this->signalsDispatcher, $signal);
					return;
				}
				
				try {
					$this->deamon('signal.dispatch '.\base64_encode(\serialize($signal))."\n");
				} catch(\Exception $e){
					$this->log($e);
				} // do not fire an exception if the deamon process is not started
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
		
		public function log($message, $caller = null, $criticity = null){
			$log = $this->config('log');
			
			if(!empty($log) && is_string($log)){
				
				$parts = array(
					'date' => date("Y-m-d H:i:s"),
					'caller' => is_string($caller) ? $caller : (is_object($caller) ? get_class($caller) : 'unk'),
					'type' => 'info',
					'message' => (string) $message
				);
				
				if($message instanceof \Exception){
					$parts['type'] = 'error';
					if(!isset($caller))
						$parts['caller'] = basename($message->getFile());
					//$parts['message'] = "Exception: {$message->getMessage()} [file:{$message->getFile()} line:{$message->getLine()} code:{$message->getCode()}]";
					$parts['message'] = (string)$message;
				}
				
				if(isset($criticity))
					$parts['type'] = $criticity;
				
				$content = implode(';',$parts);
				if($content[strlen($content)-1] !== "\n") $content.="\n";
				@file_put_contents($log, utf8_encode($content), FILE_APPEND);
			}
		}
		
		public function logErr($message, $caller = null){
			return $this->log($message, $caller, 'error');
		}
		
		public function logSuccess($message, $caller = null){
			return $this->log($message, $caller, 'success');
		}
		
		
		/*
		NOTIFICATION (email, smtp)
		*/
		
		
		
		
		public function notify($subject,$message = null){
			
			$smtpSettings = $this->config('notification.smtp');
			$mailList = $this->config('notification.emails');
			
			if(empty($smtpSettings)){
				throw new Exception("Mail feature not enable");
			}
			
			if(!isset($smtpSettings['host']) || !isset($smtpSettings['port']) || !isset($smtpSettings['user']) || !isset($smtpSettings['password']) ){
				throw new Exception("invalid notification.smtp config");
			}
			
			if(empty($mailList)){
				return true;
			}
			
			if(!isset($subject))
				$subject = 'notification';
			
			if(empty($message))
				$message = '';
			
			//Create a new PHPMailer instance
			$mail = new \PHPMailer;
			//Tell PHPMailer to use SMTP
			$mail->isSMTP();
			//Enable SMTP debugging
			// 0 = off (for production use)
			// 1 = client messages
			// 2 = client and server messages
			$mail->SMTPDebug = 0;
			//Ask for HTML-friendly debug output
			//$mail->Debugoutput = 'html';
			//Set the hostname of the mail server
			$mail->Host = $smtpSettings['host'];
			// use
			// $mail->Host = gethostbyname('smtp.gmail.com');
			// if your network does not support SMTP over IPv6
			//Set the SMTP port number - 587 for authenticated TLS, a.k.a. RFC4409 SMTP submission
			$mail->Port = $smtpSettings['port'];
			//Set the encryption system to use - ssl (deprecated) or tls
			$mail->SMTPSecure = 'tls';
			//Whether to use SMTP authentication
			$mail->SMTPAuth = true;
			//Username to use for SMTP authentication - use full email address for gmail
			$mail->Username = $smtpSettings['user'];
			//Password to use for SMTP authentication
			$mail->Password = $smtpSettings['password'];
			//Set who the message is to be sent from
			$mail->setFrom($smtpSettings['user'], 'eThing');
			//Set an alternative reply-to address
			//$mail->addReplyTo('replyto@example.com', 'First Last');
			//Set who the message is to be sent to
			foreach($mailList as $email)
				$mail->addAddress($email);
			//Set the subject line
			$mail->Subject = '[eThing] '.$subject;
			//set the text body
			$mail->isHTML(true); // accept html
			$mail->Body = $message;
			//send the message, check for errors
			if (!$mail->send()) {
				throw new Exception("Mailer Error: " . $mail->ErrorInfo);
			}
			
			return true;
		}
		
		
		
		/*
		DEAMON
		*/
		
		public function deamon($command, Stream &$stream = null, $options = array()){
			
			if(!isset($stream))
				$stream = new StreamBuffer();
			
			$stream->contentType('text/plain');
			
			$deamonSettings = $this->config('deamon');
			
			if(!empty($deamonSettings) && isset($deamonSettings['host']) && isset($deamonSettings['port'])){
				
				$options = array_merge(array(
					'timeout' => isset($deamonSettings['timeout']) ? $deamonSettings['timeout'] : 10
				), $options);
				
				$address = "tcp://".$deamonSettings['host'].":".$deamonSettings['port'];
				
				$fp = @stream_socket_client($address, $errno, $errstr, 5);
				if (!$fp) {
					$this->log("unable to communicate with the deamon process {$address} ({$errno} - {$errstr})");
					$stream->errCode(2);
					$stream->out("unable to communicate with the deamon process {$address} ({$errno} - {$errstr})", Stream::STDERR);
				} else {
					stream_set_timeout ($fp, $options['timeout']);
					
					// wait for the initialization done
					while(strlen($c = fread($fp,1))) {
						if($c === '>') break;
					}
					
					if(strlen($c)){
						
						@fwrite($fp, "{$command}\n");
						
						$out = '';
						$nl = false;
						while(strlen($c = fread($fp,1))) {
							if($c === '>' && $nl) break;
							$nl = $c === "\n";
							$out.=$c;
						}
						
						if(strlen($c)){
							$res = json_decode($out);
							if(json_last_error() === JSON_ERROR_NONE){
								if($res->ok){
									$stream->errCode(0);
									if(isset($res->result)) $stream->out($res->result);
								} else {
									$stream->errCode(1);
									$stream->out($res->error, Stream::STDERR);
								}
							}
							else {
								$stream->errCode(1);
								$stream->out('bad response', Stream::STDERR);
							}
							
						} else {
							$stream->errCode(1);
							$stream->out('timeout', Stream::STDERR);
						}
						
					
					} else {
						$stream->errCode(1);
						$stream->out('timeout', Stream::STDERR);
					}
					
					$stream->close();
					
					@fclose($fp);
					
				}
			
			} else {
				$this->log("bad deamon config");
				$stream->errCode(3);
				$stream->out("bad deamon config", Stream::STDERR);
			}
			
			return $stream->errCode() === 0;
		}
		
		
		/*
		MQTT
		*/
		public function mqttPublish($topic, $payload, $retain = false){
			
			$mqttSettings = $this->config('mqtt');
			
			if(!empty($mqttSettings) && isset($mqttSettings['host']) && isset($mqttSettings['port']) && isset($mqttSettings['clientId'])){
				$client = new MQTT\phpMQTT($mqttSettings['host'], $mqttSettings['port'], $mqttSettings['clientId']);
				
				$user = isset($mqttSettings['user']) ? $mqttSettings['user'] : null;
				$pwd = isset($mqttSettings['password']) ? $mqttSettings['password'] : null;
				
				if(!empty($mqttSettings['rootTopic'])) {
					$topic = $mqttSettings['rootTopic'].$topic;
				}
				
				if($client->connect(true, NULL, $user, $pwd)){
					
					if(!is_string($payload)){
						$payload = \json_encode($payload);
					}
					
					$client->publish($topic, $payload, 0, $retain);
					$client->close();
					return true;
				}
			}
			return false;
		}
		
		
	}
	
	
	spl_autoload_register("\Ething\Ething::autoload");
	
	
	
	
	
	
	