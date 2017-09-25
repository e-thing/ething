<?php
	
namespace Ething;
	

	
	
class Helpers
{
	
	static public function array_filter_recursive( array $array, $callback, $keyPrefix = '' ){
		$out = array();
		
		foreach($array as $key => $value){
			
			if(self::is_assoc($value)){
				$res = self::array_filter_recursive($value, $callback, $keyPrefix.$key.'.');
				if(!empty($res))
					$out[$key] = $res;
			} else {
				$res = call_user_func($callback, $keyPrefix.$key, $value);
				if($res === false) continue;
				$out[$key] = $value;
			}
			
		}
		
		return $out;
	}
	
	static public function is_assoc($array) {
		if(!is_array($array)) return false;
		
		// Keys of the array
		$keys = array_keys($array);

		// If the array keys of the keys match the keys, then the array must
		// not be associative (e.g. the keys array looked like {0:0, 1:1...}).
		return array_keys($keys) !== $keys;
	}
	
	static public function is_numeric_array($array) {
		return is_array($array) && !static::is_assoc($array);
	}
	
	static public function array_to_object_recursive( array $array ){
		$obj = new \stdClass;
		foreach($array as $k => $v) {
		 if(strlen($k)) {
			if(static::is_assoc($v)) {
			   $obj->{$k} = static::array_to_object_recursive($v);
			} else {
			   $obj->{$k} = $v;
			}
		 }
		}
		return $obj;
	}
	
	static public function object_to_array_recursive( $object ){
		return json_decode(json_encode($object), true);
	}
	
	
	static public function isLocalClient(){
		if(isset($_SERVER['REMOTE_ADDR'])){
			return in_array($_SERVER['REMOTE_ADDR'], array('127.0.0.1','::1')) || !filter_var($_SERVER['REMOTE_ADDR'], FILTER_VALIDATE_IP, FILTER_FLAG_NO_PRIV_RANGE);
		}
		return false;
	}
	
	
	static public function array_diff(array $arr1, array $arr2){
		$kdiff = array();
		foreach($arr1 as $k1 => $v1){
			
			$found = false;
			foreach($arr2 as $k2 => $v2){
				if($k1 === $k2){
					$found = true;
					if($v1 !== $v2){
						$kdiff[] = $k1; // key value changed
					}
					break;
				}
			}
			if(!$found)
				$kdiff[] = $k1; // key removed
			
		}
		
		$arrkeys1 = array_keys($arr1);
		foreach($arr2 as $k2 => $v2){
			if(!in_array($k2, $arrkeys1))
				$kdiff[] = $k2; // new key
		}
		
		return $kdiff;
	}
	
	static public function percent_replace($str, $callback){
		$replace=false;
		for($i=0; $i<strlen($str); $i++){
			$c = $str[$i];
			if($replace){
				$rep = call_user_func($callback, '%'.$c);
				if(is_string($rep)){
					$str = substr_replace($str, $rep, $i-1, 2);
					$i = $i - 1 + strlen($rep) - 1;
				}
				$replace = false;
			}
			else if($c==='%'){
				$replace = true;
			}
		}
		return $str;
	}

}


