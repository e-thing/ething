<?php

/*
*
*  Generate a swagger documentation JSON file from comments found in source files
*
*/

$rootDir = __DIR__."/..";

require_once $rootDir.'/session/session.php';

if(!(php_sapi_name() === 'cli' || \Session\isAuthenticated())){
	http_response_code(401);
	exit(1);
}

$sources = array(
	"api/index.php",
	"src"
);



function echoErr($text=''){
	file_put_contents('php://stderr',$text.PHP_EOL);
}

function help(){
	echoErr();
	echoErr("usage: ".basename(__FILE__, '.php')." [-h|--help] [--ething-dir <ETHING_ROOT_DIR>]");
	echoErr();
	exit(1);
}


// command line arguments
while($arg = next($argv)){
	switch($arg){
		case "-h":
		case "--help":
			help();
		case "--ething-dir":
			$rootDir = next($argv);
			break;
		default:
			echoErr("ERROR: invalid argument '{$arg}'");
			help();
	}
}

if(!is_dir($rootDir)){
	echoErr("ERROR: invalid directory '{$rootDir}'");
	exit(1);
}



$out = 'php://stdout';;


if (!function_exists('json_last_error_msg')) {
	function json_last_error_msg() {
		static $ERRORS = array(
			JSON_ERROR_NONE => 'No error',
			JSON_ERROR_DEPTH => 'Maximum stack depth exceeded',
			JSON_ERROR_STATE_MISMATCH => 'State mismatch (invalid or malformed JSON)',
			JSON_ERROR_CTRL_CHAR => 'Control character error, possibly incorrectly encoded',
			JSON_ERROR_SYNTAX => 'Syntax error',
			JSON_ERROR_UTF8 => 'Malformed UTF-8 characters, possibly incorrectly encoded'
		);

		$error = json_last_error();
		return isset($ERRORS[$error]) ? $ERRORS[$error] : 'Unknown error';
	}
}



$swagger = array();


foreach ( $sources as $source ) {
	foreach (glob($rootDir.'/'.$source) as $filename) {
		
		if(is_dir($filename)){
			$it = new RegexIterator(new RecursiveIteratorIterator(new RecursiveDirectoryIterator($filename)), '/^.+\.php$/i', RecursiveRegexIterator::GET_MATCH);
			foreach($it as $path) {
			  try {
					$swagger = (object) array_merge_recursive((array) $swagger, (array) extractSwagger($path[0]));
				} catch(Exception $e){
					echoErr($e->getMessage());
					exit(1);
				}
			}
		} else {
			try {
				$swagger = (object) array_merge_recursive((array) $swagger, (array) extractSwagger($filename));
			} catch(Exception $e){
				echoErr($e->getMessage());
				exit(1);
			}
		}
	}
}


$content = json_encode($swagger,JSON_PRETTY_PRINT|JSON_UNESCAPED_SLASHES );
file_put_contents($out,$content);


function extractSwagger($file){
	
	$handle = fopen($file, "r");
	if ($handle) {
		$comment = false;
		$print = false;
		$blocs = array();
		$linecount = 0;
		$swagger = array();
		
		while (($line = fgets($handle)) !== false) {
			$linecount++;
			
			if(!$comment && preg_match('/\/\*/',$line)){
				$comment = true;
				$print = false;
			}
			
			
			
			if($print){
				$lcp = $line;
				// remove any comment symbol
				$lcp = preg_replace('/^[\s]*\*\/?/','',$lcp);
				
				//$lcp = preg_replace('/^[\s]*[*\/\\\]+/','',$lcp);
				//$lcp = preg_replace('/^.*\/\*/','',$lcp);
				//$lcp = preg_replace('/\*\/.*$/','',$lcp);
				//$lcp = preg_replace('/^[\s]*\*/','',$lcp);
				
				$bloc['data'] .= $lcp;
			}
			
			if(preg_match('/^[\s*]*@([\w\-_]+)/',$line,$matches)){
				if($print = !!preg_match('/swagger(-([\w\-_]+))?/',$matches[1],$matches)){
					$bloc = array(
						'tag' => count($matches)>2 ? $matches[2] : '',
						'data' => '',
						'line' => $linecount
					);
				}
				else if(isset($bloc)){
					$blocs[] = $bloc;
					unset($bloc);
				}
			}
			
			
			if($comment && preg_match('/\*\//',$line)){
				$comment = false;
				$print = false;
				
				if(isset($bloc)){
					$blocs[] = $bloc;
					unset($bloc);
				}
			}
			
			
		}
		
		//var_dump($blocs);
		
		
		//transform the blocs into Swagger JSON
		
		foreach($blocs as $bloc){
			
			if(!preg_match('/^[\s]*{/',$bloc['data'])){
				$bloc['data'] = '{'.$bloc['data'].'}';
			}
			
			// transform multiline string
			$inString = false;
			$inlinedStr = '';
			for($i=0; $i<strlen($bloc['data']); $i++){
				$letter=$bloc['data'][$i];
				if($letter==='"' && $bloc['data'][$i-1]!='\\'){
					$inString = !$inString;
				}
				else if($inString && ord($letter) == 10){ // \n
					$letter = '\n';
				}
				else if($inString && ord($letter) == 13){ // \r
					$letter = '\r';
				}
				else if($inString && ord($letter) == 9){ // \t
					$letter = '\t';
				}
				$inlinedStr .= $letter;
				
			}
			$bloc['data'] = $inlinedStr;
			
			
			
			$bloc['json'] = json_decode($bloc['data']);
			
			if(json_last_error() === JSON_ERROR_NONE){
				
				$s = array();
				
				switch($bloc['tag']){
					case 'path':
						foreach($bloc['json'] as &$path){
							foreach($path as &$method){
								if(is_object($method)){
									if(!isset($method->description))
										$method->description = "";
									
									// clean heading and trailing space
									$method->description = preg_replace('/^[\s\n\r]*/','',$method->description);
									$method->description = preg_replace('/[\s\n\r]*$/','',$method->description);
									
									if(!isset($method->summary)){
										$summaryMaxLength = 120;
										$p = strpos($method->description, '.');
										if($p === false && strlen($method->description) <= $summaryMaxLength)
											$method->summary = $method->description;
										else if($p === false || $p > $summaryMaxLength ){
											// Ellipsis
											$p = strrpos(substr($method->description,0,$summaryMaxLength),' ');
											if($p === false)
												$p = $summaryMaxLength;
											$method->summary = substr($method->description,0,$p).'...';
										}
										else {
											// the summary is the first sentence or the description
											$method->summary = substr($method->description,0,$p+1);
										}
									}
								}
							}
						}
						$s['paths'] = $bloc['json'];
						break;
					case 'definition':
						$s['definitions'] = $bloc['json'];
						break;
					case '';
						$s = $bloc['json'];
						break;
					default:
						throw new Exception('unknown tag '.$bloc['tag']);
				}
				
				$swagger = (object) array_merge_recursive((array) $swagger, (array) $s);
				
			}
			else {
				throw new Exception("Invalid JSON at line ".$bloc['line']." in the file ".$file."\n".json_last_error_msg()."\njson:\n".$bloc['data']."\n");
			}
			
			
		}
		
		

		fclose($handle);
	} else {
		throw new Exception("unable to open the file");
	}
	
	
	return $swagger;
	
}




?>
