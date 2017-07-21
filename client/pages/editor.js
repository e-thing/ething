(function (root, factory) {
    if (typeof define === 'function' && define.amd) {
        // AMD. Register as an anonymous module.
        define(['js/ui', 'jquery', 'ething', 'ui/infopanel', 'textviewer', 'css!./editor'], factory);
    }
}(this, function (UI, $, EThing, Infopanel) {
	
	return {
		
		buildView: function(data){
		
		
			var $template = UI.Container.set('<div>loading...</div>');
			
			var $textViewer = this.$textViewer = $('#editor > .ui-container');
			
			var resource = null; // the opened resource if any
			
			
			var error = function(message){
				alert(message);
			}
			
			
			var executeScript = function(resource){
				
				if(resource instanceof EThing.App){
					var win = window.open('#!app?appid=' + resource.id(), 'ScriptWindow');
					win.focus();
				} else if(resource instanceof EThing.File && resource.isScript()){
					
					var $status = $textViewer.textViewer().$element.find('#tv-status');
					var $console = $textViewer.textViewer().$element.find('#tv-console');
					
					$status.html('<div class="info">running ...</div>');
					
					var args = $textViewer.textViewer().$element.find('#tv-arguments input').val();
					resource.execute(args).done(function(result){
						
						$console.empty();
						
						$status.html('<div class="info">Executed in '+(Math.round(result.executionTime*1000)/1000)+' seconds</div>');
						
						if(result.stdout){
							$console.append('<pre class="stdout">'+result.stdout+'</pre>');
						}
						
						if(result.stderr){
							$console.append('<pre class="stderr">'+result.stderr+'</pre>');
						}
						
						if(result.return){
							$console.append('<div class="return">'+result.return+'</div>');
						}
						
						if(!result.ok){
							$console.append('<pre class="stderr">An error occurs !</pre>');
						}
						
					}).fail(function(e){
						$console.append('<div class="stderr">An error occurs ('+e+')</div>');
					});
					
				}
			}
			
			
			var start = function(r){
				
				resource = r || null;
				
				/*if(resource){
					Infopanel.enable();
					Infopanel.setResource(resource);
				} else {
					Infopanel.disable();
				}*/
				
				if(resource && !$.TextViewer.accept(resource))
					return error('Unable to open this resource');
				
				$textViewer.on('editor-loaded.tv',function(){
					$(this).textViewer('editor').setSize(null,'100%');
				});
				
				$textViewer.on('data-loaded.tv',function(){
					
					var tv = $(this).textViewer(),
						resourceEdited = tv.resource;
					
					
					tv.toggleAction('execute',resourceEdited && (resourceEdited instanceof EThing.App || (resourceEdited instanceof EThing.File && resourceEdited.isScript())));
					
					
					require(['https://unpkg.com/split.js/split.min'], function(Split){
						
						tv.$element.find('.tv-content').append('<div id="tv-panel"><div id="tv-arguments"><input type="text" class="form-control" placeholder="arguments"></div><div id="tv-status"></div><div id="tv-console"></div></div>');
						
						tv.$element.find('.tv-content').children().first().attr('id','tv-editor');
						
						tv.$element.find('.tv-content').children().addClass('split split-horizontal');
						
						Split(['#tv-editor', '#tv-panel'], {
							sizes: [75, 25],
							minSize: 200,
							gutterSize: 2
						});
						
					});
					
					var resourceEdited = tv.resource;
					if(resource && resourceEdited && resource.id() == resourceEdited.id())
						return; // already set
					
					resource = resourceEdited;
						
					// update the url
					var data = {};
					if(resource) data.rid = resource.id();
					UI.setUrl('editor',data);
					
					
					
					
					
					
				});
					
				$textViewer.textViewer({
					data: resource || '',
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
							enable: !resource,
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
								
								if(appEditMode || (resource instanceof EThing.App)){
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
								}
								
								$html.children('ul').append($openResource,$openLocal);
								
								$openResource.wrap('<li>');
								$openLocal.wrap('<li>');
								
								// special tooltip
								if(!UI.isTouchDevice){
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
						'saveas': {
							enable: !resource,
						},
						'fullscreen':{
							enable: true
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
				}).on('clean-state-change.tv', function(){
					if($(this).textViewer('isClean')){
						window.onbeforeunload = null;
					}
					else {
						window.onbeforeunload = function (e) {
							var e = e || window.event,
								q = 'Some changes are not saved. Do you really want to leave ?';
							
							// For IE and Firefox
							if (e) {
								e.returnValue = q;
							}
							
							// For Safari
							return q;
						};
					}
				});
				
			};
			
			var appEditMode = data.app === '1';
			
			start(EThing.arbo.findOneById(data.rid));
		},
		
		deleteView: function(){
			
			window.onbeforeunload = null;
				
			if(!this.$textViewer.textViewer('isClean')){
				if(!confirm('Some changes are not saved. Do you really want to leave ?')){
					return false; // cancel page change
				}
			}
			
		}
	};
}));