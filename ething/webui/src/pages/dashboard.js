(function (root, factory) {
    if (typeof define === 'function' && define.amd) {
        // AMD. Register as an anonymous module.
        define(['ui/core', 'jquery', 'ething', 'ui/gridwidget', 'css!./dashboard', 'form', 'ui/resourceselect', 'ui/formmodal'], factory);
    }
}(this, function (UI, $, EThing, Grid) {
	
	
	
	
	
	var Page = function(opt){
		
		
		var self = {
			title: opt.title || 'dashboard',
			dashboard: opt.dashboard,
			widgets: opt.widgets || []
		};
		
		var grid = Grid({
			columns: opt.columns
		});
		
		grid.$element.appendTo(self.dashboard.$element.find('.db-pages'));
		
		return $.extend(self, grid, {
			
			show: function(){
				var self = this;
				
				if(!this.grid){
					
					this.draw();
					
					
					this.on('gridItemAdded', function(evt, gridItem){
						gridItem.on('updated', function(evt){
							self.save();
						});
					});
					
					self.widgets.forEach(function(widgetOpt){
						
						try {
							var widget = null, options = {
								x: widgetOpt.x,
								y: widgetOpt.y,
								width: widgetOpt.width,
								height: widgetOpt.height
							};
							
							if(widgetOpt.resource){
								
								var resource = EThing.arbo.findOneById(widgetOpt.resource);
								
								if(resource) widget = UI.widgetManager.resource(resource).instanciate();
								
								if(widget) widget.__ = {
									resource: options.resource
								};
								
							} else if(widgetOpt.type){
								
								var factory = UI.widgetManager.generic(widgetOpt.type);
								widget = factory.instanciate(widgetOpt.options);
								
								if(widget) widget.__ = {
									type: widgetOpt.type,
									options: widgetOpt.options
								};
								
								if(factory.configure)
									options.actions = [{
										name: 'edit',
										icon: 'edit',
										fn: function(){
											self.dashboard.editWidget(this);
										}
									}];
							}
							
							if(widget) self.addWidget(widget, options);
						
						} catch(err) {
							console.error(err);
						}
					});
					
					
					this.on('gridItemRemoved gridLayoutChanged gridItemAdded', function(evt){
						self.save();
					});
					

				}
				
				// hide all pages except this one
				self.dashboard.pages.forEach(function(page){
					if(page !== self){
						page.hide();
					}
				});
				
				// show this page
				self.$element.show();
				
				// update Header
				self.dashboard.header.update();
				
				//if(self.grid) self.grid.recalculate_faux_grid();
			},
			
			hide: function(){
				if(this.$element) this.$element.hide();
			},
			
			
			update: function(){
				grid.update.call(this);
				this.dashboard.header.update();
				if(this.gridItems.length==0){
					this.dashboard.setEditMode(false);
				}
			},
			
			setOptions: function(opt){
				
				if(opt.title != this.title){
					this.title = opt.title;
					this.dashboard.header.update();
				}
				
				grid.setOptions.call(this, opt);
				
			},
			
			serialize: function(){
				var o = {
					title: this.title,
					columns: this.columns,
					widgets: []
				};
				
				this.gridItems.forEach(function(gridItem){
					
					var go = {
						x: gridItem.x,
						y: gridItem.y,
						width: gridItem.width,
						height: gridItem.height
					};
					
					var widget = gridItem.widget;
					
					if(widget.__.type)
						go.type = widget.__.type;
					
					if(widget.__.options)
						go.options = widget.__.options;
					
					if(widget.__.resource)
						go.resource = widget.__.resource;
					
					o.widgets.push(go);
				});
				
				return o;
			},
			
			save: function(){
				this.dashboard.save();
			},
			
			destroy: function(){
				
				this.off('gridItemRemoved gridLayoutChanged gridItemAdded');
				
				grid.destroy.call(this);
			}
			
		});
		
	}
	
	
	var Header = function(opt){
		
		var self = {
			dashboard: opt.dashboard,
			$element: null
		};
		
		return $.extend(self, {
			
			draw: function(){
				
				var self = this;
			
				this.$element = $('<div>').addClass('db-header').html(
					
					'<button type="button" class="btn btn-link db-header-page-prev-btn"><span class="glyphicon glyphicon-menu-left" aria-hidden="true"></span></button>'+
					'<span class="db-header-title"></span>'+
					'<button type="button" class="btn btn-link db-header-page-next-btn"><span class="glyphicon glyphicon-menu-right" aria-hidden="true"></span></button>'+
					
					'<div class="pull-right btn-toolbar">'+
						
						'<button class="btn btn-link db-header-pin-device-btn hidden-xs">Pin device</button>'+
						'<button class="btn btn-link db-header-add-btn hidden-xs">Widget</button>'+
						'<button class="btn btn-link db-header-edit-btn hidden-xs">Edit</button>'+
						
						'<div class="btn-group">'+
						  '<button type="button" class="btn btn-link dropdown-toggle" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">'+
							'<span class="glyphicon glyphicon-option-horizontal" aria-hidden="true"></span>'+
						  '</button>'+
						  '<ul class="dropdown-menu dropdown-menu-right">'+
							'<li class="visible-xs-inline"><a href="#" data-role="device-pin">pin a device</a></li>'+
						    '<li class="visible-xs-inline"><a href="#" data-role="widget-add">add a new widget</a></li>'+
							'<li class="visible-xs-inline"><a href="#" data-role="edit">edit</a></li>'+
							'<li class="dropdown-header">Page</li>'+
							'<li><a href="#" data-role="page-add">add a new page</a></li>'+
							'<li><a href="#" data-role="page-remove">remove the current page</a></li>'+
							'<li><a href="#" data-role="page-edit">properties</a></li>'+
						  '</ul>'+
						'</div>'+
						
					'</div>'
					
				).prependTo(this.dashboard.$element.find('.db-content'));
				
				this.$element.find('.db-header-edit-btn').click(function(){
					self.dashboard.setEditMode(!self.dashboard.isEditMode());
				});
				
				this.$element.find('.db-header-add-btn').click(function(){
					self.dashboard.createWidget();
				});
				
				this.$element.find('.db-header-pin-device-btn').click(function(){
					self.dashboard.pinResource();
				});
				
				this.$element.find('.db-header-page-prev-btn').click(function(){
					self.dashboard.gotoPage('-');
				});
				
				this.$element.find('.db-header-page-next-btn').click(function(){
					self.dashboard.gotoPage('+');
				});
				
				this.$element.find('ul > li > a').click(function(evt){
					evt.preventDefault();
					
					var role = $(this).attr('data-role');
					
					switch(role){
						case 'device-pin':
							self.dashboard.pinResource();
							break;
						case 'widget-add':
							self.dashboard.createWidget();
							break;
						case 'edit':
							self.dashboard.setEditMode(!self.dashboard.isEditMode());
							break;
						case 'page-edit':
							self.dashboard.editPage(self.dashboard.currentPage());
							break;
						case 'page-add':
							self.dashboard.editPage(null);
							break;
						case 'page-remove':
							if(confirm('Do you really want to remove the current dashboard ?')){
								self.dashboard.removePage(self.dashboard.currentPage());
							}
							break;
					}
					
					return false;
				});
				
			},
			
			update: function(){
				var page = this.dashboard.currentPage();
				
				this.$element.find('.db-header-title').text(page.title);
				
				this.$element.find('.db-header-edit-btn').toggle(!!page.gridItems.length);
				
				this.$element.find('.db-header-page-prev-btn').toggle(this.dashboard.pageIndex>0);
				this.$element.find('.db-header-page-next-btn').toggle(this.dashboard.pageIndex<this.dashboard.pages.length-1);
			},
			
			destroy: function(){
				if(this.$element)
					this.$element.empty();
			}
		});
		
	}
	
	// dashboard module :
	
	var Dashboard = {
		
		configFilename : '.dashboard.json',
		
		options: {},
		
		file: null, // the file instance of the config file
		
		$element: null, // the container
		
		header: null, // Header instance
		
		pages : [], // Page instances
		
		pageIndex: 0,
		
		load: function(element, pageIndex, callback){
			
			var self = this;
			
			this.pageIndex = pageIndex || 0;
			
			function onOptionsLoad(){
				
				self.draw();
				
				self.options.pages.forEach(function(pageOptions){
					self.pages.push(Page($.extend({}, pageOptions, {
						dashboard: self
					})));
				});
				
				// if no page loaded, add an empty page
				if(self.options.pages.length===0){
					self.pages.push(Page($.extend({}, {
						dashboard: self
					})));
				}
				
				self.gotoPage(self.pageIndex);
				
				done();
				
			}
			function done(){
				
				var resizeTimeout = null;
				
				$(window).on('resize.dashboard',function(e){
					if(e.target !== window) return;
					
					if(resizeTimeout!==null) clearTimeout(resizeTimeout);
					resizeTimeout = setTimeout(function(){
						self.resize();
					}, 500);
				});
				
				if(typeof callback === 'function')
					callback.call(self);
				
			}
			
			this.options = {
				pages: []
			};
			
			this.$element = $(element);
			
			this.header = Header({
				dashboard: this
			});
			
			// prepare the dom
			this.$element.addClass('db container-fluid').html(
				'<p class="db-loader text-center">'+
					'loading ...'+
				'</p>'
			);
			
			
			this.file = EThing.arbo.findOne(function(r){
				return r instanceof EThing.File && r.name() === self.configFilename;
			});
			
			if(this.file){
				// dashboard file found : load it !
				this.file.read().done(function(opt){
					
					// try to decode json string
					if(typeof opt == 'string')
						try{
							self.options = JSON.parse(opt);
						}
						catch(e){}
					else
						self.options = opt;
					
					onOptionsLoad();
				});
			}
			else {
				// no dashboard file found !
				onOptionsLoad();
			}
			
			
			
		},
		
		draw: function(){
			
			this.$element.html(
				'<div class="db-content">'+
					'<div class="db-pages"></div>'+
				'</div>'
			);
			
			this.header.draw();
			
			
		},
		
		gotoPage: function(pageIndex){
			var self = this;
			
			if(pageIndex==='-') pageIndex = this.pageIndex - 1;
			if(pageIndex==='+') pageIndex = this.pageIndex + 1;
			
			if(pageIndex >= this.pages.length) pageIndex = this.pages.length - 1;
			if(pageIndex < 0) pageIndex = 0;
			
			this.pageIndex = pageIndex;
			
			UI.setUrl('dashboard',{
				index: this.pageIndex
			});
			
			this.currentPage().show();
		},
		
		currentPage: function(){
			return this.pages[this.pageIndex];
		},
		
		setEditMode: function(editMode){
			this.$element.toggleClass('editmode', !!editMode);
		},
		
		isEditMode: function(){
			return this.$element.hasClass('editmode');
		},
		
		save: function(){
			var self = this;
			
			if(this.file){
				
				var options = $.extend({}, this.options, {pages:[]});
				
				this.pages.forEach(function(page){
					options.pages.push(page.serialize());
				});
				
				this.file.write( JSON.stringify(options, null, 4) );
			}
			else {
				EThing.File.create({
					name: self.configFilename
				}).done(function(file){
					self.file = file;
					self.save();
				})
			}
		},
		
		resize: function(){
			this.currentPage().resize();
		},
		
		createWidget: function(callback){
			return this.editWidget(null, callback);
		},
		
		pinResource: function(callback){
			
			var self = this,
				page = self.currentPage();
			
			$.FormModal({
				item: new $.Form.FormLayout({
					items:[{
						name: 'resource',
						item: new $.Form.ResourceSelect({
							filter: function(r){
								return !!UI.widgetManager.resource(r);
							},
							validators: [$.Form.validator.NotEmpty],
							categorise: true,
							treeView: true
						})
					}]
				}),
				title: 'Pin a resource on the dashboard',
				validLabel: '+Add'
			}, function(options){
				
				var resource = EThing.arbo.findOneById(options.resource);
				
				var widget = UI.widgetManager.resource(resource).instanciate();
				
				widget.__ = {
					resource: options.resource
				};
				
				var gridItem = page.addWidget(widget);
				
				if(typeof callback === 'function')
					callback.call(self, gridItem);
				
			});
			
		},
		
		editWidget: function(gridItem, callback){
			
			var self = this,
				factory = null,
				widgetType = null,
				widget = gridItem ? gridItem.widget : null,
				editing = !!widget,
				type = null,
				options = null,
				configApplyFn = null,
				page = self.currentPage();
			
			if(widget){
				type = widget.__.type;
				options = widget.__.options;
			}
			
			var $html = $('<div>'+
			  '<div class="factory"></div>'+
			'</div>');
			
			
			function setWidgetType(newWidgetType){
				
				if(widgetType == newWidgetType) return; // the selection does not change !
				
				widgetType = newWidgetType;
				
				var $factory = $html.children('.factory').empty().data('widgetType',widgetType);
				
				$html.children('.description').remove();
				
				
				factory = UI.widgetManager.generic(newWidgetType);
				
				if(factory.description)
					$('<p class="description">').html(factory.description).insertBefore($factory);
				
				configApplyFn = factory.configure ? factory.configure($factory[0],editing ? options : null) : null;
				
			}
			
			var l = {};
			
			UI.widgetManager.generic().forEach(function(factory){
				l[factory.title] = factory.name;
			});
		
		
			$('<div>').prependTo($html).form(new $.Form.FormLayout({
				items:[{
					name: 'type',
					label: 'Type',
					item: new $.Form.Select({
						items: l,
						readonly: editing,
						onload: function(){
							if(editing){
								this.value(type);
								setWidgetType(type);
							}
							else {
								this.change(function(){
									setWidgetType(this.value());
								}).change();
							}
						}
					})
				}]
			}));
			
			
			$html.modal({
				title: editing ? 'Editing ...' : 'Create a widget',
				buttons: {
					'+Apply': function(){
						if(!factory)
							return false;
						
						var opt = configApplyFn ? configApplyFn() : {}, $this = $(this);
						
						$.when(opt).done(function(options){
							if($.isPlainObject(options)){
								
								$this.modal('hide');
								
								var widget = factory.instanciate(options);
								
								widget.__ = {
									type: widgetType,
									options: options
								};
								
								if(editing){
									// replace
									gridItem.setWidget(widget);
								}
								else {
									
									var actions = [];
									
									if(configApplyFn){
										actions.push({
											name: 'edit',
											icon: 'edit',
											fn: function(){
												self.editWidget(this);
											}
										});
									}
									
									page.addWidget(widget, {
										actions: actions
									});
								}
								
								if(typeof callback == 'function')
									callback.call(self);
								
								self.setEditMode(false);
							}
						})
						
						return false;
					},
					'Cancel': null
				}
			});
			
		},
		
		
		editPage: function(page, callback){
			var self = this,
				editing = !!page;
			
			$.FormModal({
				item: new $.Form.FormLayout({
					items:[{
						name: 'title',
						item: new $.Form.Text()
					},{
						name: 'columns',
						item: new $.Form.Number({
							minimum: 1,
							maximum: 12,
							validators: [$.Form.validator.Integer]
						})
					}]
				}),
				value: editing ? {
					title: page.title,
					columns: page.columns
				} : {
					title: '',
					columns: 8
				},
				title: editing ? ('Editing dashboard \''+page.title+'\'') : 'Add a new dashboard',
				validLabel: editing ? '+Apply' : '+Add'
			}, function(options){
				
				if(editing){
					page.setOptions(options);
				} else {
					self.pages.push(Page($.extend({}, options, {
						dashboard: self
					})));
					self.gotoPage(self.pages.length-1);
				}
				
				if(typeof callback == 'function')
					callback.call(self);
				
				self.save();
			});
			
		},
		
		removePage: function(page){
			for(var i in this.pages){
				if(page===this.pages[i]){
					this.pages.splice(i,1);
					page.destroy();
					this.gotoPage(this.pageIndex);
					this.save();
					break;
				}
			}
		},
		
		destroy: function(){
			
			$(window).off('resize.dashboard');
			
			this.pages.forEach(function(page){
				page.destroy();
			});
			
			this.pages = [];
			
			this.$element.empty();
			
			this.header.destroy();
		}
		
	};
	
	return {
		
		buildView: function(data){
			UI.Container.set('<div>');
			
			Dashboard.load('#dashboard > .ui-container', parseInt(data.index));
		},
		
		deleteView: function(){
			Dashboard.destroy();
		}
		
	};
}));