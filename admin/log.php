<?php
	require 'session.php';
?>
<!DOCTYPE html>
<html lang="en">
  <head>
    <title>Admin - Log</title>
	
	<meta charset="utf-8">
	<meta http-equiv="X-UA-Compatible" content="IE=edge">
	<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no">
	
	<!-- JQUERY -->
	<script src="//ajax.googleapis.com/ajax/libs/jquery/2.1.4/jquery.min.js"></script>
	
	<!-- BOOTSTRAP -->
	<link href='//maxcdn.bootstrapcdn.com/bootstrap/3.3.5/css/bootstrap.min.css' rel='stylesheet' type='text/css'/>
	<script src="//maxcdn.bootstrapcdn.com/bootstrap/3.3.5/js/bootstrap.min.js"></script>
	
	<link href="admin.css" rel="stylesheet">
	
  </head>
<body>
	
	<?php include 'template/navbar.html'; ?>

    <div class="container-fluid">
		<div class="main">
			
			<?php
				
				$logFile = isset($config['log']) && is_string($config['log']) ? $config['log'] : false;
				
				if(empty($logFile)){
					?>
					<div class="alert alert-warning" role="alert">
						No log file set in the configuration file.
					</div>
					<?php
				}
				else if(is_readable($logFile)){
					
					$logContent = file_get_contents($logFile);
					
					?>
					<h1>Log <small><?php echo $logFile; ?></small></h1>
					
					<pre><?php echo $logContent; ?></pre>
					<?php
				}
				else {
					?>
					<div class="alert alert-danger" role="alert">
						Unable to read the log file '<?php echo $logFile; ?>'.
					</div>
					<?php
				}
				
			?>
		</div>
    </div>
	
</body>
</html>