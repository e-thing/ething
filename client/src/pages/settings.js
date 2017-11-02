(function (root, factory) {
    if (typeof define === 'function' && define.amd) {
        // AMD. Register as an anonymous module.
        define(['ui/core', 'text!./settings.html', 'jquery', 'ething', 'form', 'css!./settings'], factory);
    }
}(this, function (UI, template, $, EThing) {
	
	
	var tmId = null;
	var $mailCheck = $('<div>Test mail settings <button class="btn btn-primary btn-xs" type="submit">Test</button><div class="alert alert-info" role="alert" style="display: none;">Sent</div><div class="alert alert-danger" role="alert" style="display: none;"></div></div>');
	$mailCheck.find('button').click(function(){
		if(tmId!==null) {
			clearTimeout(tmId);
			tmId = null;
		}
		$mailCheck.find('.alert').hide();
		EThing.notify('eThing mail test', 'it works !')
			.done(function(){
				$mailCheck.find('.alert-info').show();
				$mailCheck.find('.alert-danger').hide();
				tmId = setTimeout(function(){
					$mailCheck.find('.alert-info').hide();
				}, 5000);
			})
			.fail(function(err){
				$mailCheck.find('.alert-info').hide();
				$mailCheck.find('.alert-danger').text(err.message || 'error').show();
			});
	});
	
	var preferencesForm = new $.Form.FormLayout({
		items: [{
			name: 'db',
			label: 'database',
			description: 'Configure your MongoDB database.',
			item: new $.Form.FormLayout({
				items: [{
					name: 'host',
					label: false,
					item: new $.Form.Text({
						prefix: 'host',
						validators:[$.Form.validator.NotEmpty],
						placeholder: 'server'
					})
				},{
					name: 'port',
					label: false,
					item: new $.Form.Number({
						prefix: 'port',
						minimum: 1,
						maximum: 65535,
						value: 587,
						validators:[$.Form.validator.NotEmpty, $.Form.validator.Integer],
						placeholder: 'port'
					})
				},{
					name: 'user',
					label: false,
					item: new $.Form.Text({
						prefix: 'user',
						placeholder: 'user'
					})
				},{
					name: 'password',
					label: false,
					item: new $.Form.Text({
						prefix: 'password',
						password: true,
						placeholder: 'password'
					})
				},{
					name: 'database',
					label: false,
					item: new $.Form.Text({
						prefix: 'database',
						validators:[$.Form.validator.NotEmpty],
						placeholder: 'database'
					})
				}],
				format: {
					'out': function(value){
						if(!value.password) delete value.password;
						if(!value.user) delete value.user;
						return value;
					}
				}
			})
		},{
			
			name: 'notification',
			item: new $.Form.FormLayout({
				items: [{
					name: 'emails',
					description: 'List the email addresses to which notifications will be sent.',
					item: new $.Form.ArrayLayout({
						editable: true,
						instanciator: function(){
							return new $.Form.Text({
								placeholder: 'foo@example.com',
								validators: [
									$.Form.validator.NotEmpty,
									$.Form.validator.Email
								]
							});
						}
					})
				},{
					name: 'smtp',
					description: 'Configure a SMTP server if you want the e-Thing application to send mails.',
					item: new $.Form.FormLayout({
						items: [{
							name: 'host',
							label: false,
							item: new $.Form.Text({
								prefix: 'host',
								validators:[$.Form.validator.NotEmpty],
								placeholder: 'smtp.gmail.com'
							})
						},{
							name: 'port',
							label: false,
							item: new $.Form.Number({
								prefix: 'port',
								minimum: 1,
								maximum: 65535,
								value: 587,
								validators:[$.Form.validator.NotEmpty, $.Form.validator.Integer],
								placeholder: 'port'
							})
						},{
							name: 'user',
							label: false,
							item: new $.Form.Text({
								prefix: 'user',
								placeholder: 'username@gmail.com',
								validators:[$.Form.validator.NotEmpty]
							})
						},{
							name: 'password',
							label: false,
							item: new $.Form.Text({
								prefix: 'password',
								password: true,
								placeholder: 'password'
							})
						}],
						format: {
							'out': function(value){
								if(!value.password) delete value.password;
								if(!value.user) delete value.user;
								return value;
							}
						}
					})
				},{
					label: false,
					name: 'check',
					item: new $.Form.Label($mailCheck)
				}]
			}),
			checkable: true
		},{
			name: 'auth',
			label: 'authentication',
			item: new $.Form.FormLayout({
				items: [{
					name: 'password',
					description: 'Change your password. The minimum length is 4 characters.',
					item: new $.Form.Text({
						validators:[],
						password: true,
						placeholder: 'change your password'
					})
				}, {
					name: 'localonly',
					description: 'If enabled, the e-Thing application will only be accessible from your local network.',
					item: new $.Form.Checkbox({
						label: 'enable'
					})
				}],
				format: {
					'out': function(value){
						if(!value.password) delete value.password;
						return value;
					}
				}
			})
		},{
			name: 'proxy',
			description: 'Configure a proxy server if your e-Thing server does not have a direct connection to Internet.',
			item: new $.Form.FormLayout({
				items: [{
					name: 'host',
					label: false,
					item: new $.Form.Text({
						prefix: 'address',
						validators:[$.Form.validator.NotEmpty],
						placeholder: 'hostname'
					})
				},{
					name: 'port',
					label: false,
					item: new $.Form.Number({
						prefix: 'port',
						minimum: 1,
						maximum: 65535,
						value: 80,
						validators:[$.Form.validator.NotEmpty, $.Form.validator.Integer],
						placeholder: 'port'
					})
				},{
					name: 'user',
					label: false,
					item: new $.Form.Text({
						prefix: 'user',
						placeholder: 'user'
					})
				},{
					name: 'password',
					label: false,
					item: new $.Form.Text({
						prefix: 'password',
						password: true,
						placeholder: 'password'
					})
				}],
				format: {
					'out': function(value){
						if(!value.password) delete value.password;
						if(!value.user) delete value.user;
						return value;
					}
				}
			}),
			checkable: true
		},{
			name: 'debug',
			description: 'Enable debugging mode.',
			item: new $.Form.Checkbox({
				label: 'enable'
			})
		},{
			name: 'mqtt',
			label: 'MQTT',
			checkable: true,
			description: 'Configure a MQTT broker if you want the e-Thing application to publish MQTT message.',
			item: new $.Form.FormLayout({
				items: [{
					name: 'host',
					label: false,
					item: new $.Form.Text({
						prefix: 'host',
						validators:[$.Form.validator.NotEmpty],
						placeholder: 'localhost'
					})
				},{
					name: 'port',
					label: false,
					item: new $.Form.Number({
						prefix: 'port',
						minimum: 1,
						maximum: 65535,
						value: 1883,
						validators:[$.Form.validator.NotEmpty, $.Form.validator.Integer],
						placeholder: 'port'
					})
				},{
					name: 'user',
					label: false,
					item: new $.Form.Text({
						prefix: 'user',
						placeholder: 'username'
					})
				},{
					name: 'password',
					label: false,
					item: new $.Form.Text({
						prefix: 'password',
						password: true,
						placeholder: 'password'
					})
				},{
					name: 'clientId',
					label: false,
					item: new $.Form.Text({
						prefix: 'clientId',
						validators:[$.Form.validator.NotEmpty]
					})
				},{
					name: 'rootTopic',
					label: false,
					item: new $.Form.Text({
						prefix: 'rootTopic',
						placeholder: 'ething/'
					})
				}],
				format: {
					'out': function(value){
						if(!value.password) delete value.password;
						if(!value.user) delete value.user;
						return value;
					}
				}
			})
		},{
			name: 'log',
			description: 'Enable log for debugging purpose.',
			checkable: true,
			item: new $.Form.FormLayout({
				items:[{
					name: 'file',
					label: 'storage',
					item: new $.Form.Select({
						items: {
							'file' : true,
							'database' : false
						},
						format:{
							'in': function(v){
								return !!v;
							}
						},
						value: false
					})
				},{
					name: 'level',
					item: new $.Form.Select({
						items: {
							'TRACE' : 0,
							'DEBUG' : 1,
							'INFO' : 2,
							'WARN' : 3,
							'ERROR' : 4,
							'FATAL' : 5
						},
						value: 2
					})
				}]
			})
		},{
			name: 'script',
			description: 'Scripts are executed server side.',
			item: new $.Form.FormLayout({
				items:[{
					name: 'timeout',
					description : 'Timeout in milliseconds. 0 means no timeout.',
					item: new $.Form.Number({
						minimum: 0,
						step: 1000
					})
				}]
			})
		}]
	});
	
	return function(data){
		
		UI.disableRefresh();
		
		var $template = UI.Container.set(template);
		
			
		var $loading = $('<span>').text('loading...').prependTo('#settings-tab');
		
		$('#settings-tab button.daemon-restart').click(function() {
			$.get('../tools/daemonRestart.php');
		}).hide();
		
		EThing.settings.get().done(function(settings){
			
			$loading.remove();
			
			var $preferencesForm = $('#settings-tab .form').form(preferencesForm, settings, function(){
				setTimeout(function(){
					$preferencesForm.trigger('changed.form');
				},10);
			});
		
			$preferencesForm.on('changed.form', function(){
				$validBtn.prop('disabled', $preferencesForm.form('hasError'));
			});
			
			var $validBtn = $('#settings-tab button.validate').click(function() {
				
				$preferencesForm.form('submit', function(props){
					
					EThing.settings.set(props).done(function(){
						// success
						$('#settings-tab > .alert-success').text('Settings updated successfully').show();
						$('#settings-tab > .alert-danger').hide();
					}).fail(function(err){
						$('#settings-tab > .alert-danger').text(err.message).show();
						$('#settings-tab > .alert-success').hide();
						$preferencesForm.one('changed.form', function(){
							$('#settings-tab > .error').hide();
						});
					}).always(function(){
						$('#settings-tab button.daemon-restart').show();
					});
					
				});
				
			});
			
			
		});
		
		
		require(['bootstrap-select'], function(){
			$('#log-filter').selectpicker({
				countSelectedText: function(){
					return 'no filter';
				}
			});
		});
		
		$('#log-filter').change(function(){
			var selectedLevels = $(this).val();
			$('#log tbody tr').each(function(){
				var $tr = $(this);
				$tr.toggle(selectedLevels.indexOf($tr.children('.level').text())!==-1);
			});
		});
		
		var searchTimeoutId = null;
		$('#log-search').keyup(function(){
			var searchValue = $(this).val().toLowerCase();
			if(searchTimeoutId!==null)
				clearTimeout(searchTimeoutId);
			searchTimeoutId = setTimeout(function(){
				console.log('search '+searchValue);
				$('#log tbody tr').each(function(){
					var $tr = $(this);
					$tr.toggle(searchValue ? $tr.children('.message').text().toLowerCase().indexOf(searchValue)!==-1 : true);
				});
			}, 200);
		});
		
		
		$('#log-reload').click(loadLog);
		
		
		$('#log-length li>a').click(function(evt){
			evt.preventDefault();
			$('#log-length .value').text($(this).text());
		}).first().click();
		
		
		
		function loadLog(){
			// load the log
			
			var length = $('#log-length .value').text();
			if(length != 'all') length = 'line=' + length + '&';
			else length = '';
			
			
			var $loading = $('<tr>').html('<td>loading...</td>').prependTo($('#log tbody').empty());
			
			$.get('../tools/readLog.php?'+length+'ts='+Math.floor(Date.now() / 1000), function(data){
				
				var $body = $('#log tbody').empty();
				
				data.split("\n").forEach(function(line){
					var d = line.split(' ');
					if(d.length>=6){
						var date = d[0]+' '+d[1],
							name = d[2],
							level = d[3],
							message = d.slice(5).join(' '),
							cl;
						
						switch(level){
							case 'ERROR':
							case 'FATAL':
								cl = 'danger';
								break;
							case 'WARN':
								cl = 'warning';
								break;
							default:
								cl = '';
								break;
						}
						
						$('<tr class="'+cl+'"><td class="date">'+date+'</td><td class="level">'+level+'</td><td class="origin">'+name+'</td><td class="message">'+message+'</td></tr>').appendTo($body);
					}
					
				});
				
				
			}, 'text').fail(function(){
				$loading.remove();
				$('<tr>').html('<td>no log available</td>').prependTo('#log tbody');
			});
		}
		
		
		function loadStatus(){
			var $loading = $('<tr>').html('<td>loading...</td>').prependTo('#status tbody');
			
			$.getJSON('../tools/check.php', function(data){
				
				$loading.remove();
				
				var $body = $('#status tbody');
				
				data.forEach(function(item){
					var $l = $('<tr><td class="name">'+item.name+'</td><td class="message '+(item.ok ? 'success' : 'danger')+'">'+item.message+'</td></tr>').appendTo($body);
					if(/daemon/i.test(item.name) && item.ok){
						$l.find('.message').append(' ',$('<button class="btn btn-link"><span class="glyphicon glyphicon-refresh" aria-hidden="true"></span> restart</button>').click(function(){
							$.get('../tools/daemonRestart.php', function(){
								location.reload();
							});
						}))
					}
				});
				
			});
		}
		
		$('.nav-tabs > li > a[href="#settings-tab"]').click(function(){
			
			UI.setUrl('settings');
			
		});
		
		$('.nav-tabs > li > a[href="#log"]').click(function(){
			
			if($('#log tbody').is(':empty')){
				loadLog();
			}
			
			UI.setUrl('settings',{
				page:'log'
			});
			
		});
		
		
		$('.nav-tabs > li > a[href="#status"]').click(function(){
			
			if($('#status tbody').is(':empty')){
				loadStatus();
			}
			
			UI.setUrl('settings',{
				page:'status'
			});
			
		});
		
		
		if(data.page === 'log'){
			$('.nav-tabs > li > a[href="#log"]').click();
		}
		else if(data.page === 'status'){
			$('.nav-tabs > li > a[href="#status"]').click();
		}
		
	};
}));