(function (root, factory) {
    if (typeof define === 'function' && define.amd) {
        // AMD. Register as an anonymous module.
        define(['js/ui', 'text!./data.html', 'jquery', 'ething', 'ui/infopanel', 'ui/droppable', 'ui/uploader', 'browser','css!./data', 'jquery-mobile-events', 'formmodal', 'css!font-awesome'], factory);
    }
}(this, function (UI, template, $, EThing, Infopanel, Droppable, Uploader) {
	
	
	
	// custom view
	
	function TableViewWithInfo(opt){
		$.Browser.Views.Table.call(this, opt);
	}
	TableViewWithInfo.prototype = Object.create($.Browser.Views.Table.prototype);
	
	TableViewWithInfo.prototype.init = function($container, table){
		var $item = $.Browser.Views.Table.prototype.init.apply(this,Array.prototype.slice.call(arguments));
		$('<th>').addClass('col-info').appendTo($container.find('thead > tr'));
	}
	TableViewWithInfo.prototype.createItem = function(resource){
		var $item = $.Browser.Views.Table.prototype.createItem.apply(this,Array.prototype.slice.call(arguments));
		
		var self = this/*,
			hidden = /^\./.test(resource.basename())*/;
		
		// show the size under the name on small screen only
		
		$item.children('td.col-name').append('<div class="col-name-size visible-xs-block">'+$item.find('.col-size').html()+'</div>');
		
		// add an info column only visible on small device
		$('<td>').html('<span class="glyphicon glyphicon-option-vertical" aria-hidden="true"></span>').addClass('col-info').click(function(e){
			self.table().select(resource);
			e.stopPropagation();
			Infopanel.show();
			return false;
		}).appendTo($item);
		
		// hide all the resources starting with a dot '.'
		/*if(hidden)
			$item.hide();*/
		
		return $item;
	}
	
	
	// global variable
	var $browser, $breadcrumb;
	
	
	var updateBreadcrumb = function(dir){
		$breadcrumb.empty();
		var parts = dir.name().split('/'), d='';
		$breadcrumb.append(parts[0].length ? '<li><a href="#!data">Home</a></li>' : '<li class="active">Home</li>');
		parts.forEach(function(p, index){
			if(!p.length) return;
			d+='/'+p;
			if(index === parts.length-1)
				$breadcrumb.append('<li class="active">'+p+'</li>');
			else
				$breadcrumb.append('<li><a href="#!data?path='+encodeURIComponent(d)+'">'+p+'</a></li>');
		});
	};
	
	return {
		
		buildView: function(data){
			
			
			var dir = EThing.arbo.findOneById(data.path) || EThing.arbo.root();
			
			var $element = UI.Container.set(template);
			
			$breadcrumb = $element.find('.breadcrumb');
			
			// breadcrumb
			updateBreadcrumb(dir);
			
			
			
			$(document).on('keydown.ui-page-data',function(evt){
				switch(evt.which){
					case 46: // delete
						UI.runAction('remove', $browser.browser("selection"));
						break;
					case 37: // left
					case 38: //up
						var browser = $browser.browser(),
							selection = browser.selection()[0];
						browser.select( selection ? browser.prev(selection) : browser.last(), evt.ctrlKey || evt.shiftKey);
						break;
					case 39: // right
					case 40: //down
						var browser = $browser.browser(),
							selection = browser.selection()[0];
						browser.select( selection ? browser.next(selection) : browser.first(), evt.ctrlKey || evt.shiftKey);
						break;
					case 13: // open
						UI.runAction('open', $browser.browser("selection")[0]);
						break;
					case 27: // escape
						$browser.browser('select',null);
						break;
					case 8 : // back
						var dir = $browser.browser('model').currentFolder();
						
						if(!dir.isRoot){
							UI.go('data',{
								path: dir.parent().id()
							});
						}
						break;
				}
			});
			
			new Droppable({
				target: $element,
				onDrop: function(file, path){
					
					var dir = $browser.browser('model').currentFolder().name();
					if(dir && dir.length) dir += '/';
					
					Uploader.upload(file, dir+path).fail(function(){
						alert('Unable to upload this file !');
					});
				}
			});
			
			Infopanel.enable();
			
			var filter = function(r){
				if(r instanceof EThing.Folder){
					// show only if there are some child in it !
					return r.find(filter).length > 0;
				}
				return !(r instanceof EThing.App || r instanceof EThing.Device || /^\./.test(r.basename()));
			};
			
			$browser = $element.find('#data-content').browser({
				view: new TableViewWithInfo(),
				model: {
					filter: filter,
					root: dir,
					allowTraversing: false
				},
				selectable:{
					enable: true,
					limit: 0,
					trigger: UI.isTouchDevice ? [{
						event: 'click',
						selector: '.col-icon'
					}, 'taphold'] : 'click',
					cumul: UI.isTouchDevice
				},
				openable:{
					open: function(r){
						if(!(r instanceof EThing.Folder)){
							if(!UI.open(r))
								alert('Unable to open this resource !');
						} else {
							UI.go('data',r.id() !== '/' ? {
								path: r.id()
							} : undefined);
						}
						return false; // prevent default behaviour (== folder opening)
					}
				},
				message:{
					empty: function(){
						var $html = $(
								'<div class="text-center">'+
									'<p>'+
										'No data :-('+
									'</p>'+
								'</div>'
							);
						
						return $html;
					}
				}
			}).on('selection.change',function(){
				var selection = $(this).browser('selection');
				Infopanel.setResource(selection);
				
				$element.find('#data-header button[data-action="remove"]').remove();
				if(selection.length){
					var $removeBtn = $('<button type="button" class="btn btn-link visible-xs-inline-block" data-action="remove"><span class="glyphicon glyphicon-trash" aria-hidden="true"></span><span class="hidden-xs"> remove</span></button>').click(function(){
						UI.runAction('remove', selection);
					}).prependTo('#data-header-btns');
				}
				
				
			}).on('click', function(){
				$(this).browser('select', null);
			});
			
			
			$element.find('#btn-create-file').click(function(){
				
				var form = UI.getResourceForm('File', null, ['name','description']).then(function(formEntries){
				
					formEntries.push({
						label: 'content',
						item: new $.Form.File({
							name: 'content',
							base64: true,
							title: '<span class="glyphicon glyphicon-open" aria-hidden="true"></span> import a local file',
							format: {
								'out': function(){
									return this.getFile();
								}
							}
						})
					});
					
					return new $.Form.FormLayout({
						items: formEntries,
						onload: function(){
							var nameItem = this.findItem('name'),
								contentItem = this.findItem('content');
							contentItem.change(function(){
								var file = this.getFile();
								if(file) nameItem.value(file.name);
							});
						}
					});
				});
				
				$.FormModal({
					item: form,
					title: '<span class="glyphicon glyphicon-file" aria-hidden="true"></span> Create a new File',
					validLabel: '+Add'
				},function(props){
					
					var dir = $browser.browser('model').currentFolder();
					
					if(dir instanceof EThing.Folder && dir.name().length && props.name){
						props.name = dir.name()+'/'+props.name;
					}
					
					// extract the content from the properties
					var content = props.content;
					delete props.content;
					
					
					EThing.File.create(props).done(function(r){
						// the creation was successful
						
						// upload the content now !
						if(content){
							Uploader.UI.add(EThing.Resource.basename(r.name()),r.write(content));
						}
						
					});
					
				});
				
			});
			
			$element.find('#btn-create-table').click(function(){
				
				var form = $.Deferred();
				
				require(['csv'], function(CSV){
					
					UI.getResourceForm('Table', null, ['name','description']).done(function(formEntries){
						
						formEntries.push({
							label: 'content',
							item: new $.Form.File({
								name: 'content',
								base64: false,
								title: '<span class="glyphicon glyphicon-open" aria-hidden="true"></span> import a local file',
								validators: [
									function(value){
										this.data = null;
										
										if(typeof value == 'string'){
											
											// detect the format from the extension
											var file = this.getFile(),
												format = 'json', 
												data = null;
											if(file){
												var extension = file.name.indexOf('.')>=0 ? file.name.split('.').pop().toLowerCase() : '';
												if( CSV.extensions.indexOf(extension) != -1) format = 'csv';
											}
											
											if(format === 'json'){
												try {
													data = JSON.parse(value);
												} catch (e){
													throw 'invalid JSON content';
												}
											}
											else { // csv 
												try {
													var csvData = CSV.parse(value);
													
													data = [];
						
													// first line is the field's name
													var fields = csvData.shift();

													for(var i=0; i<csvData.length; i++){
														var d = {};
														for(var j=0; j<fields.length && j<csvData[i].length; j++)
															d[fields[j]] = csvData[i][j];
														data.push(d);
													}
													
												} catch (e){
													throw 'invalid CSV content';
												}
											}
											
											if(!Array.isArray(data))
												throw 'The content must be an array of data.';
											
											this.data = data;
										}
										
									}
								],
								format:{
									'out': function(){
										return this.data;
									}
								}
							})
						});
						
						form.resolve(new $.Form.FormLayout({
							items: formEntries,
							onload: function(){
								var nameItem = this.findItem('name'),
									contentItem = this.findItem('content');
								contentItem.change(function(){
									var file = this.getFile();
									if(file) nameItem.value(file.name);
								});
							}
						}));

					});
					
				});
				
				$.FormModal({
					item: form,
					title: '<span class="glyphicon glyphicon-list" aria-hidden="true"></span> Create a new Table',
					validLabel: '+Add'
				},function(props){
					
					var dir = $browser.browser('model').currentFolder();
					
					if(dir instanceof EThing.Folder && dir.name().length && props.name){
						props.name = dir.name()+'/'+props.name;
					}
					
					var dfr = EThing.Table.create(props);
					
					if(props.content)
						Uploader.UI.add(props.name,dfr);
				});
				
			});
		
		},
		
		updateView: function(data){
			var dir = EThing.arbo.findOneById(data.path) || EThing.arbo.root();
			updateBreadcrumb(dir);
			$browser.browser('open',dir);
		},
		
		deleteView: function(){
			$(document).off('keydown.ui-page-data');
			$browser.browser('destroy');
			
			delete $browser;
			delete $breadcrumb;
		}
	
	};
}));