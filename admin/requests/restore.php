<?php


require_once __DIR__.'/inc.php';


	
if(!empty($_FILES) && isset($_FILES['file'])){
	
	
	if(!$_FILES['file']['size'])
		error('Empty file');
	
	$ething = ething_instanciate();

	$host = $ething->config('server.host');
	$port = $ething->config('server.port');
	$user = $ething->config('server.user');
	$password = $ething->config('server.password');
	$database = $ething->config('server.database');
	
	
	/* uncompress zip file */
	$zip = new ZipArchive;
	if ($zip->open($_FILES['file']['tmp_name']) === TRUE) {
		
		if($zip->numFiles==0)
			error('Empty archive');
		
		$tmpdir = create_tmpdir();
		
		$zip->extractTo($tmpdir);
		$zip->close();
	} else {
		error(new Exception('bad archive'));
	}
	
	// read the info file
	$infofile = $tmpdir.DIRECTORY_SEPARATOR.'info.json';
	if(!is_readable($infofile)){
		remove_dir($tmpdir);
		error(new Exception('The archive must contain an info.json file.'));
	}
	
	$info = json_decode(file_get_contents($infofile),true);
	if(!(is_array($info) && isset($info['version']))){
		remove_dir($tmpdir);
		error(new Exception('Invalid info.json file.'));
	}
	
	// version control
	if(version_compare($info['version'],\Ething\Ething::VERSION) != 0){
		// invalid version
		remove_dir($tmpdir);
		error(new Exception("The importing database is incompatible (version: '".$info['version']."', current : '".\Ething\Ething::VERSION."')"));
	}
	
	
	/* remove database first */
	try {
		$ething = ething_instanciate();
		$ething->db()->drop();
	}
	catch(Exception $e){
		remove_dir($tmpdir);
		error($e);
	}
	
	
	/* restore */
	$command = "mongorestore --db " . $database . " --drop";

	if(!empty($host))
		$command .= ' --host '.$host;
	if(!empty($port))
		$command .= ' --port '.$port;
	if(!empty($user) && !empty($password))
		$command .= ' --username '.$user.' --password '.$password;
	
	$command .= ' ' . $tmpdir;
	
	exec($command,$output,$return_code);
	
	/*var_dump($command);
	var_dump($return_code);
	var_dump($output);*/
	
	
}
else
	error(new Exception('Bad Request'));


