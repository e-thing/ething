(function(){
	
	
	Header.setMobileTitle('Editor');
	
	window.main = function() {
		
		var resource = null; // the opened resource if any
		
		
		var error = function(message){
			alert(message);
			window.location.replace(window.location.href.replace(/\?.*$/,'')); // load an empty document, do not modify the history
		}
		
		
        var executeScript = function(resource){
          var win = window.open('app.html?appid=' + resource.id(), 'ScriptWindow');
		  win.focus();
        }
		
		
		var start = function(r){
			
          	resource = r || null;
			
			if(resource && !$.TextViewer.accept(resource))
				return error('Unable to open this resource');
			
			$('#main').on('editor-loaded.tv',function(){
				$(this).textViewer('editor').setSize(null,'100%');
			});
			
			$('#main').on('data-loaded.tv',function(){
				
				var tv = $(this).textViewer(),
					resourceEdited = tv.resource;
				
				
				tv.toggleAction('execute',resourceEdited && (resourceEdited instanceof EThing.App));
				
				document.title = tv.options.filename;
				
				var resourceEdited = tv.resource;
				if(resource && resourceEdited && resource.id() == resourceEdited.id())
					return; // already set
				
				resource = resourceEdited;
					
				// update the url
				var queryString = window.location.search;
				queryString = queryString.replace(/[?&]r=[^&]*/,'');
				if(!queryString.length || queryString[0]!='?')
					queryString = '?'+queryString.replace(/^&/,'');
				if(resource)
					queryString += (queryString.length>1 ? '&' : '') + 'r=' + resource.id();
				
				history.replaceState('', '', queryString);
			});
				
			$('#main').textViewer({
				data: resource,
				lint: true,
				toolbar:{
					filename: {
						format: function(filename){
							var dirname = EThing.Resource.dirname(filename),
								basename = EThing.Resource.basename(filename),
								html = '<span class="editor-basename">'+basename+'</span>';
							if(dirname)
								html = '<span class="editor-dirname">'+dirname+'/</span>'+html;
							return html;
						}
					}
				},
				actions:{
					'open': {
						icon: 'glyphicon-folder-open',
						on: function(tv,data,subaction){
							if(!subaction){
								// returns a deferred object
								return $.OpenDialog({
									filter: $.TextViewer.accept,
									limit: 1
								}).then(function(r){
									return tv.open(r[0]); // piped deferred
								});
							}
							else if(subaction=="local" && data){
								return tv.open(data);
							}
							else if(subaction=="example" && data){
								var filename = data.name+'.html';
								return tv.open({
										filename: filename,
										data: $.get('/ething/lib/examples/'+filename,null,null,'text')
								});
								
							}
						},
						html: function(tv){
							var name = this.name;
							
							var $html = $('<div class="btn-group btn-group-sm" style="display:inline-block;" role="group">'+
								'<button type="button" class="btn btn-default dropdown-toggle" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">'+
								  '<span class="glyphicon '+this.icon+'" aria-hidden="true"></span> '+
								  '<span class="caret"></span>'+
								'</button>'+
								'<ul class="dropdown-menu multi-level"></ul>'+
							'</div>');
							
							var $openResource = $('<a>Open</a>').click(function(){
								// returns a deferred object
								tv.triggerAction(name);
								return false;
							});
							
							
							var fileSelector = $('<input type="file" accept="text/*">');
							fileSelector.change(function () {
								var input = $(this)[0];
								if (!input.files) {
									alert("This browser doesn't seem to support the `files` property of file inputs.");
								}
								else if (input.files[0]) {
									tv.triggerAction(name+'.local',input.files[0]);
								}
							});
							
							var $openLocal = $('<a>Open local</a>').click(function(){
								fileSelector.click();
								return false;
							});
							
							
							var $openExample = $('<ul class="dropdown-menu">');
							$.getJSON('/ething/lib/examples/meta.json',function(examples){
								examples.forEach(function(example){
									$('<a>'+example.name+'</a>').click(function(){
										tv.triggerAction(name+'.example',example);
									}).appendTo($openExample).wrap('<li>');
								});
								
								if(examples.length){
									$html.children('ul').append($('<li class="dropdown-submenu">').append(
										$('<a>Example</a>').click(function(e){
											e.preventDefault();
											e.stopImmediatePropagation();
											return false;
										}),
										$openExample
									));
								}
							});
							
							$html.children('ul').append($openResource,$openLocal);
							
							$openResource.wrap('<li>');
							$openLocal.wrap('<li>');
							
							// special tooltip
							if(!EThing.utils.isTouchDevice){
								if(this.tooltip!==false)
									$html.children('button').tooltip({
										container: tv.$element,
										trigger:'hover',
										placement: 'bottom',
										title: this.tooltip || this.name
									});
							}
							this.tooltip = false; // no tooltip or it will be triggered on the submenu
							
							
							return $html;
						}
					},
					'fullscreen':{
						enable: false
					},
					'execute':{
						on: function(tv){
                          	if(tv.isClean())
                              executeScript(resource);
                          	else
                              // save first
                              return tv.triggerAction('save').done(function(){
                                // execute if the saving was successfull
                                executeScript(resource);
                              });
						},
						icon: 'glyphicon-play'
					}
				}
			});
			
		};
		
		
		var rArg = EThing.utils.getParameterByName('r');
		
		if(rArg){
			EThing.get(rArg)
				.done(start)
				.fail(function(err){
              		error(err.message);
				});
		}
		else
			start(); // empty file
		
		
		window.onbeforeunload = function (e) {
			
			var textViewer = $('#main').textViewer();
			
			if(textViewer && !textViewer.isClean()){
				var e = e || window.event,
					q = 'Some changes are not saved. Do you really want to leave ?';
				
				// For IE and Firefox
				if (e) {
					e.returnValue = q;
				}
				
				// For Safari
				return q;
			}
			
			return null;
		};
	};
	
})()