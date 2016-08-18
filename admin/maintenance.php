<?php
	require 'session.php';
?>
<!DOCTYPE html>
<html lang="en">
  <head>
    <title>Admin - Maintenance</title>
	
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

    <div class="container">
		<div class="main">
			<?php
				
				$cliEnable = !!shell_exec("mongo --version");
				
				if($cliEnable){
				
			?>
			<h1>Backup</h1>
			<p>
				<form id="backup-form" action="requests/backup.php">
					<button type="button" class="btn btn-default" id="backup-btn">
						<span class="glyphicon glyphicon-cloud-download" aria-hidden="true"></span>
						Back up
					</button>
				</form>
				
				<script>
					$(function(){
						$('#backup-btn').click(function() {
							
							$('#backup-form').submit();
							
						});
					});
				</script>
			</p>
			<h1>Restore</h1>
			<p>
				<form class="form-inline" id="restore-form" action="requests/restore.php" enctype="multipart/form-data" method="post">
					<div class="form-group">
						<input type="file" class="form-control" name="file">
					</div>
					<button type="button" class="btn btn-default" id="restore-btn">
						<span class="glyphicon glyphicon-cloud-upload" aria-hidden="true"></span>
						Restore
					</button>
				</form>
				
				<script>
					$(function(){
						$('#restore-btn').click(function() {
							if(confirm('Are you sure to restore the database? All your data will be replaced !')){
								$('#restore-form').submit();
							}
						});
					});
				</script>
			</p>
			<h1>Reset</h1>
			<p>
				<form id="reset-form" action="requests/reset.php">
					<button type="button" class="btn btn-default" id="reset-btn">
						<span class="glyphicon glyphicon-cloud-download" aria-hidden="true"></span>
						Reset
					</button>
				</form>
				
				<script>
					$(function(){
						$('#reset-btn').click(function() {
							
							if(confirm('Are you sure to reset the database? All your data will be lost !')){
								$('#reset-form').submit();
							}
							
						});
					});
				</script>
			</p>
			<?php
				}
				else {
			?>
			<div class="alert alert-danger" role="alert">
				The MongoDB command line interface could not be found !
			</div>
			<?php
				}
			?>
		</div>
    </div>
	
</body>
</html>