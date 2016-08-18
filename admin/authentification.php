<?php
	
	$config = array_replace_recursive(include(__DIR__.'/../config.php'),array(
		'admin'=> array(
			'user' => 'admin',
			'password' => 'admin',
			'onlyLocal' => false // if set to true, only local ip are allowed to connect to the admin interface
		)
	));
	
	
	if($config['admin']['onlyLocal']){
		if(!preg_match('/^(192\.168\.)|(127\.)/',$_SERVER['REMOTE_ADDR'])){
			die('only local address IP can access to this page');
		}
	}
	
	$errorMessage = '';
	
	if(!empty($_POST) && !empty($_POST['user']) && !empty($_POST['password'])){
		
		if($_POST['user'] === $config['admin']['user'] && $_POST['password'] === $config['admin']['password']) {
			// start a new session
			session_name('ADMIN_SESSION');
			session_set_cookie_params(3600,dirname($_SERVER['REQUEST_URI']),$_SERVER['HTTP_HOST']);
			session_start();
			$_SESSION['authenticated'] = true;
			// redirect to the main page admin.php
			header('Location: index.php');
			exit();
		}
		
		$errorMessage = 'Invalid Access';
	}
	
	
?>
<!DOCTYPE html>
<html lang="en">
  <head>
    <title>Sign in</title>
	
	<meta charset="utf-8">
	<meta http-equiv="X-UA-Compatible" content="IE=edge">
	<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no">
	
	<!-- BOOTSTRAP -->
	<link href='//maxcdn.bootstrapcdn.com/bootstrap/3.3.5/css/bootstrap.min.css' rel='stylesheet' type='text/css'/>
	
	<style>
		
		body {
			background-color: #F7F7F7;
		}
		
		.loginmodal-container {
		  padding: 15px;
		  max-width: 330px;
		  width: 100% !important;
		  margin: 0 auto;
		  overflow: hidden;
		}

		.loginmodal-container .title {
		  text-align: center;
		  text-shadow: 1px 1px 4px rgba(150, 150, 150, 1);
		}
		
		.loginmodal-container .subtitle {
		  text-align: center;
		  color: #929292;
		}
		
		.loginmodal-container .subtitle .glyphicon {
		  font-size: 64px;
		}

		.loginmodal-container form .form-control {
			height: auto;
			padding: 10px;
			font-size: 16px;
		}
		
		.loginmodal-container .extra {
			margin-top: 10px;
		}
		
	</style>
	
  </head>
  <body>
	<div class="loginmodal-container">
		<h1 class="title">e-Thing</h1>
		<h3 class="subtitle" >
			<div><span class="glyphicon glyphicon-cog" aria-hidden="true"></span></div>
			Administration
		</h3>
		
		<form action="<?php echo htmlspecialchars($_SERVER['PHP_SELF']); ?>" method="post">
			<div class="form-group">
				<label for="login" class="sr-only">Login</label>
				<input class="form-control" id="login" type="text" name="user" placeholder="Username" required autofocus>
			</div>
			<div class="form-group">
				<label for="password" class="sr-only">Password</label>
				<input class="form-control" id="password" type="password" name="password" placeholder="Password" required>
			</div>
			<?php
			  if(!empty($errorMessage)) 
			  {
				echo '<p class="alert alert-danger" role="alert">', htmlspecialchars($errorMessage) ,'</p>';
			  }
			?>
			<input class="btn btn-lg btn-primary btn-block" type="submit">
		</form>
		<div class="extra">
			<a href="../client">Client interface</a>
		</div>
	</div>
  </body>
</html>