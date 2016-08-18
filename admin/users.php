<?php
	require_once __DIR__.'/session.php';
?>
<!DOCTYPE html>
<html lang="en">
  <head>
    <title>Admin - User</title>
	
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
			$connectError = false;
			
			try {
				$ething = ething_instanciate();
			}
			catch(Exception $e){
				$connectError = $e->getMessage();
			}
			
			if($connectError!==false){
				echo '<div class="alert alert-danger" role="alert">'.$connectError.'</div>';
			}
			else {
		  ?>
			<h1>User management</h1>
			<p>
				<button type="button" class="btn btn-default" data-toggle="modal" data-target="#modal-add-user">
					<span class="glyphicon glyphicon-plus" aria-hidden="true"></span>
					Add user
				</button>
				
				<!-- Modal -->
				<div class="modal fade" id="modal-add-user" tabindex="-1" role="dialog" aria-labelledby="modal-add-user-title">
				  <div class="modal-dialog" role="document">
					<div class="modal-content">
					  <div class="modal-header">
						<button type="button" class="close" data-dismiss="modal" aria-label="Close"><span aria-hidden="true">&times;</span></button>
						<h4 class="modal-title" id="modal-add-user-title">Add user</h4>
					  </div>
					  <div class="modal-body">
						<form autocomplete="off" id="modal-add-user-form">
							<!-- the 2 next hidden inputs are just here to turn autocomplete off on google chrome -->
							<input type="text" style="display:none" />
							<input type="password" style="display:none">
							
							<div class="form-group">
								<label for="modal-add-user-username">Username</label>
								<input type="text" class="form-control" name="user" placeholder="Username" id="modal-add-user-username" autocomplete="off">
							</div>
							<div class="form-group">
								<label for="modal-add-user-password">Password</label>
								<input type="password" class="form-control" name="password" placeholder="Password" id="modal-add-user-password" autocomplete="off">
							</div>
							<div class="form-group">
								<label for="modal-add-user-email">Email address</label>
								<input type="email" class="form-control" name="email" placeholder="E-mail" id="modal-add-user-email" autocomplete="off">
							</div>
							<div class="form-group">
								<label for="modal-add-user-quota">Quota</label>
								<p>
									The amount of space allowed for this user. 0 means unlimited.
								</p>
								<div class="input-group">
									<input type="number" class="form-control" name="quota" placeholder="Quota" id="modal-add-user-quota" autocomplete="off" value="100" min="0" step="100">
									<span class="input-group-addon">MB</span>
								</div>
							</div>
							<div class="alert alert-danger" role="alert" id="modal-add-user-error" style="display:none"></div>
						</form>
					  </div>
					  <div class="modal-footer">
						<button type="button" class="btn btn-default" data-dismiss="modal">Close</button>
						<button type="button" class="btn btn-primary" id="modal-add-user-submit">Add</button>
					  </div>
					</div>
				  </div>
				</div>
				<script>
					$(function(){
						$('#modal-add-user-submit').click(function() {
							// handle form processing here
							//$('form#modal-add-user-form').submit();
							// handle form processing here
							$('#modal-add-user-error').hide();
							$.ajax({
								type: "POST",
								url: "requests/adduser.php",
								data: $('form#modal-add-user-form').serialize()
							})
								.done(function(){
									// success: reload the page
									location.reload();
								})
								.fail(function(xhr){
									var ct = xhr.getResponseHeader("Content-Type"),
										data = /json/.test(ct) ? JSON.parse(xhr.responseText) : xhr.responseText;
									
									$('#modal-add-user-error').text(data.message ? data.message : 'internal error').show();
								})
							
						});
					});
				</script>
			</p>
			<p>
				<table class="table table-striped" id="user-list">
					<thead>
						<tr>
							<th>Name</th>
							<th>Email</th>
							<th>Created</th>
							<th>space</th>
							<th>Operations</th>
						</tr>
					</thead>
					<tbody></tbody>
				</table>
				<script>
					
					var users = <?php
						$users = $ething->findUsers();
						echo json_encode(array_map(function($user){
							return array_merge($user->profile(), array('stats' => $user->stats()));
						},$users),JSON_PRETTY_PRINT|JSON_UNESCAPED_SLASHES);
					?>;
					
					var canNotify = <?php echo empty($ething->config('mail')) ? 'false' : 'true'; ?>;
					
					var sizeToString = function(s) {
						s = parseInt(s);
						if(isNaN(s)) return '-';
						var coef = 0.9;
						if (s > 1000000000 * coef)
							s = (Math.floor((s / 1000000000) * 100) / 100) + 'GB';
						else if (s > 1000000 * coef)
							s = (Math.floor((s / 1000000) * 10) / 10) + 'MB';
						else if (s > 1000 * coef)
							s = Math.floor((s / 1000)) + 'KB';
						else
							s = s + 'B';
						return s;
					};
					
					$(function(){
						
						var $usersTableBody = $('tbody','#user-list');
						
						if(users.length===0){
							$usersTableBody.html('<tr><td colspan="5">no user</td></tr>');
						}
						else
							users.forEach(function(user){
								
								var $Operations = $('<div class="btn-group" role="group">');
								
								var $modify = $('<button type="button" class="btn btn-primary btn-xs" aria-label="notify"><span class="glyphicon glyphicon-cog" aria-hidden="true"></span></button>');
								var $delete = $('<button type="button" class="btn btn-danger btn-xs" aria-label="delete"><span class="glyphicon glyphicon-remove" aria-hidden="true"></span></button>');
								var $notify = $('<button type="button" class="btn btn-primary btn-xs" aria-label="notify"><span class="glyphicon glyphicon-envelope" aria-hidden="true"></span></button>');
								
								$modify.click(function(){
									$('#modal-modify-user-id').val(user.id);
									$('#modal-modify-user-username').val(user.name);
									$('#modal-modify-user-email').val(user.email);
									$('#modal-modify-user-quota').val(Math.round(user.quota / 1000000));
									$('#modal-modify-user').modal('show');
								});
								
								$delete.click(function(){
									if(confirm('Do you really want to delete the user "'+user.name+'" definetely and all his data ?')){
										$.ajax({
											type: "POST",
											url: "requests/removeuser.php",
											data: {
												id: user.id
											}
										})
											.done(function(){
												// success: reload the page
												location.reload();
											})
											.fail(function(xhr){
												var ct = xhr.getResponseHeader("Content-Type"),
													data = /json/.test(ct) ? JSON.parse(xhr.responseText) : xhr.responseText;
												
												alert(data.message ? data.message : 'internal error');
											})
									}
								});
								
								$notify.click(function(){
									$('#modal-notify-user-id').val(user.id);
									$('#modal-notify-user').modal('show');
								});
								
								$Operations.append(canNotify ? $notify : null, $modify, $delete);
								
								var hasQuota = !!user.stats.quota_size;
								
								var cells = [
									user.name,
									user.email,
									new Date(user.createdDate).toLocaleString(),
									sizeToString(user.stats.used)+(hasQuota ? ('/'+sizeToString(user.stats.quota_size)+' ('+Math.round(100*user.stats.used/user.stats.quota_size)+'%)') : ' used'),
									$Operations
								];
								
								cells.reduce(function($tr,cell){
									return $tr.append($('<td>').html(cell));
								},$('<tr>')).appendTo($usersTableBody);
								
							});
						
					});
					
				</script>
				<div class="modal fade" id="modal-notify-user" tabindex="-1" role="dialog" aria-labelledby="modal-notify-user-title">
				  <div class="modal-dialog" role="document">
					<div class="modal-content">
					  <div class="modal-header">
						<button type="button" class="close" data-dismiss="modal" aria-label="Close"><span aria-hidden="true">&times;</span></button>
						<h4 class="modal-title" id="modal-notify-user-title">Notify user</h4>
					  </div>
					  <div class="modal-body">
						<form autocomplete="off" id="modal-notify-user-form">
							<input type="hidden" name="id" value="null" id="modal-notify-user-id">
							<div class="form-group">
								<label for="modal-notify-user-subject">Subject</label>
								<input type="text" class="form-control" name="subject" placeholder="Subject" id="modal-notify-user-subject" autocomplete="off">
							</div>
							<div class="form-group">
								<label for="modal-notify-user-message">Message</label>
								<textarea class="form-control" rows="15" name="message" id="modal-notify-user-message"></textarea>
							</div>
							<div class="alert alert-danger" role="alert" id="modal-notify-user-error" style="display:none"></div>
						</form>
					  </div>
					  <div class="modal-footer">
						<button type="button" class="btn btn-default" data-dismiss="modal">Close</button>
						<button type="button" class="btn btn-primary" id="modal-notify-user-submit">Notify</button>
					  </div>
					</div>
				  </div>
				</div>
				<script>
					$(function(){
						$('#modal-notify-user-submit').click(function() {
							// handle form processing here
							//$('form#modal-notify-user-form').submit();
							// handle form processing here
							$('#modal-notify-user-error').hide();
							$.ajax({
								type: "POST",
								url: "requests/notifyuser.php",
								data: $('form#modal-notify-user-form').serialize()
							})
								.done(function(){
									// close the modal dialog
									$('#modal-notify-user').modal('hide');
								})
								.fail(function(xhr){
									var ct = xhr.getResponseHeader("Content-Type"),
										data = /json/.test(ct) ? JSON.parse(xhr.responseText) : xhr.responseText;
									
									$('#modal-notify-user-error').text(data.message ? data.message : 'internal error').show();
								})
							
						});
					});
				</script>
				<div class="modal fade" id="modal-modify-user" tabindex="-1" role="dialog" aria-labelledby="modal-modify-user-title">
				  <div class="modal-dialog" role="document">
					<div class="modal-content">
					  <div class="modal-header">
						<button type="button" class="close" data-dismiss="modal" aria-label="Close"><span aria-hidden="true">&times;</span></button>
						<h4 class="modal-title" id="modal-modify-user-title">Modify user</h4>
					  </div>
					  <div class="modal-body">
						<form autocomplete="off" id="modal-modify-user-form">
							<input type="hidden" name="id" value="null" id="modal-modify-user-id">
							<!-- the 2 next hidden inputs are just here to turn autocomplete off on google chrome -->
							<input type="text" style="display:none" />
							<input type="password" style="display:none">
							
							<div class="form-group">
								<label for="modal-modify-user-username">Username</label>
								<input type="text" class="form-control" placeholder="Username" id="modal-modify-user-username" autocomplete="off" readonly="readonly">
							</div>
							<div class="form-group">
								<label for="modal-modify-user-password">Password</label>
								<input type="password" class="form-control" name="password" placeholder="Password" id="modal-modify-user-password" autocomplete="off">
							</div>
							<div class="form-group">
								<label for="modal-modify-user-email">Email address</label>
								<input type="email" class="form-control" name="email" placeholder="E-mail" id="modal-modify-user-email" autocomplete="off">
							</div>
							<div class="form-group">
								<label for="modal-modify-user-quota">Quota</label>
								<div class="input-group">
									<input type="number" class="form-control" name="quota" placeholder="Quota" id="modal-modify-user-quota" autocomplete="off" value="100" min="0" step="100">
									<span class="input-group-addon">MB</span>
								</div>
							</div>
							<div class="alert alert-danger" role="alert" id="modal-modify-user-error" style="display:none"></div>
						</form>
					  </div>
					  <div class="modal-footer">
						<button type="button" class="btn btn-default" data-dismiss="modal">Close</button>
						<button type="button" class="btn btn-primary" id="modal-modify-user-submit">Modify</button>
					  </div>
					</div>
				  </div>
				</div>
				<script>
					$(function(){
						$('#modal-modify-user-submit').click(function() {
							// handle form processing here
							$('#modal-modify-user-error').hide();
							$.ajax({
								type: "POST",
								url: "requests/modifyuser.php",
								data: $('form#modal-modify-user-form').serialize()
							})
								.done(function(){
									// close the modal dialog
									$('#modal-modify-user').modal('hide');
									location.reload();
								})
								.fail(function(xhr){
									var ct = xhr.getResponseHeader("Content-Type"),
										data = /json/.test(ct) ? JSON.parse(xhr.responseText) : xhr.responseText;
									
									$('#modal-modify-user-error').text(data.message ? data.message : 'internal error').show();
								})
							
						});
					});
				</script>
			</p>
		  <?php
			}
		  ?>
		</div>
    </div>
	
</body>
</html>