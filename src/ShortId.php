<?php


namespace Ething;

use RandomLib\Factory;

class ShortId {
	
	
	static private $randomGenerator = null;
	
	// length of the identifier (must be between 7 and 14)
    static private $length = 7;
    // alphabet to use when generating the identifier (must be 64 characters long)
    static private $alphabet = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_-';
	
	
	static public function generate(){
		
		if(static::$randomGenerator === null){
            $factory = new Factory();
            static::$randomGenerator = $factory->getMediumStrengthGenerator();
        }
		
		return static::$randomGenerator->generateString(static::$length, static::$alphabet);
	}
	
	static public function validate($id){
		return is_string($id) && strlen($id)==static::$length && strspn($id, static::$alphabet)==static::$length;
	}
	
}
