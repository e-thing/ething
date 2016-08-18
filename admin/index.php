<?php require_once 'session.php'; ?>
<!DOCTYPE html>
<html lang="en">
  <head>
    <title>Admin</title>
	
	<meta charset="utf-8">
	<meta http-equiv="X-UA-Compatible" content="IE=edge">
	<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no">
		
	<!-- JQUERY -->
	<script src="//ajax.googleapis.com/ajax/libs/jquery/2.1.4/jquery.min.js"></script>
	
	<!-- BOOTSTRAP -->
	<link href='//maxcdn.bootstrapcdn.com/bootstrap/3.3.5/css/bootstrap.min.css' rel='stylesheet' type='text/css'/>
	<script src="//maxcdn.bootstrapcdn.com/bootstrap/3.3.5/js/bootstrap.min.js"></script>
	
	<link href="admin.css" rel="stylesheet">
	
	<style>
	.main {
	  text-align: center;
	}
	</style>
	
  </head>
<body>
	
	<?php include 'template/navbar.html'; ?>

    <div class="container">

      <div class="main">
        <h1>Administration Interface</h1>
        <p class="lead">Use this interface to do some administration task such as adding some new user ...</p>
      </div>
	  
	  <div>
        <h2>Status</h2>
		
		<?php
			
			function check_web_server(){
				
				return array(
					'test' => true,
					'message' => $_SERVER['SERVER_SOFTWARE']
				);
				
			}
			
			function check_php_version(){
				
				$phpVersion = phpversion();
				$phpVersionMin = '5.4.0';
				if(version_compare($phpVersion, $phpVersionMin, '<')){
					return array(
						'test' => false,
						'message' => $phpVersion.' < '.$phpVersionMin
					);
				}
				else
					return array(
						'test' => true,
						'message' => $phpVersion
					);
			}
			
			function check_mongo_plugin(){
				
				$mongoVersion = phpversion('mongo');
				$mongoVersionMin = '1.6.0';
				if(!extension_loaded('mongo') || $mongoVersion === false){
					return array(
						'test' => false,
						'message' => 'The mongo PHP extension is not installed'
					);
				}
				else if(version_compare($mongoVersion, $mongoVersionMin, '<')){
					return array(
						'test' => false,
						'message' => $mongoVersion.' < '.$mongoVersionMin
					);
				}
				else
					return array(
						'test' => true,
						'message' => $mongoVersion
					);
			}
			
			function check_curl_plugin(){
			
				if(!extension_loaded('curl')){
					return array(
						'test' => false,
						'message' => 'The curl PHP extension is not installed'
					);
				}
				
				$curlVersion = curl_version()['version'];
				$curlVersionMin = '7.0.0';
				if(version_compare($curlVersion, $curlVersionMin, '<')){
					return array(
						'test' => false,
						'message' => $curlVersion.' < '.$curlVersionMin
					);
				}
				else
					return array(
						'test' => true,
						'message' => $curlVersion
					);
			}
			
			function check_gd_plugin(){
				if(!(extension_loaded('gd') && function_exists('gd_info'))){
					return array(
						'test' => false,
						'message' => 'The GD PHP library is not installed'
					);
				}
				$info = gd_info();
				$gdVersion = isset($info['GD Version']) ? $info['GD Version'] : 'unknown';
				return array(
					'test' => true,
					'message' => $gdVersion
				);
			}
			
			function check_database(){
				try {
					$ething = ething_instanciate();
					
					$mongodb_info = $ething->db()->command(array('buildinfo'=>true));
					$mongodb_version = $mongodb_info['version'];
					
					return array(
						'test' => true,
						'message' => 'connected ; database '.$ething->config('server.database').' ; EThing version:'.\Ething\Ething::VERSION.' ; MongoDB version:'.$mongodb_version
					);
				} catch(\Exception $e) {
					return array(
						'test' => false,
						'message' => 'unable to connect to the database ['.$e->getMessage().']'
					);
				}
			}
			
			function check_http_request(){
				global $config;
				
				//open connection
				$ch = curl_init('http://example.com/');
				curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
				
				// proxy
				if(isset($config['proxy'])){
					$proxySettings = $config['proxy'];
					if(is_array($proxySettings) && !empty($proxySettings) && !empty($proxySettings['host'])){
						$proxyAddress = $proxySettings['host'];
						if(!empty($proxySettings['port']))
							$proxyAddress .= ':'.$proxySettings['port'];
						curl_setopt($ch, CURLOPT_PROXY, $proxyAddress); // The HTTP proxy to tunnel requests through
						// proxy authentication
						if(!empty($proxySettings['user']) && !empty($proxySettings['password']))
							curl_setopt($ch, CURLOPT_PROXYUSERPWD, $proxySettings['user'].':'.$proxySettings['password']); // A username and password formatted as "[username]:[password]" to use for the connection to the proxy.
					}
				}
				
				//execute post
				$result = curl_exec($ch);
					
				//close connection
				curl_close($ch);
				
				if(!$result)
					return array(
						'test' => false,
						'message' => 'unable to make a http request (check your proxy settings)'
					);
		
				return array(
					'test' => true
				);
			}
			
			function check_mongodb_cli(){
				
				$command = "mongo --version";
				
				$results = shell_exec($command);
				
				if(empty($results))
					return array(
						'test' => false,
						'message' => 'unable to execute MongoDB command line'
					);
				else
					return array(
						'test' => true,
						'message' => $results
					);
				
			}
			
			function check_deamon_running(){
				
				$pid = false;
				
				if (strtoupper(substr(PHP_OS, 0, 3)) === 'WIN') {
					// windows 
					exec('echo | wmic PROCESS where "caption=\'php.exe\' and commandline like \'%ethingd.php%\'" get Processid', $processList, $res);
					
					if($res===0){
						foreach($processList as $processLine){
							if(ctype_digit($processLine)){
								if($pid!==false){
									return array(
										'test' => false,
										'message' => 'multiple daemon processes are running !'
									);
								}
								$pid=intval($processLine);
							}
						}
					}
				}
				else {
					// unix like
					exec('ps -o pid,cmd -e', $processList, $res);
					
					if($res===0){
						foreach(preg_grep('/ethingd.php/i',$processList) as $processLine){
							
							if(preg_match('/^(\s*\d+ )/',$processLine,$matches)){
								if($pid!==false){
									return array(
										'test' => false,
										'message' => 'multiple daemon processes are running !'
									);
								}
								$pid=intval(trim($matches[1]));
							}
						}
					}
					
				}
				
				if($pid===false)
					return array(
						'test' => false,
						'message' => "the daemon process 'ethingd.php' is not running"
					);
				else
					return array(
						'test' => true,
						'message' => "daemon process 'ethingd.php' running. PID={$pid}"
					);
			}

			
			
			$tests = array(
				
				array(
					'name' => 'WEB Server',
					'fct' => 'check_web_server'
				),
				array(
					'name' => 'PHP version',
					'fct' => 'check_php_version'
				),
				array(
					'name' => 'mongo PHP plugin',
					'fct' => 'check_mongo_plugin'
				),
				array(
					'name' => 'curl PHP plugin',
					'fct' => 'check_curl_plugin'
				),
				array(
					'name' => 'GD PHP library',
					'fct' => 'check_gd_plugin'
				),
				array(
					'name' => 'database',
					'fct' => 'check_database'
				),
				array(
					'name' => 'HTTP request',
					'fct' => 'check_http_request'
				),
				array(
					'name' => 'MongoDB CLI',
					'fct' => 'check_mongodb_cli'
				),
				array(
					'name' => 'daemon process',
					'fct' => 'check_deamon_running'
				)
				
			);
	
		?>
		<p>
			<table class="table table-striped" id="user-list">
				<thead>
					<tr>
						<th>Test</th>
						<th>Status</th>
						<th>Message</th>
					</tr>
				</thead>
				<tbody>
				<?php
					
					foreach($tests as $test){
						
						if(is_callable($test['fct'])){
						
							echo "<tr>";
							
							echo "<td>".$test['name']."</td>";
							
							try {
								$result = array_merge(array(
									'test' => false,
									'message' => ''
								),$test['fct']());
								
							}
							catch(\Exception $e){
								$result = array(
									'test' => false,
									'message' => $e->getMessage()
								);
							}
							
							echo "<td>";
							if($result['test'])
								echo '<span style="color:green;">success</span>';
							else
								echo '<span style="color:red;">FAIL</span>';
							echo "</td>";
							
							echo "<td>".$result['message']."</td>";
							
							
							echo "</tr>";
						}
					}
					
				?>
				</tbody>
			</table>
		</p>
      </div>

    </div>
	
</body>
</html>