(function(){
	
	
	var map_actions = [{
			test: function(r){
				return r instanceof EThing.Folder;
			},
			fn: function(r){
				Server.set('browser:'+r.id());
			}
		},{
			test: function(r){
				return r instanceof EThing.App;
			},
			fn: function(r){
				window.location.href = 'app.html?appid='+r.id();
			}
		},{
			test: function(r){
				return r instanceof EThing.Table;
			},
			fn: function(r){
				Server.set('table:'+r.id());
			}
		},{
			test: function(r){
				return /^image\//.test(r.mime());
			},
			fn: function(r){
				Server.set('image:'+r.id());
			}
		},{
			test: function(r){
				return r instanceof EThing.Device && r.url();
			},
			fn: function(r){
				window.location.href = 'device.html?r='+r.id();
			}
		},{
			test: function(r){
				return (r instanceof EThing.File) && r.isText();
			},
			fn: function(r){
				if(r.size() > 4000000)
					throw 'The file is to big to be edited !';
				Server.set('text:'+r.id());
			}
	}];
	
	
	var emptyMessages = {
		'Explore': function(){
			var $html = $(
					'<div class="text-center">'+
						'<p>'+
							'No file or table :-('+
						'</p>'+
						'<p>'+
							'<button class="btn btn-primary" data-name="file"><span class="glyphicon glyphicon-plus" aria-hidden="true"></span> New file</button> '+
							'<button class="btn btn-primary" data-name="table"><span class="glyphicon glyphicon-plus" aria-hidden="true"></span> New table</button>'+
						'</p>'+
					'</div>'
				);
			
			$html.find('button[data-name="file"]').click(function(){
				EThing.ui.createFile();
			});
			$html.find('button[data-name="table"]').click(function(){
				EThing.ui.createTable();
			});
			
			return $html;
		},
		'App': function(){
			var $html = $(
					'<div class="text-center">'+
						'<p>'+
							'No app :-('+
						'</p>'+
						'<p>'+
							'<button class="btn btn-primary" data-name="app"><span class="glyphicon glyphicon-plus" aria-hidden="true"></span> New app</button> '+
						'</p>'+
					'</div>'
				);
			
			$html.find('button[data-name="app"]').click(function(){
				createApp();
			});
			
			return $html;
		},
		'Device': function(){
			var $html = $(
					'<div class="text-center">'+
						'<p>'+
							'No device :-('+
						'</p>'+
						'<p>'+
							'<button class="btn btn-primary" data-name="device"><span class="glyphicon glyphicon-plus" aria-hidden="true"></span> New device</button> '+
						'</p>'+
					'</div>'
				);
			
			$html.find('button[data-name="device"]').click(function(){
				EThing.ui.createDevice();
			});
			
			return $html;
		}
	};
	
	
	var notify = function(message, type, autoRemoveAfterMs){
		
		var cl = 'alert-info',
			prefix = '';
		switch(type){
			case 'danger':
				prefix = '<strong>Error!</strong> ';
				cl = 'alert-danger';
				break;
			case 'success':
				prefix = '<strong>Success!</strong> ';
				cl = 'alert-success';
				break;
			case 'warning':
			default:
				prefix = '<strong>Warning!</strong> ';
				cl = 'alert-warning';
				break;
		}
		
		var $n = $('<div class="alert '+cl+' alert-dismissible fade in" role="alert">'+
		  '<button type="button" class="close" data-dismiss="alert" aria-label="Close"><span aria-hidden="true">&times;</span></button>'+
		  prefix+message+
		'</div>').appendTo('#notification');
		
		if(autoRemoveAfterMs!==0) // 0 means no autoremove
			window.setTimeout(function(){
				$n.alert('close');
			},autoRemoveAfterMs || 5000)
	}
	
	

	
	
	function eachAction(resource, func) {
		
		if($.isArray(resource) && resource.length==1)
			resource = resource[0];
		
		var multiple = $.isArray(resource),
			openWith = Server.get().path.split(':')[0];
		
		// actions
			
		if(!multiple){
			if(isOpenable(resource))
				func('open','eye-open',function(){
					open(resource);
				});

			if (typeof resource.getContentUrl == 'function') {
				func('download','download',function(){
					
					function download(url, filename, callback){
						
						EThing.request({
							url: url,
							dataType: 'blob'
						}).done(function(data){
							EThing.utils.require('//cdnjs.cloudflare.com/ajax/libs/FileSaver.js/2014-11-29/FileSaver.min.js',function(){
								saveAs(data, filename);
								if(typeof callback == 'function')
									callback.call(resource);
							});
						})
					};
					
					if(resource instanceof EThing.Table){
						
						$('<div>')
							.form({
								'format': {
									input: function(){
										return '<select id="add-app-contentType" class="form-control">'+
												'<option selected value="json">JSON</option>'+
												'<option value="csv">CSV</option>'+
											  '</select>';
									}
								}
							})
							.modal({
								title: "Format ...",
								buttons: {
									'+Download': function(){
										var $this = $(this);
										$this.form().validate().done(function(props){
											var format = props.format;
											download(resource.getContentUrl()+'?fmt='+(format=="json"?"json_pretty":format), resource.basename().replace(/\.db$/i,'')+'.'+format,function(){
												$this.modal('hide');
											});
										});
										return false;
									},
									'Cancel': function(){}
								}
							})
					}
					else
						download(resource.getContentUrl(), resource.basename());
					
				});
			}
			
			if (resource instanceof EThing.Table){
				openWith==='graph' ?
				func('table','th-list',function(){
					Server.set('table:'+resource.id());
				})
				:
				func('chart','stats',function(){
					if(resource.keys().length > 3){
						
						$('<div>')
							.graphSimpleWizard(resource)
							.modal({
								title: 'Graph : "'+resource.name()+'"',
								buttons: {
									'+Draw': function(){
										var $this = $(this);
										$this.graphSimpleWizard('validate',function(options){
											$this.modal('hide',function(){
												Server.set('graph:'+resource.id(),options);
											});
										});
										return false;
									},
									'Cancel': null
								}
							});
					}
					else
						Server.set('graph:'+resource.id(),$.Graph.defaultOptionsFromTable(resource));
				});
			}
			
			if (
				(resource instanceof EThing.App) ||
				((resource instanceof EThing.File) && resource.isText())
				){
				func('edit','edit',function(){
					EThing.ui.edit(resource);
				});
			}
			

			if (!(resource instanceof EThing.Folder) && resource.user().id() == EThing.auth.getUser().id()){
			
				func('modify','cog',function(){
					EThing.ui.settings(resource, function(){
						Server.reload();
					});
				});
				
				func('remove','trash',function(){
					if (confirm("Remove the resource " + resource.name() + " definitely ?"))
						resource.remove(function() {
							EThing.arbo.remove(resource);
						});
				});
				
			}
			
			
		}
		else {
			// multiple selection
			
			var deletableResources = [];
			for(var i=0; i<resource.length; i++){
				if(!(resource[i] instanceof EThing.Folder) && resource[i].user().id() == EThing.auth.getUser().id())
					deletableResources.push(resource[i]);
			};
			if(deletableResources.length > 0){
				func('remove','trash',function(){
					if (confirm("Remove the "+deletableResources.length+" selected resource(s) definitely ?"))
						removeResources(deletableResources);
				});
			}
			
		}
		
		
	}
	
	var blobToImage = function(blob){
		// build an image from the blob data
		var urlCreator = window.URL || window.webkitURL;
		var imageUrl = urlCreator.createObjectURL( blob );
		
		var image = new Image();
		image.src = imageUrl;
		return image;
	};
	
	var loadImage = EThing.utils.createCache(function(url) {
		var deferred = $.Deferred();
		
		if(!url){
			deferred.reject();
			return null;
		}
		
		var x = new XMLHttpRequest();
		x.open("GET", url, true);
		x.setRequestHeader('X-ACCESS-TOKEN', EThing.auth.getToken());
		x.responseType = 'blob';
		x.onload=function(e){
			if (x.status >= 200 && x.status < 300) {  
				// Obtain a blob: URL for the image data.
				deferred.resolve(this.response);
			}
			else
				deferred.reject();
		}
		x.onerror=function(e){
			deferred.reject();
		}
		x.onabort=function(e){
			deferred.reject();
		}
		x.onprogress=function(e){
			if (e.lengthComputable)
				deferred.notify(e.loaded / e.total);
		}
		x.send();
		
		return deferred.promise(x);
	});
	
	
	
	
	
	
	
	
	function createApp(){
		EThing.ui.createApp(function(mode){
			switch(mode){
				case 'example':
				case 'code':
					EThing.ui.edit(this);
					break;
				case 'repository':
					Server.set('app:'+this.id());
					break;
			}
		});
	};
	
	
	
	function removeResources(resources, cb){
		if(!$.isArray(resources))
			resources = [resources];
		
		var promises = resources.map(function(resource){
			return EThing.Resource.remove(resource).done(function(){
				EThing.arbo.remove(resource,true);
			});
		});
		$.when.apply($, promises).then(function(){
			if(typeof cb == 'function')
				cb();
		});
	}
	
	
	
	RightPanel = {
		
		hide: function(){
			$('body').removeClass('rp');
		},
		show: function(){
			$('body').addClass('rp');
		},
		toggle: function(){
			if($('body').hasClass('rp'))
				RightPanel.hide();
			else
				RightPanel.show();
		},
		details: function(resource,forceUpdate){
			var $rightPanelDetails = $('#right-panel #details');
			
			if(arguments.length==0){
				forceUpdate = true;
				resource = EThing.arbo.findOneById($rightPanelDetails.data('rid'));
			}
			
			if($.isArray(resource) && resource.length==1)
				resource = resource[0];
			
			var multiple = $.isArray(resource),
				selectionId = multiple ? (resource.length ? resource.map(function(r){return r.id();}).join(',') : null) : (resource ? resource.id() : null);
				
			
			if(!forceUpdate && $rightPanelDetails.data('rid')===selectionId)
				return; // no change
			
			$rightPanelDetails.data('rid',selectionId);
			
			if(selectionId===null){ // no selection
				if($rightPanelDetails.is(':visible'))
					$rightPanelDetails.slideUp(400,function(){
						$(this).hide();
					});
				return;
			}
			
			
			
			var $title = $('[data-role="title"]',$rightPanelDetails).empty(),
				$thumbnail = $('[data-role="thumbnail"]',$rightPanelDetails).empty(),
				$detail = $('[data-role="detail"]',$rightPanelDetails).empty(),
				$action = $('[data-role="action"]',$rightPanelDetails).empty(),
				$description = $('[data-role="description"]',$rightPanelDetails).empty().hide();
			
			var props = null;
			
			if(multiple){
				// multiple selection
				
				var svg = '<svg viewBox="0 0 32 32" style="fill: #5959B6;"><circle cx="18" cy="14" r="14"></circle><circle cx="17" cy="15" r="14" fill="white"></circle><circle cx="16" cy="16" r="14"></circle><circle cx="15" cy="17" r="14" fill="white"></circle><circle cx="14" cy="18" r="14"></circle><text x="14" y="18" font-size="22" fill="white" font-weight="bold" font-family="Arial" text-anchor="middle" alignment-baseline="central">+</text></svg>';
				$thumbnail.html(svg);
				
				var $cntttl = $('<div style="white-space: normal;">'), maxTitleRows = 5;
				
				if(resource.length>maxTitleRows)
					$cntttl.html( resource.slice(0,maxTitleRows).map(function(r){return r.basename();}).join(',<br>')+'<small><br>...<br>+'+(resource.length-maxTitleRows)+' more</small>' );
				else
					$cntttl.html( resource.map(function(r){return r.basename();}).join(',<br>') );
				$title.html($cntttl);
				
				var totalSize = resource.reduce(function(size,r){return size + (r.size ? r.size() : 0);},0);
				
				props = {
					'size': EThing.utils.sizeToString(resource.reduce(function(size,r){return size + (r.size ? r.size() : 0);},0)),
					'length': resource.length+' resources'
				};
				
			}
			else { // single resource
			
				$title.html(resource.basename());
				$thumbnail.html($.Browser.generateSvgResourceIcon(resource));
				
				var imageUrl = (typeof resource.thumbnailLink == 'function') ? resource.thumbnailLink() : ((typeof resource.iconLink == 'function') ? resource.iconLink() : null);
				if(imageUrl){
					loadImage(imageUrl)
						.done(function(blob){
							if($rightPanelDetails.data('rid')===resource.id())
								$thumbnail.html(blobToImage(blob));
						});
				}

			
				props = EThing.ui.getResourceFormattedValues(resource,{
					"location":{
						formatter: function(v){
							var showOnMapLink = Server.url('map:'+resource.id());
							if($.isPlainObject(v)){
								return '<a href="'+showOnMapLink+'">'+v.latitude+"N "+v.longitude+"E"+'</a>';
							}
							else
								return (resource instanceof EThing.Device) ? "none" : null;
						}
					},
					"createdBy":{
						formatter: function(id){
							var createdByRess = EThing.arbo.findOneById(id);
							return createdByRess ? ('<a href="explore.html'+Server.url(createdByRess.type().toLowerCase()+':'+createdByRess.id())+'">'+createdByRess.basename()+'</a>') : 'Me';
						}
					}
				}, function(){
					return ["name","type","user","createdBy","createdDate","modifiedDate","lastSeenDate","size","mime","length","maxLength","expireAfter","battery","rules","location","url"].indexOf(this.name) >= 0;
				});
				
			}
			
			// print the properties
			for(var i in props){
				if(props[i]!==null){
					$('<div class="row">').append(
						'<div class="col-xs-4 ellipsis key">'+i+'</div>',
						$('<div class="col-xs-8 ellipsis value">').append(props[i])
					).appendTo($detail);
				}
			}
			
			// print the actions
			function createAction(name, icon, callback, data){
				if(data && $.isFunction(data.domValidator) && !data.domValidator($action))
					return;
				var $a = $('<button type="button" class="btn btn-default" aria-label="'+name+'">'+
								'<span class="glyphicon glyphicon-'+icon+'" aria-hidden="true"></span>'+
							'</button>');

				if($.isFunction(callback))
					$a.click(callback);
				
				if(!EThing.utils.isTouchDevice)
					$a.tooltip({
						container: $action,
						trigger:'hover',
						placement: 'bottom',
						title: name
					});

				$a.appendTo($action);
			}
			
			eachAction(resource, createAction);
			
			// description
			var description = (!multiple && $.isFunction(resource.description)) ? resource.description() : null;
			if(description)
				$description.html(description).show();
			
			if(!$rightPanelDetails.is(':visible'))
				$rightPanelDetails.slideDown(400,function(){
					$(this).show();
				});
			
			
		},
		showUsage: function(){
			var id = String(Math.round(Math.random()*1000000)),
				$usage = $('#usage').html('loading...').data('id',id);
			
			getUsage(function(usage){
				if(id != $usage.data('id')) return;
				
				var hasQuota = !!usage.quota_size,
					tableUsed = usage.used - usage.fileTotalSize - usage.appTotalSize,
					vquota = hasQuota ? usage.quota_size : usage.used,
					usedRatio = usage.used / vquota,
					fileUsedRatio = usage.fileTotalSize / vquota,
					appUsedRatio = usage.appTotalSize / vquota,
					tableUsedRatio = tableUsed / vquota;
					
				$usage.html(
					'<h2 class="usage-used">'+
						EThing.utils.sizeToString(usage.used)+' used'+
					'</h2>'+
					'<div class="usage-bar">'+
						'<div class="usage-bar-file" style="width: '+(Math.round(fileUsedRatio*100))+'%"></div>'+
						'<div class="usage-bar-table" style="width: '+(Math.round((fileUsedRatio+tableUsedRatio)*100))+'%"></div>'+
						'<div class="usage-bar-app" style="width: '+(Math.round(usedRatio*100))+'%"></div>'+ // else
					'</div>'+
					'<table class="usage-bar-detail">'+
						'<tr class="usage-bar-detail-file">'+
							'<td class="usage-bar-detail-color"></td>'+
							'<td class="usage-bar-detail-type">File</td>'+
							'<td class="usage-bar-detail-size">'+EThing.utils.sizeToString(usage.fileTotalSize)+'</td>'+
						'</tr>'+
						'<tr class="usage-bar-detail-table">'+
							'<td class="usage-bar-detail-color"></td>'+
							'<td class="usage-bar-detail-type">Table</td>'+
							'<td class="usage-bar-detail-size">'+EThing.utils.sizeToString(tableUsed)+'</td>'+
						'</tr>'+
						'<tr class="usage-bar-detail-app">'+
							'<td class="usage-bar-detail-color"></td>'+
							'<td class="usage-bar-detail-type">App</td>'+
							'<td class="usage-bar-detail-size">'+EThing.utils.sizeToString(usage.appTotalSize)+'</td>'+
						'</tr>'+
					'</table>'+
					'<h4 class="usage-count-title">Details :</h4>'+
					'<table class="usage-count">'+
						'<tr class="usage-count-file">'+
							'<td class="usage-count-value">'+(usage.nbFile || 0)+'</td>'+
							'<td class="usage-count-name">File</td>'+
						'</tr>'+
						'<tr class="usage-count-table">'+
							'<td class="usage-count-value">'+(usage.nbTable || 0)+'</td>'+
							'<td class="usage-count-name">Table</td>'+
						'</tr>'+
						'<tr class="usage-count-device">'+
							'<td class="usage-count-value">'+(usage.nbDevice || 0)+'</td>'+
							'<td class="usage-count-name">Device</td>'+
						'</tr>'+
						'<tr class="usage-count-app">'+
							'<td class="usage-count-value">'+(usage.nbApp || 0)+'</td>'+
							'<td class="usage-count-name">App</td>'+
						'</tr>'+
					'</table>'
				);
			});
		}
	};
	
	
	/* special view */
	function WallViewWithInfo(opt){
		$.Browser.Views.Wall.call(this, opt);
	}
	WallViewWithInfo.prototype = Object.create($.Browser.Views.Wall.prototype);
	
	WallViewWithInfo.prototype.createItem = function(resource){
		var $item = $.Browser.Views.Wall.prototype.createItem.apply(this,Array.prototype.slice.call(arguments));
		
		var self = this;
		
		// info
		var $info = $('<div>').html('<span class="glyphicon glyphicon-option-horizontal" aria-hidden="true"></span>').addClass('col-info').click(function(e){
			self.table().select(resource);
			e.stopPropagation();
			RightPanel.show();
			return false;
		});
		
		$item.prepend(
			$info
		);
		
		return $item;
	}
	
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
		
		var self = this,
			createdByRess = EThing.arbo.findOneById(resource.createdBy()),
			hidden = /^\./.test(resource.basename());
		
		// append the name of the creator
		if(createdByRess instanceof EThing.Device){
			$item.children('td.col-name').append('<span class="createdBy"><span class="glyphicon glyphicon-phone" aria-hidden="true"></span> '+createdByRess.name()+'</span>');
		}
		
		// show the size under the name on small screen only
		
		$item.children('td.col-name').append('<div class="col-name-size visible-xs-block">'+$item.find('.col-size').html()+'</div>');
		
		// add an info column only visible on small device
		$('<td>').html('<span class="glyphicon glyphicon-option-horizontal" aria-hidden="true"></span>').addClass('col-info').click(function(e){
			self.table().select(resource);
			e.stopPropagation();
			RightPanel.show();
			return false;
		}).appendTo($item);
		
		// hide all the resources starting with a dot '.'
		if(hidden)
			$item.hide();
		
		return $item;
	}
	
	
	function displayResources(resources,view,selection,emptyMessage,openable){
		
		if(typeof openable == 'undefined')
			openable = true; // default behaviour
		
		if(!Array.isArray(resources))
			resources = [resources];
		
		var openfct = function(e){
			var resource = e.data.item;
			if(open(resource))
				e.stopImmediatePropagation(); // disable default behaviour (not necessary if openable.enable == false)
			else
				alert('unable to open this resource');
		};
		
		var $b = $('#main');
		
		if(view instanceof $.Browser.Views.Wall){
			// replace the original icon by the thumbnail when available (only for the wall view)
			$b.on('redraw',function(){
				$('[data-role="item"]',this).each(function(){
					var $this = $(this),
						resource = $(this).data('item'),
						imageUrl = (typeof resource.thumbnailLink == 'function') ? resource.thumbnailLink() : ((typeof resource.iconLink == 'function') ? resource.iconLink() : null);
					
					if(imageUrl){
						loadImage(imageUrl)
							.done(function(blob){
								$('.col-icon',$this).html(blobToImage(blob));
							});
					}
				});
				
			});
		}
		
		
		$b
			.browser({
				model: {
					root: resources
				},
				view: view || new TableViewWithInfo(),
				selectable:{
					enable: true,
					limit: 0,
					trigger: 'click',
					cumul: false
				},
				openable:{
					enable: false
				},
				// custom events on rows
				row: openable ? {
					events: EThing.utils.isTouchDevice
					? {
						'click': openfct
					}
					: {
						'dblclick': openfct
					}
				} : {},
				message:{
					empty: emptyMessage || 'empty'
				}
			})
			.on('selection.change',function(){
				RightPanel.details($(this).browser('selection'));
			})
			
		
		if(selection instanceof EThing.Resource){
			$b.browser('select',selection);
		}
		
	}
	
	
	
	
	function isOpenable(resource){
		for(var i=0; i<map_actions.length; i++){
			if(map_actions[i].test(resource))
				return true;
		}
		return false;
	};
	
	function open(resource){
		for(var i=0; i<map_actions.length; i++){
			if(map_actions[i].test(resource)){
				try{
					map_actions[i].fn(resource);
				} catch(e){
					alert(e);
				}
				return true;
			}
		}
		return false;
	};
	
	
	
	function addGlobalAction(opt){
		
		opt = $.extend(true,{
			name: null,
			icon: null,
			click: null,
			html: function(){
				return $('<button type="button" class="btn btn-default">'+
					'<span class="glyphicon glyphicon-'+this.icon+'" aria-hidden="true"></span>'+
					'<span class="hidden-xs"> '+this.name+'</span>'+
				'</button>');
			},
			mobileOnly: false
		},opt);
		
		opt.icon = opt.icon || opt.name;
			
		
		var $a = opt.html.call(opt);
		
		$a.attr('data-role','global-action');
		$a.attr('data-name',opt.name);
		$a.click(opt.click);
		
		var $copy = $a.clone(true);
		
		if(!opt.mobileOnly){
			$a.appendTo('#header-action');
		}
		
		$copy.addClass('navbar-collapse-btn').appendTo('#navbar [data-role="navbar-extra-btn"]');
		
	}
	
	function removeGlobalAction(name){
		$('[data-role="global-action"][data-name="'+name+'"]').remove();
	}
	
	
	
	function setPath(w){
		
		if(typeof w == 'string'){
			$('#breadcrumb').breadcrumb('value', w);
			Header.setMobileTitle(w);
		}
		else if(w instanceof EThing.Resource && !w.isRoot){
			$('#breadcrumb').breadcrumb('value',w.name());
			
			Header.setMobilePath(w.basename(),function(){
				Server.set('browser:'+w.parent().id());
			});
		}
		else{
			$('#breadcrumb').breadcrumb('value',null);
			Header.restoreMobileTitle();
		}
	}
	
	
	// ex: browse:55aecc2
	function parseUri(filter,route){
		return function(uri, data){
			var resource;
			
			// check if an id is present in the uri xxx:id
			var i = uri.indexOf(':');
			if(i>=0){
				resource = EThing.arbo.findOneById(uri.substr(i+1));
			
				// check if the given resource match the filter
				if(resource){
					if(typeof filter == 'string'){
						if(resource.type() !== filter){
							Server.reset();
							return false;
						}
					}
					else if(typeof filter == 'function'){
						if(!filter(resource)){
							Server.reset();
							return false;
						}
					}
					else if(Array.isArray(filter)){
						var pass = false;
						for(var i=0; i<filter.length; i++)
							if(resource.type() === filter[i]){
								pass=true;
								break;
							}
						if(!pass){
							Server.reset();
							return false;
						}
					}
				}
				else {
					// resource id given but does not exist !
					Server.reset();
					return false;
				}
				
				
				RightPanel.details(resource instanceof EThing.Folder && resource.isRoot ? false : resource, true);
			}
			else
				RightPanel.details(false); // hide the details
			
			return route(resource,data);
		}
	}

	
	
	
	/*
	* Events
	*/
	
	
	// on Uri change
	Server.begin(function(name){
		
		// get the entry name
		var subprog = name.match(/^[a-z0-9]*/i)[0];
		
		// remove any previous content
		$('#main').replaceWith('<div id="main" data-app='+subprog+'><div style="text-align: center;margin: 20px;">loading ...</div>');
		
		// for small screen, if the right panel was shown, hide it
		RightPanel.hide();
		
		
	},null);
	
	Server.bind(/^browser(:.*)?$/,parseUri(['Folder','Table','File'],function(resource){
		
		if(!resource)
			resource = EThing.arbo.root();
		
		var dir,selection;
		
		if(resource instanceof EThing.Folder){
			dir = resource;
		}
		else {
			dir = resource.parent();
			selection = resource;
		}
		
		addGlobalAction({
			name:'new',
			icon:'plus',
			html: function(){
				var $html = $('<div class="dropdown">'+
					'<button type="button" class="btn btn-default" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">'+
						'<span class="glyphicon glyphicon-'+this.icon+'" aria-hidden="true"></span>'+
						'<span class="hidden-xs"> '+this.name+'</span>'+
					'</button>'+
				  '<ul class="dropdown-menu dropdown-menu-right">'+
				  '</ul>'+
				'</div>');
				
				$html.children('button').dropdown();
				
				var $ul = $html.children('ul'),
					icons = {
						'File': 'file',
						'Table': 'list'
					};
				['File','Table'].forEach(function(type){
					$('<li>').append(
						$('<a>').html('<span class="glyphicon glyphicon-'+icons[type]+'" aria-hidden="true"></span> '+type).click(function(){
							EThing.ui['create'+type](null,dir);
						})
					).appendTo($ul);
				});
				
				
				return $html;
			}
		});
		
		setPath(dir);
		
		DragAndDrop.enable(function(file){
			EThing.ui.Uploader.upload(file,dir);
		});
		
		displayResources(dir.children(function(r){
			return !((r instanceof EThing.App) || (r instanceof EThing.Device)); // hide app and device
		}),null,selection, emptyMessages['Explore']);
		
	}),function(){
		removeGlobalAction('new');
		DragAndDrop.disable();
	});
	
	
	
	
	Server.bind(/^table:/,parseUri('Table',function(resource){
		setPath(resource);
		$('#main').tableViewer({
			table: resource
		});
	}));
	Server.bind(/^text:/,parseUri(['File','App'],function(resource){
		setPath(resource);

		$('#main').textViewer({
			data: resource,
			readonly: true,
			toolbar: {
				enable: true,
				filename: {
					enable: false
				}
			},
			actions: {
				'open': {
					enable: false
				},
				'edit': {
					icon: 'glyphicon-edit',
					on: function(){
						EThing.ui.edit(resource);
					}
				},
				/*'mode':{
					enable: true
				},*/
				'fullscreen':{
					enable: false
				}
			}
		}).addClass('embedded');
	}));
	Server.bind(/^image:/,parseUri(function(resource){
		return (resource instanceof EThing.File) && /^image\//.test(resource.mime());
	},function(resource){
		setPath(resource);

		var directoryPath = resource.dirname(),
			loadIndex = null;
		
		// select only the image in the same folder
		var images = EThing.arbo.find(function(r){
			return /^image\//.test(r.mime()) && r.dirname() === directoryPath;
		});
		
		if(resource){
			for(var i=0; i<images.length; i++){
				if(images[i].id()===resource.id()){
					loadIndex = i;
					break;
				}
			}
		}
		
		$('#main')
			.on('show.imageviewer',function(ev,el){
				RightPanel.details(el.content);
			})
			.imageViewer({
				elements: images,
				navigator:{
					enable: true
				},
				index: loadIndex
			});
		
	}));
	Server.bind(/^graph(:.*)?$/,parseUri('Table', function(resource, data){
		setPath('Graph');
		$('#main').graph(data);
	}),null);
	Server.bind(/^map(:.*)?$/,parseUri(function(r){
		return typeof r.location == 'function';
	},function(resource){
		
		setPath('Map');
		
		$('#main').mapViewer({
			resources: EThing.arbo.find(),
			marker:{
				onClick:function(resource){
					RightPanel.details(resource);
				}
			},
			center: resource,
			onload: function(){
				var map = this;
				//setTimeout(function(){
					map.showPopup(resource);
				//},1000);
			}
		});
	}));
	Server.bind(/^device(:.*)?$/,parseUri('Device',function(resource){
		addGlobalAction({
			name:'new',
			icon:'plus',
			click:function(){
				EThing.ui.createDevice();
			}
		});
		
		setPath('Device');
		
		displayResources(EThing.arbo.find(function(r){
			return r.type() == 'Device';
		}), new DeviceView(), resource, emptyMessages['Device']);
		
	}),function(){
		removeGlobalAction('new');
	});
	Server.bind(/^dv:.*$/,parseUri('Device',function(resource){
		
		setPath('Device');
		
		$('#main').deviceViewer({
			device: resource
		});
		
	}),function(){
		removeGlobalAction('new');
	});
	Server.bind(/^app(:.*)?$/,parseUri('App',function(resource){
		addGlobalAction({
			name:'new',
			icon:'plus',
			click:function(){
				createApp();
			}
		});
		
		setPath('App');
		
		displayResources(EThing.arbo.find(function(r){
			return r.type() == 'App';
		}), new WallViewWithInfo(), resource, emptyMessages['App']);
		
	}),function(){
		removeGlobalAction('new');
	});
	
	Server.bind(/^(image|text|table|graph)(:.+)$/,function(uri){
		addGlobalAction({
			name: 'info',
			icon: 'option-horizontal',
			click:RightPanel.toggle,
			mobileOnly: true
		});
	},function(){
		removeGlobalAction('info');
	});
	
	
	
	
	
	EThing.ajaxError(function( error, xhr, options ) {
		notify(error.message,'danger',10000);
	});
	
	
	// reset hash
	window.location.hash = window.location.hash.replace(/#([^!].*)?$/,'');
	
	
	
	
	
	
	
	/*
	* Views
	*/
	
	
	var DeviceView = function(opt) {
		
		this._options = $.extend(true,{
			class: 'deviceview'
		},opt);
		
		$.Table.View.call(this);
	}
	DeviceView.prototype = Object.create($.Table.View.prototype);

	DeviceView.prototype.init = function($container, table){
		
		$.Table.View.prototype.init.call(this,$container,table);
		
		this._$grid = $('<div>').appendTo(this.$().addClass('container-fluid')).addClass(this._options.class).addClass('row');
		
	}
	DeviceView.prototype.clear = function(){
		this._$grid.empty();
	}

	DeviceView.prototype.createItem = function(device){
		var self = this, isServer = !!device.url();
		
		var $item = $('<div>').addClass('col-xs-12 col-md-6 col-lg-4');
		
		if(isServer)
			$item.addClass('dev-server');
		
		// construct the item dom element
		
		var name = EThing.ui.getResourceProperty(device,'name'),
			lastSeenDate = EThing.ui.getResourceProperty(device,'lastSeenDate'),
			location = EThing.ui.getResourceProperty(device,'location'),
			url = EThing.ui.getResourceProperty(device,'url');
		
		
		// icon
		var $icon = $('<div>').html($.Browser.generateSvgResourceIcon(device,true)).addClass('col-icon');
		
		// open button
		if(isServer){
			var $b = $('<div class="dev-open-btn">').append(
				'<span class="glyphicon glyphicon-tasks" aria-hidden="true"></span>',
				'<div>Open</div>'
			).appendTo($icon).click(function(){
				open(device);
				e.stopPropagation();
			});
		}
		
		// name
		var $name = $('<h4 class="col-name">').addClass('ellipsis').html(name.formattedValue);
		
		// last time the device communicate
		var $time = $('<div class="col-date">').addClass('ellipsis').html('<span class="glyphicon glyphicon-time" aria-hidden="true"></span> '+lastSeenDate.formattedValue);
		
		// location
		var $loc = location.formattedValue ? $('<div class="col-loc">').addClass('ellipsis').html('<span class="glyphicon glyphicon-map-marker" aria-hidden="true"></span> '+'<a href="'+Server.url('map:'+device.id())+'">'+location.formattedValue+'</a>') : null;
		
		
		// info
		var $info = $('<span class="glyphicon glyphicon-option-horizontal" aria-hidden="true"></span>').addClass('col-info').click(function(e){
			self.table().select(device);
			e.stopPropagation();
			RightPanel.show();
			return false;
		});
		
		$item.append(
			$('<div>').append(
				$icon,
				$('<div class="meta">').append(
					$info,
					$name,
					$time,
					$loc
				),
				'<div style="clear: both;"></div>'
			)
		);
		
		
		this._$grid.append($item);
		
		return $item;
	}
	
	
	
	var usageDfr;
	function getUsage(cb){
		if(!usageDfr)
			usageDfr = EThing.Resource.usage();
		
		usageDfr.done(function(usage){
			
			EThing.arbo.load(function(){
				
				$.extend(usage,{
					'nbResource': 0,
					'fileTotalSize': 0,
					'appTotalSize': 0,
					'tableTotalRowCount': 0
				});
				
				EThing.arbo.list().forEach(function(r){
					usage.nbResource++;
					
					var type = r.type(),
						metaname = 'nb'+type;
					
					if(!usage.hasOwnProperty(metaname))
						usage[metaname] = 0;
					usage[metaname]++;
					
					if(type==='File')
						usage.fileTotalSize += r.size();
					else if(type==='Table')
						usage.tableTotalRowCount += r.length();
					else if(type==='App')
						usage.appTotalSize += r.size();
					
				})
				
				if(typeof cb == "function")
					cb(usage);
			});
			
		});
		
	}
	
	
	
	// drag and drop
	
	// The plugin code (ie: http://stackoverflow.com/questions/10253663/how-to-detect-the-dragleave-event-in-firefox-when-dragging-outside-the-window/10310815#10310815)
	$.fn.draghover = function(options) {
	  return this.each(function() {

		var collection = $(),
			self = $(this);

		self.on('dragenter', function(e) {
		  if (collection.length === 0) {
			self.trigger('draghoverstart');
		  }
		  collection = collection.add(e.target);
		});

		self.on('dragleave drop', function(e) {
		  collection = collection.not(e.target);
		  if (collection.length === 0) {
			self.trigger('draghoverend');
		  }
		});
	  });
	};
	
	
	var DragAndDrop = {
		enable: function(onDrop){
			
			var $target = $(document),
				$body = $('body'),
				$overlay = $('<div class="drop-overlay"><span>Drop Here</span></div>');
			
			$target.draghover().on({
			  'draghoverstart': function() {
				$overlay.appendTo($body);
			  },
			  'draghoverend': function() {
				$overlay.detach();
			  }
			});
			$target.on('dragenter', function(e) {
				e.preventDefault();
				e.stopPropagation();
				return false;
			});
			
			$target.on('dragover', function(e) {
				e.preventDefault(); // Cancel drop forbidding
				e.stopPropagation();
				return false;
			});
			
			$target.on('dragleave', function(e) {
				e.preventDefault();
				e.stopPropagation();
				return false;
			});
			
			$target.on('drop', function(e) {	
				if(e.originalEvent.dataTransfer){
				   if(e.originalEvent.dataTransfer.files.length) {
						// Stop the propagation of the event
						e.preventDefault();
						e.stopPropagation();
						
						// fetch FileList object
						var files = e.originalEvent.dataTransfer.files;

					   // process all File objects
						for (var i = 0, f; f = files[i]; i++) {
							if(typeof onDrop == 'function')
								onDrop(f);
						}
				   }  
				}
				else {
					alert('unable to upload this file');
				}
				return false;
			});
			
		},
		disable: function(){
			var $target = $(document);
		
			$target.off('dragenter');
			$target.off('dragover');
			$target.off('dragleave');
			$target.off('drop');
			$target.off('draghoverstart');
			$target.off('draghoverend');
			
		}
	}
	
	
	
	
	
	EThing.arbo.on('resource-remove resource-add',function(e){
		var resource = e.resource;
		// update the browser
		if(Server.match(/^(browser|app|device)(:.*)?$/)){
			if(!(e.type == 'resource-add' && Server.match(/^app/)))
				Server.reload();
		}
		else {
			Server.set('browser:'+resource.parent().id()); // go to the parent directory
		}
	});
	
	
	/*
	* ENTRY POINT
	*/
	window.main = function(){
		
		// load the resources
		EThing.arbo.load(function(resources){
			
			Server.run({
				defaultState:{
					path: 'browser',
					data: null
				},
				onUnbindState:function(state){
					Server.reset();
					return false;
				}
			});
			//$(document).trigger("data:resources", [resources]);
			
			var f = EThing.arbo.find(function(r){
				return r instanceof EThing.File;
			})[0];
			
		});
		
		
		
		// load breadcrumb
		$('#breadcrumb').breadcrumb({
			onClick: function(path){
				if(typeof path == "string")
					Server.set(path.length? ('browser:'+path) : 'browser');
			},
			maxItems: 5
		});
		
		
		RightPanel.showUsage();
		
		if(EThing.utils.isTouchDevice)
			$('body').addClass('touchOnly');
		
	}
	
})();