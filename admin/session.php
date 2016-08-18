<?php
// check if the session still exist

$redirect = true;


session_name('ADMIN_SESSION');

if(!empty($_COOKIE[session_name()])){
	
	session_start();
	
	if(!empty($_SESSION['authenticated']))
		$redirect = false;
}


if($redirect) 
{
  header('Location: authentification.php');
  exit();
}


/* ething */

$rootPath = __DIR__.'/..';

$config = include($rootPath.'/config.php');

require_once $rootPath.'/vendor/autoload.php';
require_once $rootPath.'/src/Ething.php';

$ething_instance_ = null;

if(!function_exists('ething_instanciate')){
	function ething_instanciate(){
		global $config, $ething_instance_;
		return $ething_instance_ ? $ething_instance_ : new \Ething\Ething($config);
	}
}

