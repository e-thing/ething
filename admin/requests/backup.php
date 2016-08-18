<?php


require_once __DIR__.'/inc.php';



$tmpdir = create_tmpdir();

$ething = ething_instanciate();

$host = $ething->config('server.host');
$port = $ething->config('server.port');
$user = $ething->config('server.user');
$password = $ething->config('server.password');
$database = $ething->config('server.database');

	
$command = "mongodump --db " . $database;

if(!empty($host))
	$command .= ' --host '.$host;
if(!empty($port))
	$command .= ' --port '.$port;
if(!empty($user) && !empty($password))
	$command .= ' --username '.$user.' --password '.$password;

$command .= ' --out '.$tmpdir;

exec($command,$output,$return_code);


$dboutFolder = $tmpdir . DIRECTORY_SEPARATOR . $database;

if(!is_dir($dboutFolder)){
	remove_dir($tmpdir);
	error(new Exception('Error in mongodump execution.'));
}
	
/* zip file */
$files = new RecursiveIteratorIterator(new RecursiveDirectoryIterator($dboutFolder, RecursiveDirectoryIterator::SKIP_DOTS), RecursiveIteratorIterator::CHILD_FIRST);

// Initialize archive object
$zip = new ZipArchive;
$zipfilename = $tmpdir . DIRECTORY_SEPARATOR . 'ething_db_' . date('Ymd_His') . '.zip';
$zip->open( $zipfilename, ZipArchive::CREATE | ZipArchive::OVERWRITE);
foreach($files as $file) {
	if ($file->isFile())
		$zip->addFile($file->getRealPath(), $file->getBasename());
}
// add a info file
$zip->addFromString('info.json',json_encode(array(
	'version' => \Ething\Ething::VERSION,
	'date' => date(\DateTime::RFC3339),
	'host' => $host,
	'port' => $port,
	'database' => $database
),JSON_PRETTY_PRINT));
$zip->close();


/* send file to the user */
header('Content-Type: application/octet-stream');
header("Content-Transfer-Encoding: Binary"); 
header("Content-disposition: attachment; filename=\"" . basename($zipfilename) . "\""); 
readfile($zipfilename);


/* remove temporary dir */
remove_dir($tmpdir);


	

