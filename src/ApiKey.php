<?php

namespace Ething;

class ApiKey implements \JsonSerializable {
	
	public function __construct($doc)
	{
		$this->_d = $doc;
	}
	
	public function key(){
		return $this->_d['key'];
	}
	
	public function createdDate() {
		return $this->_d['createdDate']->sec;
	}
	
	public function data(){
		return $this->_d;
	}
	
	public static function generate(){
		$doc = array(
			'key' => self::uuid(),
			'createdDate' => new \MongoDate()
		);
		return new ApiKey($doc);
	}
	
	public function jsonSerialize() {
		$d = $this->_d;
		$d['createdDate'] = $d['createdDate']->sec;
		return $d;
	}
	
	/**
	 * 
	 * Generate v4 UUID
	 * 
	 * Version 4 UUIDs are pseudo-random.
	 *
	 * link : http://www.php.net/manual/en/function.uniqid.php#94959
	 */
	public static function uuid()
	{
		return sprintf('%04x%04x-%04x-%04x-%04x-%04x%04x%04x',
		// 32 bits for "time_low"
		mt_rand(0, 0xffff), mt_rand(0, 0xffff),
		// 16 bits for "time_mid"
		mt_rand(0, 0xffff),
		// 16 bits for "time_hi_and_version",
		// four most significant bits holds version number 4
		mt_rand(0, 0x0fff) | 0x4000,
		// 16 bits, 8 bits for "clk_seq_hi_res",
		// 8 bits for "clk_seq_low",
		// two most significant bits holds zero and one for variant DCE1.1
		mt_rand(0, 0x3fff) | 0x8000,
		// 48 bits for "node"
		mt_rand(0, 0xffff), mt_rand(0, 0xffff), mt_rand(0, 0xffff)
		);
	}
	
	
}

