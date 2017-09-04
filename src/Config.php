<?php
	
namespace Ething;
	
/**
 * @swagger-definition
 * "Settings":{
 *   "type": "object",
 *   "description": "The settings object",
 * 	 "properties":{}
 * }
 */

define('ETHING_CONFIG_FILE', __DIR__.'/../config.json');
define('ETHING_LOG_FILE', __DIR__.'/../log/ething.log');
	
class Config implements \JsonSerializable
{
	
	const READ = 0x1;
	const WRITE = 0x2;
	const READWRITE = 0x3;
	
	static private $publicAccessPolicy = array(
		'path' => self::READWRITE,
		'db.host' => self::READWRITE,
		'db.port' => self::READWRITE,
		'db.user' => self::READWRITE,
		'db.password' => self::WRITE,
		'db.database' => self::READWRITE,
		'proxy' => self::READWRITE,
		'proxy.host' => self::READWRITE,
		'proxy.port' => self::READWRITE,
		'proxy.user' => self::READWRITE,
		'proxy.password' => self::WRITE,
		'auth.localonly' => self::READWRITE,
		'auth.password' => self::WRITE,
		'notification' => self::READWRITE,
		'notification.emails' => self::READWRITE,
		'notification.smtp' => self::READWRITE,
		'notification.smtp.host' => self::READWRITE,
		'notification.smtp.port' => self::READWRITE,
		'notification.smtp.user' => self::READWRITE,
		'notification.smtp.password' => self::WRITE,
		'cors' => self::READWRITE,
		'log' => self::READWRITE,
		'log.file' => self::READWRITE,
		'log.level' => self::READWRITE,
		'mqtt.host' => self::READWRITE,
		'mqtt.port' => self::READWRITE,
		'mqtt.user' => self::READWRITE,
		'mqtt.password' => self::WRITE,
		'mqtt.clientId' => self::READWRITE,
		'mqtt.rootTopic' => self::READWRITE,
		'script.timeout' => self::READWRITE
	);
	
	// default configuration
	private $_d = array(
		
		// url path, the API is accessible by default to http://localhost/ething/api
		'path' => '/ething',
		
		// mongoDB server
		'db' => array(
			'host' => 'localhost',
			'port' => 27017,
			'user' => null,
			'password' => null,
			'database' => "ething"
		),
		
		// (set to false to disable this feature)
		'notification' => array(
			'emails' => array(),
			
			/*'smtp' = array(
				'host'=> 'smtp.gmail.com',
				'port' => 587,
				'user' => '<username>@gmail.com',
				'password' => '<password>'
			),*/
			'smtp' => false
		),
		
		// if your server is behind a proxy, set the proxy address here (e.g. proxy.example.com:5100)
		/*
		 'proxy' => array(
			'host'=> 'proxy-host',
			'port' => 8080,
			'user' => null,
			'password' => null
		)
		*/
		'proxy' => false,
		
		'auth' => array(
			'password' => 'admin',
			'localonly' => false
		),
		
		// enable Cross-origin resource sharing (CORS)
		'cors' => true,
		
		// debug information is given in the error messages send through HTTP requests
		'debug' => true,
		
		// logging. Set to false to disable logging.
		'log' => array(
			'file' => ETHING_LOG_FILE, // if not given, log will be written in the database
			'level' => Logger::INFO
		),
		
		'session' => array(
			'expiration' => 86400, // in seconds, the time after which a session is expired
			'cookie_name' => 'ething_session',
			'secret' => 'taupesecretstring' // must not be shared
		),
		
		'daemon' => array(
			'host' => '127.0.0.1',
			'port' => 24934,
			'timeout' => 10 // in seconds
		),
		
		/*
		"mqtt": {
			"host": "127.0.0.1",
			"port": 1883,
			"clientId": "ething",
			"rootTopic": "ething/"
		}
		*/
		'mqtt' => false,
		
		'script' => array(
			'timeout' => 300000 // in millisecondes
		)
		
	);
	
	const VALIDATE_PASSWORD = '/^.{4,}$/';
	
	private $filename;
	
	public function __construct($configFilename = null) // Constructeur
	{
		$this->filename = !empty($configFilename) ? $configFilename : ETHING_CONFIG_FILE;
	}
	
	public function load(){
		if(!file_exists($this->filename)){
			$this->save();
		}
		else if(is_readable($this->filename)){
			$content = file_get_contents($this->filename);
			$content = json_decode($content, true);
			if(is_array($content)){
				$this->_d = array_replace_recursive($this->_d, $content);
			} else {
				// invalid content
				return false;
			}
		} else {
			return false;
		}
		return true;
	}
	
	public function check(){
		if(!file_exists($this->filename))
			throw new Exception('no config file found');
		if(!is_readable($this->filename))
			throw new Exception('config file : no read permission');
		if(!is_writable($this->filename))
			throw new Exception('config file : no write permission');
		return true;
	}
	
	public function save(){
		@file_put_contents ($this->filename, json_encode($this->_d, JSON_PRETTY_PRINT|JSON_UNESCAPED_SLASHES));
	}
	
	// get/set attribute
	public function attr($name, $value = null)
	{
		if(is_object($name))
			$name = (array)$name;
		
		if (is_array($name)) {
			
			foreach($name as $key => $v){
				$this->attr($key, $v);
			}
			
		} else {
			
			if(is_object($value))
				$value = (array)$value;
			
			if (func_num_args() === 2 && Helpers::is_assoc($value)) {
				foreach($value as $key => $v){
					$this->attr("$name.$key", $v);
				}
			} else {
				
				if (func_num_args() === 1) {
					
					$path = explode('.',$name);
					$p = &$this->_d;
					foreach($path as $k){
						if(is_array($p) && isset($p[$k]))
							$p = &$p[$k];
						else
							return null;
					}
					
					return $p;
				} else {
					
					// setter
					
					if(!isset(static::$publicAccessPolicy[$name]) || !(static::$publicAccessPolicy[$name] & static::WRITE))
						throw new Exception('field "'.$name.'" cannot be set');
					
					switch($name){
						case 'notification.emails':
							$ok = false;
							if(is_array($value)){
								$ok = true;
								foreach($value as $email){
									if(!(is_string($email) && filter_var($email, FILTER_VALIDATE_EMAIL))){
										$ok = false;
										break;
									}
								}
							}
							if(!$ok) throw new Exception('emails must be an array of email');
							break;
						case 'auth.localonly':
						case 'cors':
							if(!is_bool($value))
								throw new Exception("$name must be a boolean");
							break;
						case 'auth.password':
							if(!(is_string($value) && preg_match(self::VALIDATE_PASSWORD, $value)))
								throw new Exception('auth.password must be a string (min. length = 4 cahracters)');
							$value = md5($value);
							break;
						case 'script.timeout':
							if(!(is_int($value) && $value >= 0))
								throw new Exception('script.timeout must be an integer >= 0');
							break;
						case 'proxy':
						case 'notification':
						case 'notification.smtp':
						case 'log':
							if(!is_null($value) && $value!==false)
								throw new Exception("$name is invalid");
							break;
						case 'db.host':
						case 'db.user':
						case 'db.password':
						case 'proxy.host':
						case 'proxy.user':
						case 'proxy.password':
						case 'notification.smtp.host':
						case 'notification.smtp.user':
						case 'notification.smtp.password':
						case 'mqtt.host':
						case 'mqtt.user':
						case 'mqtt.password':
						case 'mqtt.clientId':
							if(!is_string($value) || empty($value))
								throw new Exception("$name must be a non empty string");
							break;
						case 'mqtt.rootTopic':
							if(!is_string($value))
								throw new Exception("$name must be a string");
							break;
						case 'db.port':
						case 'proxy.port':
						case 'notification.smtp.port':
						case 'mqtt.port':
							if(!(is_int($value) && $value >= 0 && $value <= 65535))
								throw new Exception("$name must be a valid port number");
							break;
						
						case 'log.file':
							if(!is_bool($value))
								throw new Exception("$name must be a boolean");
							$value = $value ? ETHING_LOG_FILE : false;
							break;
						case 'log.level':
							if(!(is_int($value) && $value >= Logger::TRACE && $value <= Logger::FATAL))
								throw new Exception("$name must be a valid log level number");
							break;
						
						default:
							throw new Exception('unknown field "'.$name.'"');
					}
					
					$path = explode('.',$name);
					$p = &$this->_d;
					foreach($path as $k){
						if(!isset($p[$k]) || !is_array($p[$k]))
							$p[$k] = array();
						$p = &$p[$k];
					}
					
					$p = $value;
				}
			}
		}
	}
	
	public function __get($name){
		return $this->attr($name);
    }
	
	public function __set($name, $value){
		$this->attr($name, $value);
    }
	
	public function __invoke() {
		return call_user_func_array(array($this, 'attr'), func_get_args());
    }
	
	public function jsonSerialize() {
		return Helpers::array_filter_recursive($this->_d, function($key){
			return isset(static::$publicAccessPolicy[$key]) && (static::$publicAccessPolicy[$key] & static::READ);
		});
	}
	
	

}


