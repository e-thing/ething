<?php

namespace Ething;

class Scope
{

	const RESOURCE_WRITE = '/(^|\s)resource(\.owndata)?($|\s)/';   // check if a scope can write to a resource ?
	const RESOURCE_READ = '/(^|\s)resource($|\.|\s)/';             // check if a scope can read a resource ?
	const NOTIFICATION = '/(^|\s)notification($|\s)/';             // allow notification
	const PROFILE_WRITE = '/(^|\s)profile($|\s)/';                 // allow profile editing ?
	const PROFILE_READ = '/(^|\s)profile($|\.|\s)/';               // allow to see the profile ?
	const RESOURCE_OWNDATA = '/(^|\s)resource.owndata($|\s)/';     // allow a device to create resources and to read/write only those resources ?
	const RESOURCE_ALL = '/(^|\s)resource(\.readonly)?($|\s)/';    // allow to read to any resource ?
	const RESOURCE_ALL_WRITE = '/(^|\s)resource($|\s)/';           // allow to write to any resource ?
	
	
	
	public static $list = array(
		'resource', // allow to read and write to any resource
		'resource.readonly', // allow to read only to any resource
		'resource.owndata', // allow a device to create resources and to read/write only those resources (default)
		'notification',  // allow to send notification
		'profile', // allow to edit the profile of this user
		'profile.readonly', // allow to see the profile of this user
	);
	
	public static function valide(&$scope){
		if(empty($scope))
			$scope = '';
		if(is_string($scope)){
			$scopes = preg_split('/ +/',$scope);
			if(array_reduce($scopes, function($scope) {
				return in_array($scope, Scope::$list);
			}, true)){
				$scope = implode($scopes, ' ');
				return true;
			}
		}
		return false;
	}
	
	// ex:  Scope::check(Scope::RESOURCE_WRITE,$device);
	public static function check($scope, Resource $resource){
		return preg_match($scope,method_exists($resource,'scope') ? $resource->scope() : '')===1;
	}
	
}

