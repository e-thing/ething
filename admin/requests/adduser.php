<?php


require_once __DIR__.'/inc.php';



if( !empty($_POST) &&
	isset($_POST['user']) && 
	isset($_POST['password']) && 
	isset($_POST['email']) &&
	isset($_POST['quota']) && is_numeric($_POST['quota'])
){
	
	// check the inputs
	if(empty($_POST['user']))
		error('empty user name');
	if(empty($_POST['password']))
		error('empty password');
	if(empty($_POST['email']))
		error('empty email');
	
	
	try {
		$ething = ething_instanciate();
		
		$user = $ething->createUser(array(
			'name' => $_POST['user'],
			'password' => md5($_POST['password']),
			'email' => $_POST['email'],
			'quota' => intval($_POST['quota'])*1000000
		));
		
	}
	catch(Exception $e){
		error($e);
	}
	
	if(isset($user)){
		
		$readmeFilePath = __DIR__.'/../../readme.adoc';
		
		if(file_exists($readmeFilePath) && is_readable($readmeFilePath)){
			
			$file = $ething->create($user,array(
				'name' => basename($readmeFilePath)
			));
			
			$file->write(file_get_contents($readmeFilePath));
			
		}
		
	}
	
	
}
else
	error(new Exception('Bad Request'));
	
