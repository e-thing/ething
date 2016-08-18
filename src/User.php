<?php
	
namespace Ething;
	
	/**
	 * @swagger-definition
	 * "User":{ 
	 *   "type": "object",
	 *   "description": "The User object",
	 * 	 "properties":{  
	 * 		"id":{
	 * 		   "type":"string",
	 * 		   "description":"The id of the user.",
	 *         "readOnly": true
	 * 		},
	 * 		"name":{  
	 * 		   "type":"string",
	 * 		   "description":"The name of the user.",
	 *         "readOnly": true
	 * 		}
	 * 	 }
	 * }
	 */
	
	/**
	 * @swagger-definition
	 * "Profile":{ 
	 *   "type": "object",
	 *   "description": "The User profile",
	 * 	 "properties":{  
	 * 		"id":{
	 * 		   "type":"string",
	 * 		   "description":"The id of the user.",
	 *         "readOnly": true
	 * 		},
	 * 		"name":{  
	 * 		   "type":"string",
	 * 		   "description":"The name of the user.",
	 *         "readOnly": true
	 * 		},
	 * 		"email":{  
	 * 		   "type":"string",
	 * 		   "description":"The email address of the user.",
	 *         "readOnly": false
	 * 		},
	 * 		"createdDate":{
	 * 		   "type":"string",
	 * 		   "format":"date-time",
	 * 		   "description":"Create time for this user (formatted RFC 3339 timestamp).",
	 *         "readOnly": true
	 * 		},
	 * 		"quota":{
	 * 		   "type":"number",
	 * 		   "description":"The allowed quota in bytes. 0 means unlimited.",
	 *         "readOnly": true
	 * 		}
	 * 	 }
	 * }
	 */
	
class User implements \JsonSerializable
{
	
	const VALIDATE_NAME = '/^[a-zA-Z0-9\-.\'_]{3,25}$/';
	const VALIDATE_PASSWORD = '/^.{4,}$/';
	
	private $ething = null;
	
	protected $_d = null; // the mongodb document associated to the current user
	
	public function __construct(Ething $ething, array $doc) // Constructeur
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
	
	public function name() {
		return $this->_d['name'];
	}
	
	public function password() {
		return $this->_d['password'];
	}
	
	public function email() {
		return $this->_d['email'];
	}
	
	public function createdDate() {
		return $this->_d['createdDate']->sec;
	}
	
	// in bytes
	public function quota() {
		return $this->_d['quota'];
	}
	
	public function dataCollectionName() {
		return 'data-'.$this->name();
	}
	
	public function jsonSerialize() {
		return array(
			'id' => (string)$this->id(),
			'name' => $this->name()
		);
	}
	
	public function profile() {
		return array(
			'id' => (string)$this->id(),
			'name' => $this->name(),
			'email' => $this->email(),
			'createdDate' => date(\DateTime::RFC3339, $this->createdDate()),
			'quota' => $this->quota()
		);
	}
	
	
	public function stats(){
		$data_stats = $this->ething->db()->command(array('collStats' => $this->dataCollectionName()));
		
		$c = $this->ething->db()->selectCollection("resources");
		$results = $c->aggregate(
			array(
				'$match' => array(
					"user" => $this->id()
				)
			),
			array(
				'$group' => array(
					"_id" => null,
					"size" => array('$sum' => '$size')
				),
			)
		);
		
		$resource_size = !empty($results["result"]) ? $results["result"][0]["size"] : 0;
		
		return array(
			'quota_size' => $this->quota(),
			'used' => ($resource_size + $data_stats['size'])
		);
	}
	
	public function sendMail($subject,$message = null){
		
		$mailSettings = $this->ething->config('mail');
		
		if(!$mailSettings){
			throw new \Ething\Exception("Mail feature not enable");
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
		$mail->Host = $mailSettings['host'];
		// use
		// $mail->Host = gethostbyname('smtp.gmail.com');
		// if your network does not support SMTP over IPv6
		//Set the SMTP port number - 587 for authenticated TLS, a.k.a. RFC4409 SMTP submission
		$mail->Port = $mailSettings['port'];
		//Set the encryption system to use - ssl (deprecated) or tls
		$mail->SMTPSecure = 'tls';
		//Whether to use SMTP authentication
		$mail->SMTPAuth = true;
		//Username to use for SMTP authentication - use full email address for gmail
		$mail->Username = $mailSettings['user'];
		//Password to use for SMTP authentication
		$mail->Password = $mailSettings['password'];
		//Set who the message is to be sent from
		$mail->setFrom($mailSettings['user'], 'Bind Admin');
		//Set an alternative reply-to address
		//$mail->addReplyTo('replyto@example.com', 'First Last');
		//Set who the message is to be sent to
		$mail->addAddress($this->email());
		//Set the subject line
		$mail->Subject = '[eThing] '.$subject;
		//set the text body
		$mail->isHTML(true); // accept html
		$mail->Body = $message;
		//send the message, check for errors
		if (!$mail->send()) {
			throw new \Ething\Exception("Mailer Error: " . $mail->ErrorInfo);
		}
	}
	
	
	public function remove() {
		
		// remove all the resources associated to this user
		$resources = $this->ething->find(array(
			'user' => $this->id()
		));
		foreach($resources as $r) {
			$r->remove();
		}
		
		// remove this user from the users collection
		$c = $this->ething->db()->selectCollection("users");
		$c->remove(array('_id' => $this->id()), array('justOne' => true));
		$this->_d = null;
		
	}
	
	
	public function set(array $props) {
		
		foreach($props as $key => &$value){
			
			$ret = false;
			
			switch($key){
				case 'email':
					$ret = is_string($value) && filter_var($value, FILTER_VALIDATE_EMAIL);
					break;
				case 'password':
					if(is_string($value) && preg_match(self::VALIDATE_PASSWORD, $value)){
						$value = md5($value);
						$ret = true;
					}
					break;
				case 'quota':
					$ret = (is_int($value) && $props['quota'] >= 0);
					break;
				default:
					throw new \Ething\Exception('invalid field "'.$key.'"');
			}
			
			if(!$ret)
				throw new \Ething\Exception('Invalid value for the field "'.$key.'"');
			
		}
		
		$this->_d = array_merge($this->_d,$props);
		$c = $this->ething->db()->selectCollection("users");
		$c->save($this->_d);
		
		return true;
	}
	
	
	
	// create a new user
	public static function create(Ething $ething, array $attr) {
		
		if(
			is_array($attr) &&
			isset($attr['name']) &&
			isset($attr['password']) &&
			isset($attr['email']) &&
			is_string($attr['name']) &&
			is_string($attr['password']) &&
			is_string($attr['email'])
		) {
			
			if(!preg_match(self::VALIDATE_NAME, $attr['name']))
				throw new \Ething\Exception('not a valid name. 25>=Length>=3. Allowed characters: letters (a-z), digits, dashes, points, apostrophes and underscores.');
			if(!preg_match(self::VALIDATE_PASSWORD, $attr['password'])) // hashed password
				throw new \Ething\Exception('not a valid password. Minimum 4 characters.');
			if(!filter_var($attr['email'], FILTER_VALIDATE_EMAIL))
				throw new \Ething\Exception('not a valid email');
			
			if(isset($attr['quota'])){
				if(!is_int($attr['quota']) || $attr['quota'] < 0)
					throw new \Ething\Exception('not a valid quota integer');
			}
			
			$c = $ething->db()->selectCollection("users");
			
			$data = array_merge(array(
				'quota' => 100000000
			),$attr,array(
				'_id' => ShortId::generate(),
				'createdDate' => new \MongoDate()
			));
			
			try {
				$c->insert($data);
			}
			catch(\MongoCursorException $e) {
				throw new \Ething\Exception('db error: '.$e->getMessage());
			}
			
			$u = new User($ething, $data);
			
			// create the data collection (used by table resources)
			$ething->db()->createCollection($u->dataCollectionName());
			
			return $u;
			
		}
		
		return null;
	}
	
	

}


