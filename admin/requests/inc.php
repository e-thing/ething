<?php
	
	require_once __DIR__.'/../session.php';
	
	if(!function_exists('error')){
		function error($e = 'unknown error'){
			
			if(is_string($e)){
				$e = new Exception($e);
			}
			
			// set the response code
			$responseCode = $e->getCode() > 0 ? $e->getCode() : 400 ;
			http_response_code($responseCode);
			// send the error message as JSON
			header('Content-Type: application/json');
			$error = array(
				'message' => $e->getMessage(),
				'code' => $responseCode
			);
			echo json_encode($error);
			
			exit();
		}
	}
	
	if(!function_exists('create_tmpdir')){
		function create_tmpdir(){
			$systmpdir = sys_get_temp_dir();
			if(empty($systmpdir))
				error(new Exception('Unable to create the tmp directory'));

			// remove trailing slash if there is any !
			$systmpdir = preg_replace('/(\/|\\\)$/','',$systmpdir);

			$tmpdir = $systmpdir.DIRECTORY_SEPARATOR.uniqid('ething_');

			if(!is_dir($tmpdir)){
				if(!mkdir($tmpdir)){
					error(new Exception('Unable to create the tmp directory'));
				}
			}

			if(!is_writable($tmpdir)){
				error(new Exception('No write access to tmp directory'));
			}
			
			return $tmpdir;
		}
	}
	
	if(!function_exists('remove_dir')){
		function remove_dir($src) {
			$dir = opendir($src);
			while(false !== ( $file = readdir($dir)) ) {
				if (( $file != '.' ) && ( $file != '..' )) {
					$full = $src . '/' . $file;
					if ( is_dir($full) ) {
						remove_dir($full);
					}
					else {
						unlink($full);
					}
				}
			}
			closedir($dir);
			rmdir($src);
		}
	}
	
	
	