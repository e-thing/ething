<?php

$rootDir = __DIR__.'/..';

require_once $rootDir.'/vendor/autoload.php';
require_once $rootDir.'/src/Ething.php';
require_once $rootDir.'/session/session.php';

if(!(php_sapi_name() === 'cli' || \Session\isAuthenticated())){
	http_response_code(401);
	exit(1);
}

function check_ething_version(){
	return \Ething\Ething::VERSION;
}

function check_web_server(){
	return $_SERVER['SERVER_SOFTWARE'];
}

function check_php_version(){
	
	$phpVersion = phpversion();
	$phpVersionMin = '5.4.0';
	if(version_compare($phpVersion, $phpVersionMin, '<')){
		throw new Exception('Upgrade PHP '.$phpVersion.' < '.$phpVersionMin);
	}
	else
		return $phpVersion;
}

function check_mongodb_driver(){
	
	$mongoVersion = phpversion('mongodb');
	$mongoVersionMin = '1.2.0';
	if(!extension_loaded('mongodb') || $mongoVersion === false){
		throw new Exception('The mongodb PHP driver is not installed');
	}
	else if(version_compare($mongoVersion, $mongoVersionMin, '<')){
		throw new Exception('Upgrade mongodb PHP driver '.$mongoVersion.' < '.$mongoVersionMin);
	}
	else
		return $mongoVersion;
}

function check_curl_plugin(){

	if(!extension_loaded('curl')){
		throw new Exception('The curl PHP extension is not installed');
	}
	
	$curlVersion = curl_version()['version'];
	$curlVersionMin = '7.0.0';
	if(version_compare($curlVersion, $curlVersionMin, '<')){
		throw new Exception('Upgrade curl PHP extension '.$curlVersion.' < '.$curlVersionMin);
	}
	else
		return $curlVersion;
}

function check_gd_plugin(){
	if(!(extension_loaded('gd') && function_exists('gd_info'))){
		throw new Exception('The GD PHP library is not installed');
	}
	$info = gd_info();
	$gdVersion = isset($info['GD Version']) ? $info['GD Version'] : 'unknown';
	return $gdVersion;
}

function check_database(){
	try {
		$ething = new \Ething\Ething();
		
		$mongodb_info = $ething->db()->command(array('buildinfo'=>true))->toArray();
		$mongodb_version = $mongodb_info[0]['version'];
		
		return 'connected ; MongoDB version:'.$mongodb_version;
	} catch(\Exception $e) {
		throw new Exception('unable to connect to the database ['.$e->getMessage().']');
	}
}

function check_http_request(){
	
	$ething = new \Ething\Ething();
	
	if(!\Ething\Proxy::get($ething, 'http://example.com/')){
		throw new Exception('unable to make a http request (check your proxy settings)');
	}
	
	return true;
}

function check_mongodb_cli(){
	
	$command = "mongo --version";
	
	$results = shell_exec($command);
	
	if(empty($results))
		throw new Exception('unable to execute MongoDB command line');
	else
		return $results;
}

function check_deamon_running(){
	
	try {
		
		$ething = new \Ething\Ething();
		
		if(!$ething->deamon('info', $stream))
			throw new Exception();
		
		if(preg_match('/uptime=([0-9]+)/',$stream->data(),$matches)){
			$seconds = intval($matches[1]);
			$days = floor($seconds / 86400);
			$seconds -= $days * 86400;
			$H = floor($seconds / 3600);
			$i = ($seconds / 60) % 60;
			$s = $seconds % 60;
			return sprintf("running for %d day(s) %d hour(s) %d minute(s) and %d seconde(s)", $days, $H, $i, $s);
		}
	} catch(\Exception $e) {
		throw new Exception("the deamon is not running");
	}
	
	return true;
}

function check_config(){
	
	$ething = new \Ething\Ething();
	$ething->config->check();
	
	return true;
}


function check_avconv(){
	
	$command = "avconv -version";
	
	$results = shell_exec($command);
	
	if(empty($results))
		throw new Exception('unable to find avconv');
	else
		return preg_split('/[\\r\\n]/', $results, 2)[0];
}

function check_python(){
	
	$command = "python -V 2>&1";
	
	$results = shell_exec($command);
	
	if(empty($results))
		throw new Exception('unable to find python');
	else {
		exec("python pycheck.py 2>&1", $lines, $return_var);
		if($return_var!==0){
			array_unshift($lines, $results);
			$results = implode(', ',$lines);
			throw new Exception($results);
		}
	}
	
	return $results;
}

function check_mosquitto(){
	
	exec("mosquitto -h", $lines, $return_var);
	
	if($return_var===0 || $return_var===3){
		return $lines[0];
	} else {
		throw new Exception('mosquitto not installed');
	}
	
}


function check_nodejs(){
	
	$command = "node --version 2>&1";
	
	$results = shell_exec($command);
	
	if(empty($results))
		throw new Exception('unable to find node');
	else {
		exec("node nodecheck.js 2>&1", $lines, $return_var);
		if($return_var!==0){
			array_unshift($lines, $results);
			$results = implode(', ',$lines);
			throw new Exception($results);
		}
	}
	
	return $results;
}

$tests = array(
	
	array(
		'name' => 'e-Thing',
		'fct' => 'check_ething_version'
	),
	array(
		'name' => 'WEB Server',
		'fct' => 'check_web_server'
	),
	array(
		'name' => 'PHP version',
		'fct' => 'check_php_version'
	),
	array(
		'name' => 'mongodb PHP driver',
		'fct' => 'check_mongodb_driver'
	),
	array(
		'name' => 'database',
		'fct' => 'check_database'
	),
	/*array(
		'name' => 'MongoDB CLI',
		'fct' => 'check_mongodb_cli'
	),*/
	array(
		'name' => 'curl PHP plugin',
		'fct' => 'check_curl_plugin'
	),
	array(
		'name' => 'GD PHP library',
		'fct' => 'check_gd_plugin'
	),
	
	array(
		'name' => 'HTTP request',
		'fct' => 'check_http_request'
	),
	array(
		'name' => 'Deamon',
		'fct' => 'check_deamon_running'
	),
	array(
		'name' => 'Config',
		'fct' => 'check_config'
	),
	array(
		'name' => 'avconv',
		'fct' => 'check_avconv'
	),
	array(
		'name' => 'python',
		'fct' => 'check_python'
	),
	array(
		'name' => 'nodejs',
		'fct' => 'check_nodejs'
	),
	array(
		'name' => 'mosquitto',
		'fct' => 'check_mosquitto'
	)
	
	
);


$results = array();

foreach($tests as $test){
	
	if(is_callable($test['fct'])){
		
		$result = array(
			'name' => $test['name'],
			'ok' => true,
			'message' => ''
		);
		
		try {
			$r = call_user_func($test['fct']);
			$result['message'] = is_string($r) ? $r : 'ok';
		}
		catch(\Exception $e){
			
			$result['ok'] = false;
			$result['message'] = $e->getMessage();
		}
		
		$results[] = $result;
	}
}

header('Content-Type: application/json');
echo json_encode($results,JSON_PRETTY_PRINT|JSON_UNESCAPED_SLASHES);

