<?php


require_once __DIR__.'/inc.php';



if( !empty($_POST) &&
	!empty($_POST['id']) &&
	isset($_POST['password']) && 
	isset($_POST['email']) &&
	isset($_POST['quota']) && is_numeric($_POST['quota'])
){
	
	// check the inputs
	if(empty($_POST['password']))
		error('empty password');
	if(empty($_POST['email']))
		error('empty email');
	
	
	try {
		$ething = ething_instanciate();
		
		$user = $ething->findOneUserById($_POST['id']);
		if(!$user)
			throw new Exception('unknown user');
		
		$props = array(
			'email' => $_POST['email'],
			'quota' => intval($_POST['quota'])*1000000
		);
		
		if(!empty($_POST['password']))
			$props['password'] = $_POST['password'];
		
		$user->set($props);
		
	}
	catch(Exception $e){
		error($e);
	}
	
}
else
	error(new Exception('Bad Request'));
	
