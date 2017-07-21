<!DOCTYPE html>
<html lang="en">
  <head>
	<meta charset="utf-8">
	<meta http-equiv="X-UA-Compatible" content="IE=edge">
	<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no">
	
	<title>eThing | Login</title>
	
	
	<!-- BOOTSTRAP -->
	<link href='//maxcdn.bootstrapcdn.com/bootstrap/3.3.5/css/bootstrap.min.css' rel='stylesheet' type='text/css'/>
	
	
	<style>
		body {
		  padding-top: 40px;
		  padding-bottom: 40px;
		  background-color: #F7F7F7;
		}

		.wrapper {
		  max-width: 330px;
		  padding: 15px;
		  margin: 0 auto;
		}
		.form-signin h1 {
			text-align: center;
			text-shadow: 1px 1px 4px rgba(150, 150, 150, 1);
			margin-bottom: 30px;
		}
		.form-signin .checkbox {
		  margin-bottom: 10px;
		}
		.form-signin .checkbox {
		  font-weight: normal;
		}
		.form-signin .form-control {
		  position: relative;
		  height: auto;
		  -webkit-box-sizing: border-box;
			 -moz-box-sizing: border-box;
				  box-sizing: border-box;
		  padding: 10px;
		  font-size: 16px;
		}
		.form-signin .form-control:focus {
		  z-index: 2;
		}


		a.nolinkstyle {
			color:#000000 !important;
			text-decoration:none;
		}

		.extra {
			margin-top: 10px;
		}
	</style>
	
	
	
  </head>

  <body role="document">

    <div class="container">

	  <div class="wrapper">
		  <div class="form-signin" id="signin-form">
			<h1>e-Thing</h1>
			
			<div class="form-group">
				<label for="password" class="sr-only">Password</label>
				<input type="password" id="password" name="password" class="form-control" placeholder="Password" required autofocus>
			</div>
			
			<div class="alert alert-danger" role="alert" id="access-err" style="display: none;">Invalid acces</div>
			
			<button id="signin-btn" class="btn btn-lg btn-primary btn-block" type="submit">Login</button>
			
		  </div>
	  </div>

    </div>
	
	<script>
		
		var passwordElm = document.getElementById('password'),
			submitBtn = document.getElementById('signin-btn'),
			errorElm = document.getElementById('access-err'),
			redirect_uri = "<?php echo $redirect_uri; ?>";
		
		passwordElm.onkeyup = function(e){
			if(e.keyCode == 13){
				submitBtn.onclick.call(submitBtn);
			}
		}
		
		submitBtn.onclick = function(){
			
			errorElm.style.display = 'none';
			
			var xhr = new XMLHttpRequest();
			
			xhr.open("POST", 'password', true);
			xhr.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
			
			xhr.onreadystatechange = function() {
				if (this.readyState == 4){
					
					var data = this.responseText;
					
					if(/json/.test(this.getResponseHeader("Content-Type") || '')){
						data = JSON.parse(data);
					}
					
					if(this.status >= 200 && this.status < 400) {
						
						// redirect
						window.location.replace(redirect_uri);
						
					}
					else {
						
						errorElm.style.display = 'block';
						
					}
				}
			};
			
			xhr.send('password='+encodeURIComponent(passwordElm.value)+'&redirect_uri='+encodeURIComponent(redirect_uri));
			
		}
	</script>

  </body>
</html>
