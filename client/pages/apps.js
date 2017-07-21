(function (root, factory) {
    if (typeof define === 'function' && define.amd) {
        // AMD. Register as an anonymous module.
        define(['js/ui', 'text!./apps.html', 'jquery', 'ething', 'ui/infopanel', 'browser','css!./apps','jquery-mobile-events', 'form', 'ui/modal'], factory);
    }
}(this, function (UI, template, $, EThing, Infopanel) {
	
	
	
	// custom view
	
	function WallViewWithInfo(opt){
		$.Browser.Views.Wall.call(this, opt);
	}
	WallViewWithInfo.prototype = Object.create($.Browser.Views.Wall.prototype);
	
	WallViewWithInfo.prototype.createItem = function(resource){
		var $item = $.Browser.Views.Wall.prototype.createItem.apply(this,Array.prototype.slice.call(arguments));
		
		var self = this;
		
		// info
		var $info = $('<div>').html('<span class="glyphicon glyphicon-option-vertical" aria-hidden="true"></span>').addClass('col-info').click(function(e){
			self.table().select(resource);
			e.stopPropagation();
			Infopanel.show();
			return false;
		});
		
		$item.append(
			$info
		);
		
		// icon
		var imageUrl = resource.iconLink(),
			$icon = $item.find('.col-icon');
		if(imageUrl){
			EThing.request({
				url: imageUrl,
				dataType: 'blob'
			}).done(function(blob){
				// build an image from the blob data
				var urlCreator = window.URL || window.webkitURL;
				var imageUrl = urlCreator.createObjectURL( blob );
				
				var image = new Image();
				image.src = imageUrl;
				$icon.empty().append(image);
			});
		}
		
		return $item;
	}
	
	
	return function(){
		
		var $element = UI.Container.set(template);
		
		Infopanel.enable();
		
		$element.find('#apps-content').browser({
			view: new WallViewWithInfo(),
			model: {
				filter: function(r){
					return r instanceof EThing.App;
				},
				flat: true
			},
			selectable:{
				enable: true,
				limit: 0,
				trigger: UI.isTouchDevice ? 'taphold' : 'click',
				cumul: UI.isTouchDevice
			},
			openable:{
				enable: true,
				open: function(r){
					UI.go('app',{
						appid: r.id()
					});
				}
			},
			message:{
				empty: function(){
					var $html = $(
							'<div class="text-center">'+
								'<p>'+
									'No application installed :-('+
								'</p>'+
							'</div>'
						);
					
					return $html;
				}
			}
		}).on('selection.change',function(){
			var selection = $(this).browser('selection');
			Infopanel.setResource(selection);
			
			$element.find('#apps-header button[data-action="remove"]').remove();
			if(selection.length){
				var $removeBtn = $('<button type="button" class="btn btn-link visible-xs-inline-block" data-action="remove"><span class="glyphicon glyphicon-trash" aria-hidden="true"></span><span class="hidden-xs"> remove</span></button>').click(function(){
					UI.runAction('remove', selection);
				}).prependTo('#apps-header-btns');
			}
		}).on('click', function(){
			$(this).browser('select', null);
		});
		
		
		$element.find('#btn-new-app').click(function(){
			
			var $code = $('<div class="subpart subpart-primary" name="code">'+
			  '<h4>Build from source code</h4>'+
			  '<p>Enter below the name of the application you want to develop. Then you will be able to write your own application in an editor.</p>'+
			  '<p>'+
				'<div class="input-group">'+
				  '<input type="text" class="form-control" placeholder="Application name...">'+
				  '<span class="input-group-btn">'+
					'<button class="btn btn-primary" type="button">Edit</button>'+
				  '</span>'+
				'</div>'+
			   '</p>'+
			'</div>');
			var $repository = $('<div class="subpart subpart-primary" name="repository">'+
			  '<h4>Install from an URL</h4>'+
			  '<p>Enter below the URL of the application JSON file you want to install.</p>'+
			  '<p>'+
				'<div class="input-group">'+
				  '<input type="text" class="form-control" placeholder="example.org/install.json">'+
				  '<span class="input-group-btn">'+
					'<button class="btn btn-primary" type="button">Install</button>'+
				  '</span>'+
				'</div>'+
			   '</p>'+
			'</div>');
			
			
			
			var $html = $('<div>').append($code,$repository);
			
			var setError = function(message, tag){
				var $sp = (typeof tag == 'string') ? $('div.subpart[name="'+tag+'"]',$html) : tag;
				if(!message){
					// remove any error
					$sp.find('.alert').remove();
					$sp.find('.input-group').removeClass('has-error');
				}
				else {
					//set error
					var $err = $sp.find('.alert');
					if(!$err.length)
						$err = $('<div class="alert alert-danger" role="alert">').appendTo($sp);
					$err.html(message);
					$sp.find('.input-group').addClass('has-error');
				}
			}
			
			// bind enter key pressed 
			$html.find('input[type="text"]').keypress(function(event) {
				var keycode = (event.keyCode ? event.keyCode : event.which);
				if (keycode == 13) {
					$(this).parent().find('button').trigger('click');
				}
			});
			
			
			function create(options,$h){
				
				setError(null,$h);
				
				EThing.App.create(options,function(app){
					if(app instanceof EThing.App){
						// the creation was successfull
						$html.modal('hide');// will be autoremoved
						
						// redirection 
						switch($h.attr('name')){
							case 'example':
							case 'code':
								UI.go('editor',{
									rid: app.id()
								});
								break;
						}
					}
					else
						// print the error message but do not close the modal dialog
						setError(app.message,$h);
				});
				
			};
			
			
			$repository.find('button').click(function(){
				
				var jsonUrl = $('input',$repository).val().trim();
				
				if(!/^([a-z]+:)?\/\//.test(jsonUrl)) jsonUrl = '//'+jsonUrl;
				
				if(!url_re.test(jsonUrl)){
					setError('Invalid URL.',$repository);
					return;
				}
				
				$.getJSON(jsonUrl).done(function(json){
					
					var data = $.extend(true,{
						"name" : null,
						"script": null,
						"scope": null,
						"icon": null,
						"description": null,
						"version": null,
						"summary": null,
						iconData: null,
						scriptData: null
					},json);
					
					// default
					if(!data.name) data.name = "untitled";
					if(!data.scope) data.scope = "";
					if(!data.summary && data.description) data.summary = data.description;
					
					if(data.summary && data.summary.length>500) data.summary = data.summary.substr(0,500).replace(/[!?., ]+[^!?., ]*$/,'...');
					
					// build the absolute url
					if(data.icon) data.icon = rel2abs(data.icon,jsonUrl);
					data.script = rel2abs(data.script || 'index.html',jsonUrl);
					
					// retrieve all the external resources
					var dfrs = [];
					
					if(data.icon){
						var dfrIcon = $.Deferred();
						EThing.request({
							url: data.icon,
							dataType: 'blob'
						}).done(function(d){
							imageSquareResizeBlob(d, 128, function(blob){
								data.iconData = blob;
								dfrIcon.resolve();
							});
						}).fail(function(){
							// icon not found !
							console.error('not found '+data.icon);
							dfrIcon.resolve(); // resolve anyway
						});
						dfrs.push(dfrIcon);
					}
					
					dfrs.push(
						EThing.request({
							url: data.script,
							dataType: 'text'
						}).done(function(d){
							data.scriptData = d;
						}).fail(function(){
							console.error('not found '+data.script);
						})
					);
					
					$.when.apply($, dfrs).done(function(){
						
						$html.modal('hide', function(){
						
							// generate the confirmation page
							$html = $(
								'<div class="authorize-app">'+
								  '<h1 class="title">'+
									'<img>'+
									'<span class="title">'+data.name+'</span>'+
									'<span class="version small">'+(data.version || '')+'</span>'+
								  '</h1>'+
								  '<h4>Permissions</h4>'+
								  '<p>This application would like to :</p>'+
								  '<p class="permissions"></p>'+
								'</div>'
							);
							
							if(data.description)
								$html.find('h1').after('<h4>Description</h4>', $('<p>').text(data.description));
							
							var iconUrl = data.iconData ? (window.URL || window.webkitURL).createObjectURL(data.iconData) : 'images/noapp.png';
							$html.find('h1 img').attr('src',iconUrl);
							
							var $permissions = $html.find('.permissions'),
								warning_permissions = ['resource:admin', 'resource:write', 'file:write', 'table:write', 'app:write', 'app:execute', 'device:write', 'profile:write', 'proxy:write' ],
								n = 0;
							
							data.scope.split(' ').forEach(function(scope){
								if(!scope) return;
								
								var description = scopes.hasOwnProperty(scope) ? scopes[scope] : scope,
									warning = warning_permissions.indexOf(scope) !== -1;
								
								$permissions.append(
									'<div class="permission '+(warning ? 'permission-warning' : '')+'">'+
										'<span class="glyphicon glyphicon-alert" aria-hidden="true"></span>'+
										'<div class="permission-description">'+description+'</div>'+
									'</div>'
								);
								
								n++;
								
							});
							
							if(!n){
								$permissions.append('No permission asked !');
							}
							
							var $error = $html.find('.alert');
							
							$html.modal({
								title: 'Install application "'+data.name+'" ?',
								buttons: {
									'+Install': function(){
										// install it !
										create({
											name: data.name,
											content: data.scriptData,
											icon: data.iconData,
											scope: data.scope,
											version: data.version || null,
											description: data.summary || null
										},$html);
										
										return false;
									},
									'!Cancel': null
								}
							});
							
						});
						
					}).fail(function(){
						setError('error.',$repository);
					});
					
					
				}).fail(function(){
					setError('not found.',$repository);
				});
				
			});
			
			$code.find('button').click(function(){
				
				var name = $('input',$code).val().trim(),
					defaultScopes = 'resource:read';
				
				if(!name){
					setError('empty or invalid name',$code);
					return;
				}
				
				// install this app with a default content
				
				$.ajax({
					url: 'app.default.txt',
					dataType: 'text'
				})
				.done(function(defaultContent){
					create({
						name: name,
						content: defaultContent,
						scope: defaultScopes
					},$code);
				})
				.fail(function(){
					create({
						name: name,
						scope: defaultScopes
					},$code);
				});
				
			});
			
			$html
				.modal({
					title: '<span class="glyphicon glyphicon-flash" aria-hidden="true"></span> Add a new application'
				})
			
		});
	
	};
}));