<?php

namespace Ething;

class Scope
{
    
	
	public static $list = array(
		
		'resource:read' => array(
			'description' => 'read the content of any resource'
		),
		'resource:write' => array(
			'description' => 'create resources of any kind and modify the content of any resource'
		),
		'resource:admin' => array(
			'description' => 'modify resource properties, delete resource and access to apikeys'
		),
		'file:read' => array(
			'description' => 'read the content of any file'
		),
		'file:write' => array(
			'description' => 'create files and modify the content of any file'
		),
		'table:read' => array(
			'description' => 'read the content of any table'
		),
		'table:write' => array(
			'description' => 'create tables and modify the content of any table'
		),
		'table:append' => array(
			'description' => 'append data to any existing table'
		),
		'app:read' => array(
			'description' => 'read the raw script content of any apps'
		),
		'app:write' => array(
			'description' => 'create and edit apps'
		),
		'app:execute' => array(
			'description' => 'execute apps'
		),
		'device:read' => array(
			'description' => 'send GET request to any device'
		),
		'device:write' => array(
			'description' => 'send POST,PUT,PATCH,DELETE request to any device'
		),
		'notification' => array(
			'description' => 'send notification'
		),
		'settings:read' => array(
			'description' => 'read the settings'
		),
		'settings:write' => array(
			'description' => 'modify the settings'
		),
		'proxy:read' => array(
			'description' => 'send GET request through your local network'
		),
		'proxy:write' => array(
			'description' => 'send POST,PUT,PATCH,DELETE through your local network'
		),
		'rule:read' => array(
			'description' => 'read rules attributes'
		),
		'rule:write' => array(
			'description' => 'create rules'
		),
		'rule:execute' => array(
			'description' => 'execute rules'
		),
		'rule:admin' => array(
			'description' => 'delete rules'
		)
		
		
	);
	
	
	static public function validate(&$scopes){
		if(is_string($scopes)){
			$_scopes = array();
			foreach( explode(' ',$scopes) as $scope ){
				if(!$scope) continue;
				if(!array_key_exists($scope,static::$list)) return false;
				$_scopes[] = $scope;
			}
			$scopes = implode(' ',$_scopes);
			return true;
		}
		return false;
	}
	
	
}

