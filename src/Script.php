<?php
	
namespace Ething;


use \Ething\File;
use \Ething\Exception;

class Script
{
	
	const PROG = __DIR__.'/nodejs/vm.js';
	
	static public function run(Ething $ething, $script, array $globals = null){
		
		$prog = self::PROG;
		
		if(!file_exists($prog)){
			throw new Exception("unable to execute {$prog}");
			return false;
		}
		
		
		
		// temporary files
		$scriptHdl = tmpfile();
		fwrite($scriptHdl, $script);
		$stdoutHdl = tmpfile();
		$stderrHdl = tmpfile();
		$resultHdl = tmpfile();
		
		$cmd = "node {$prog} ".stream_get_meta_data($scriptHdl)['uri']." --result ".stream_get_meta_data($resultHdl)['uri']." --stdout ".stream_get_meta_data($stdoutHdl)['uri']." --stderr ".stream_get_meta_data($stderrHdl)['uri'];
		
		$cmd .= ' --apiUrl "'.\addslashes($ething->config('path')).'"';
		$cmd .= ' --user ething';
		$cmd .= ' --password "'.\addslashes($ething->config('auth.password')).'"';
		$cmd .= ' -t '.$ething->config('script.timeout');
		
		if(is_array($globals) && !empty($globals)){
			$cmd .= ' --globals "'.\addslashes(\json_encode($globals)).'"';
		}
		
		$cmd .= ' 2>&1';
		
		$time_start = microtime(true);
		exec($cmd, $output, $return_var);
		$time_end = microtime(true);
		
		$stdout = stream_get_contents($stdoutHdl);
		$stderr = stream_get_contents($stderrHdl);
		$result = stream_get_contents($resultHdl);
		
		//echo(join("\n",$output));
		
		return array(
			'executionTime' => $time_end - $time_start,
			'return' => $result,
			'stdout' => $stdout,
			'stderr' => $stderr,
			'ok' => $return_var === 0
		);
	}
	
	
	static public function runFromFile(File $scriptR, $arguments = ''){
		
		if($scriptR->mime !== 'application/javascript')
			throw new Exception('not a valid script file');
		
		$script = $scriptR->read();
		$argv = array();
		
		if(is_string($arguments) && !empty($arguments)){
			\preg_match_all('/"(?:\\\\.|[^\\\\"])*"|\S+/', $arguments, $matches);
			$argv = $matches[0];
		}
		
		return self::run($scriptR->ething, $script, array(
			'script' => array(
				'id' => $scriptR->id(),
				'name' => $scriptR->name()
			),
			'argv' => $argv,
			'argc' => count($argv)
		));
		
	}

}


