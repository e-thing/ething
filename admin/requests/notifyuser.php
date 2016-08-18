<?php


require_once __DIR__.'/inc.php';




if( !empty($_POST) &&
	!empty($_POST['id']) &&
	isset($_POST['subject'])
){
	
	if(empty($_POST['subject']))
		error('empty subject');
	
	try {
		$ething = ething_instanciate();
		
		$user = $ething->findOneUserById($_POST['id']);
		if(!$user)
			throw new Exception('unknown user');
		
		$user->sendMail($_POST['subject'], isset($_POST['message']) ? $_POST['message'] : null);
		
	}
	catch(Exception $e){
		error($e);
	}
	
	
}
else
	error(new Exception('Bad Request'));
	



	

