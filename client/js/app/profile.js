(function(){
	
	var selected_avatar = null;
	
	window.main = function() {
		
		/*$('#avatar-browse-btn').click(function(){
			$('#avatar').trigger('click');
		});
		
		$("#avatar").change(function (){
			var avatar = $(this)[0].files[0];
			if(avatar){
				selected_avatar = avatar;
				
				var reader = new FileReader();
				reader.onload = function (event) {
				  var image = new Image();
				  image.src = event.target.result;
				  //image.width = "128"; // a fake resize
				  //image.height = 128;
				  $('#avatar-preview').html($(image).css({
						'width':'100%',
						'max-width': '100px',
						'max-height': '100px'
					}));
				};
				
				reader.readAsDataURL(avatar);
			}
		});*/
		
		$('#form').form(new $.Form.FormLayout([{
			// just here to disable autofill on chrome
			item: '<input type="text" name="user_f5f7tyjh"/><input type="password" name="pass_f5f7tyjh"/>',
			hidden: true,
			skip: true
		},{
			name: 'name',
			label: 'Username',
			item: {
				input: 'text',
				value: EThing.auth.getUser().name(),
				attr:{
					disabled: true
				}
			}
		},{
			label: 'email',
			item: {
				input: 'email',
				get: function($e){
					var v = ($e.val() || '').trim();
					if(v.length==0)
						throw "The email must not be empty";
					return v;
				}
			}
		},{
			label: 'password',
			item: {
				input: 'password',
				get: function($e){
					var v = $e.val(),
						vConfirm = this.form().findItem('passwordConfirm').getValue();
					if(v.length==0 && vConfirm==0)
						return;
					if(vConfirm != v)
						throw "The 2 passwords are not identical";
					return $e.val();
				}
			}
		},{
			label: 'Confirm password',
			item: {
				name: 'passwordConfirm',
				get: null,
				input: 'password'
			},
			skip: true
		}]));
		
		
		$('#btn-validate').click(function() {
			
			$('#form').form('validate').done(function(props){
				
				if(props){
					if(!$.isEmptyObject(props)){
						EThing.auth.getUser().set(props,function(profile,status){
							if(status.error)
								$('#form').form().setError(status.error.message);
							else 
								// the patch was successfull
								window.location.replace('explore.html');
						});
					}
					else {
						window.location.replace('explore.html');
					}
				}
			
			});
			
		});
		
		
		EThing.auth.getUser().getProfile(function(userProfile){
			$('#form').form().setValue(userProfile);
		});
		
	};
	
})()