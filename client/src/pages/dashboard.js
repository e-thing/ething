(function (root, factory) {
    if (typeof define === 'function' && define.amd) {
        // AMD. Register as an anonymous module.
        define(['ui/core', 'jquery', 'ething', 'widgetcollection', 'css!./dashboard', 'form', 'ui/resourceselect', 'ui/formmodal', 'jquery.gridster'], factory);
    }
}(this, function (UI, $, EThing, WidgetCollection) {
	
	
	var isTouchDevice = navigator ? (/android|webos|iphone|ipad|ipod|blackberry|iemobile|opera mini/i.test(navigator.userAgent.toLowerCase())) : false;
	
	
	
	var GridItem = function(opt){
		
		var self = {
			x: opt.x || null,
			y: opt.y || null,
			width: opt.width || 1,
			height: opt.height || 1,
			
			options: opt.options || {},
			type: opt.type || null,
			device: opt.device || null,
			
			widget: null
		};
		
		
		
		
		var page = opt.page;
		var dashboard = page.dashboard;
		
		
		var onRemove = opt.onRemove;
		
		
		return $.extend(self, {
			
			// remove this item from the grid !
			remove: function(){
				
				this.removeWidget();
				
				// remove this widget from the grid
				if(this.$gridItem) page.grid.remove_widget(this.$gridItem);
				
				this.$gridItem = null;
				
				if(typeof onRemove === 'function'){
					onRemove.call(self);
				}
				
				
			},
			
			
			setWidget: function(type, options, callback){
				if(type instanceof EThing.Device){
					self.device = type.id();
					self.type = null;
				} else {
					self.type = type;
					self.device = null;
				}
				self.options = options;
				return self.draw(callback);
			},
				
			draw: function(callback){
				if(self.widget){
					self.removeWidget();
				}
				
				if(!this.$gridItem){
					
					var $gridItem = this.$gridItem = $('<div>');
					
					var $wrapper = $('<div>').addClass('db-widget-wrapper');
					
					var $widgetEdit = $('<div>').addClass('db-widget-edit')
						.html('<div><div class="btn-group btn-group-xs">'+
							'<button class="btn btn-link gs-drag-handle" data-name="move"><span class="glyphicon glyphicon-move" aria-hidden="true"></span></button> '+
							'<button class="btn btn-link" data-name="edit"><span class="glyphicon glyphicon-edit" aria-hidden="true"></span></button> '+
							'<button class="btn btn-link" data-name="remove"><span class="glyphicon glyphicon-trash" aria-hidden="true"></span></button>'+
						'</div></div>');
					
					$widgetEdit.find('button[data-name="edit"]').click(function(){
						edit();
					});
					
					$widgetEdit.find('button[data-name="remove"]').click(function(){
						self.remove();
					});
					
					$wrapper.append($widgetEdit, '<div class="db-widget-err">').appendTo($gridItem);
					
					var edit = function(callback){
						dashboard.editWidget(self,callback);
					}
					
					var grid = page.grid;
					
					$gridItem.data('gridItem',self);
					
					// add this item to the grid
					grid.add_widget($gridItem, self.width, self.height, self.x, self.y, null, null, function(){
						
					});
				}
				
				var idfr;
				if(self.device){
					var device = EThing.arbo.findOneById(self.device);
					if(device){
						var type = WidgetCollection.getWidgetNameFromDevice(device);
						if(type)
							idfr = WidgetCollection.instanciate(type, self.options, device);
						else {
							self.setError('widget not found !', true);
						}
					} else {
						self.setError('device not found !', true);
						return;
					}
				} else {
					idfr = WidgetCollection.instanciate(self.type, self.options);
				}
				
				idfr.done(function(widget, name){
					self.widget = widget;
					
					widget.$element.addClass('db-widget-type-'+name.replace('/','-'));
					self.$gridItem.find('.db-widget-wrapper').prepend(widget.$element);
					widget.draw();
					
				}).always(callback).fail(function(err){
					self.setError(err, true);
				});
				
			},
			
			removeWidget: function(){
				// destroy the widget only, but not the grid item
				if(self.widget) {
					self.widget.destroy();
					self.widget.$element.remove();
					self.widget = null;
				}
			},
			
			resize: function(){
				if(self.widget) self.widget.resize();
			},
			
			serialize: function(){
				var o = {
					options: self.options,
					x: self.x,
					y: self.y,
					width: self.width,
					height: self.height
				};
				
				if(self.device)
					o.device = self.device;
				else
					o.type = self.type;
				
				return o;
			},
			
			setError: function(err, showremoveBtn){
				if(err===false){
					this.$gridItem.find('.db-widget-err').hide();
					return this;
				}
				console.error(err);
				
				var $html = $('<p><span class="glyphicon glyphicon-warning-sign" aria-hidden="true"></span><br>'+((typeof err == 'object' && err !== null && typeof err.message == 'string') ? err.message : (err || 'error'))+'</p>');
				
				if(showremoveBtn){
					var self = this;
					$('<button class="btn btn-link">remove</button>').click(function(){
						self.remove();
					}).appendTo($html);
				}
				
				this.$gridItem
					.find('.db-widget-err')
					.html($html)
					.show();
				return this;
			}
			
		});
		
	}
	
	
	var Page = function(opt){
		
		var self = {
			
			gridItems: [],
			
			grid: null, // the grid instance
			
			$element: null,
			
			title: opt.title || '',
				
			widgets: opt.widgets || [],
			
			dashboard: opt.dashboard,
			
			columns: opt.columns || 8,
			
			id: 'Page-'+Math.round(Math.random()*100000)
			
		};
		
		self.widgets.forEach(function(item){
			
			var gridItem = GridItem($.extend({
				page: this,
				onRemove: function(){
					// remove it from the gridItems list
					self.gridItems.forEach(function(gi, index){
						if(gi===this){
							self.gridItems.splice(index,1);
							return false;
						}
					}, this);
					
					// save changes & update
					self.save();
					self.update();
				}
			}, item));
			
			this.gridItems.push(gridItem);
			
		},self);
		
		
		return $.extend(self, {
			
			show: function(callback){
				var self = this;
				
				var dfr = $.Deferred();
				
				if(!this.$element){
					this.draw(function(){
						dfr.resolve();
					});
				} else {
					dfr.resolve();
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
				
				dfr.done(function(){
					
					if(self.grid) self.grid.recalculate_faux_grid();
					
					if(typeof callback === 'function')
						callback.call(self);
				});
			},
			
			hide: function(){
				if(this.$element) this.$element.hide();
			},
			
			setOptions: function(opt, callback){
				
				var change = false, redraw = false;
				
				if(opt.title != this.title){
					change = true;
					this.title = opt.title;
				}
				
				if(opt.columns != this.columns){
					change = true;
					redraw = true;
					this.columns = opt.columns;
				}
				
				if(change){
					
					if(redraw){
						this.destroy();
					}
					
					this.show(callback);
				}
			},
			
			draw: function(callback){
				
				var self = this;
				
				this.$element = $('<div>').attr('id', this.id).addClass('db-page').html(
					'<div class="text-center db-page-empty">'+
						'<p>Your dashboard is empty !</p>'+
					'</div>'+
					'<div class="gridster">'+
						'<div></div>'+
					'</div>'
				).appendTo(this.dashboard.$element.find('.db-pages'));
				
				var timeoutId = null;
				
				// create the grid
				var $grid = this.$element.find('.gridster > div').gridster({
					namespace: '#'+this.id,
					autogenerate_stylesheet: true,
					widget_margins: [10, 10],
					/*widget_base_dimensions: ['auto', 240],
					min_cols: 4,
					max_cols: 4,*/
					widget_base_dimensions: ['auto', 160],
					min_cols: this.columns,
					max_cols: this.columns,
					serialize_params: function($w, wgd){
						return { col: wgd.col, row: wgd.row, width: wgd.size_x, height: wgd.size_y, $el: $w };
					},
					draggable: {
						stop: function(event, ui){
							if(timeoutId!==null) clearTimeout(timeoutId);
							var timeoutId = setTimeout(function(){self.saveLayout();}, 500);
						},
						handle: '.db-widget-edit *'
					},
					resize: {
						enabled: true,
						stop: function(e, ui, $widget){
							if(timeoutId!==null) clearTimeout(timeoutId);
							var timeoutId = setTimeout(function(){self.saveLayout();}, 500);
							
							$widget.data('gridItem').resize();
						}
					},
					responsive_breakpoint: 640,
					
					widget_selector: 'div',
					widget_margins: [5, 5],
					
					shift_widgets_up: false,
					shift_larger_widgets_down: false,
					collision: {
						wait_for_mouseup: true
					}
				});
				
				this.grid = $grid.data('gridster');
				
				var dfrs = [];
				
				this.gridItems.forEach(function(item){
					var dfr = $.Deferred();
					item.draw(function(){
						dfr.resolve();
					});
					dfrs.push(dfr);
				},this);
				
				this.update();
				
				$.when.apply($, dfrs).done(function(){
					if(!self.$element) return; // destroyed
					
					if(typeof callback === 'function')
						callback.call(self);
				});
			},
			
			
			addDashboardItem: function(item, noSave, callback){
				var self = this;
				
				var gridItem = GridItem($.extend({
					dashboard: this.dashboard,
					page: this,
					grid: this.grid,
					onRemove: function(){
						// remove it from the gridItems list
						self.gridItems.forEach(function(gi, index){
							if(gi===this){
								self.gridItems.splice(index,1);
								return false;
							}
						}, this);
						
						// save changes & update
						self.save();
						self.update();
					}
				}, item));
				
				this.gridItems.push(gridItem);
				
				gridItem.draw(callback);
				
				if(!noSave){
					this.save();
				}
				
				this.update();
				
				return gridItem;
				
			},
			
			update: function(){
				if(this.$element) this.$element.find('.db-page-empty').toggle(this.gridItems.length==0);
				this.dashboard.header.update();
				if(this.gridItems.length==0){
					this.dashboard.setEditMode(false);
				}
			},
			
			saveLayout: function(force){
				
				var widgetPositions = this.grid.serialize();
				var change = false;
				
				widgetPositions.forEach(function(widgetPos){
					var gridItem = widgetPos.$el.data('gridItem');
					
					if(gridItem.x !== widgetPos.col || gridItem.y !== widgetPos.row || gridItem.width !== widgetPos.width || gridItem.height !== widgetPos.height){
						change = true;
						gridItem.x = widgetPos.col;
						gridItem.y = widgetPos.row;
						gridItem.width = widgetPos.width;
						gridItem.height = widgetPos.height;
					}
				});
				
				if(change || force===true)
					this.save();
			},
			
			serialize: function(){
				var o = {
					title: this.title,
					columns: this.columns,
					widgets: []
				};
				
				this.gridItems.forEach(function(gridItem){
					o.widgets.push(gridItem.serialize());
				});
				
				return o;
			},
			
			save: function(){
				this.dashboard.save();
			},
			
			destroy: function(){
				
				this.gridItems.forEach(function(gridItem){
					gridItem.removeWidget();
				});
				
				if(this.grid){
					this.grid.destroy();
					this.grid = null;
				}
				
				if(this.$element) this.$element.empty();
				this.$element = null;
			},
			
			resize: function(){
				this.gridItems.forEach(function(gridItem){
					gridItem.resize();
				});
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
						
						'<button class="btn btn-link db-header-add-btn"><span class="glyphicon glyphicon-plus" aria-hidden="true"></span><span class="hidden-xs"> Widget</span></button>'+
						'<button class="btn btn-link db-header-edit-btn"><span class="glyphicon glyphicon-cog" aria-hidden="true"></span><span class="hidden-xs"> Edit</span></button>'+
						
						'<div class="btn-group">'+
						  '<button type="button" class="btn btn-link dropdown-toggle" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">'+
							'<span class="glyphicon glyphicon-option-horizontal" aria-hidden="true"></span>'+
						  '</button>'+
						  '<ul class="dropdown-menu dropdown-menu-right">'+
							'<li class="dropdown-header">Page</li>'+
							'<li><a href="#" data-role="page-edit"><span class="glyphicon glyphicon-cog" aria-hidden="true"></span> edit</a></li>'+
							'<li><a href="#" data-role="page-add"><span class="glyphicon glyphicon-plus" aria-hidden="true"></span> add</a></li>'+
							'<li><a href="#" data-role="page-remove"><span class="glyphicon glyphicon-trash" aria-hidden="true"></span> remove</a></li>'+
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
				
				self.draw(done);
				
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
		
		draw: function(callback){
			var self = this;
			
			this.$element.html(
				'<div class="db-content">'+
					'<div class="db-pages"></div>'+
				'</div>'
			);
			
			this.header.draw();
			
			this.gotoPage(this.pageIndex, callback);
			
		},
		
		gotoPage: function(pageIndex, callback){
			var self = this;
			
			if(pageIndex==='-') pageIndex = this.pageIndex - 1;
			if(pageIndex==='+') pageIndex = this.pageIndex + 1;
			
			if(pageIndex >= this.pages.length) pageIndex = this.pages.length - 1;
			if(pageIndex < 0) pageIndex = 0;
			
			this.pageIndex = pageIndex;
			
			UI.setUrl('dashboard',{
				index: this.pageIndex
			});
			
			this.currentPage().show(function(){
				if(typeof callback === 'function')
					callback.call(self);
			});
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
		
		editWidget: function(gridItem, callback){
			
			var self = this,
				widgetFactory = null,
				plugin = null,
				widgetType = null,
				editing = !!gridItem,
				device = null;
			
			
			var $html = $('<div>'+
			  '<div class="factory"></div>'+
			'</div>');
			
			
			function setWidgetType(newWidgetType){
				
				if(newWidgetType==='device'){
					setWidgetDevice(deviceSelect.value());
					return;
				}
				
				if(widgetType == newWidgetType) return; // the selection does not change !
				
				widgetType = newWidgetType;
				
				var $factory = $html.children('.factory').html('loading ...').data('widgetType',widgetType);
				
				$html.children('.description').remove();
				
				widgetFactory = null;
				plugin = null;
				
				WidgetCollection.load(widgetType)
					.done(function(w){
						if(widgetType != $factory.data('widgetType')) return;
						
						$factory.empty();
						plugin = w;
						
						var description = plugin.description;
						if(typeof description == 'function')
							description = description.call(plugin);
						if(description)
							$('<p class="description">').html(description).insertBefore($factory);
						
						if(typeof plugin.factory === 'undefined' || plugin.factory===null){
							// no conf
							widgetFactory = null;
						}
						else if(typeof plugin.factory == 'function'){
							widgetFactory = plugin.factory.call(plugin,$factory[0],editing ? gridItem.options : null);
						}
						else {
							widgetFactory = plugin.factory;
						}
					})
					.fail(function(e){
						if(widgetType != $factory.data('widgetType')) return;
						console.error(e);
						$factory.html((typeof e == 'object' && e !== null && typeof e.message == 'string') ? e.message : (e || 'error'));
					});
			}
			
			function setWidgetDevice(devId){
				
				if(typeof devId !== 'string') return;
				
				newWidgetType = 'device-'+devId;
				
				if(widgetType === newWidgetType) return; // the selection does not change !
				
				widgetType = newWidgetType;
				
				device = EThing.arbo.findOneById(devId);
				
				var $factory = $html.children('.factory').html('loading ...').data('widgetType',widgetType);
				
				$html.children('.description').remove();
				
				widgetFactory = null;
				plugin = null;
				
				WidgetCollection.loadFromDevice(device)
					.done(function(w){
						if(widgetType != $factory.data('widgetType')) return;
						
						$factory.empty();
						plugin = w;
						
						var description = plugin.description;
						if(typeof description == 'function')
							description = description.call(plugin);
						if(description)
							$('<p class="description">').html(description).insertBefore($factory);
						
						if(typeof plugin.factory === 'undefined' || plugin.factory===null){
							// no conf
							widgetFactory = null;
						}
						else if(typeof plugin.factory == 'function'){
							widgetFactory = plugin.factory.call(plugin,$factory[0],device, editing ? gridItem.options : null);
						}
						else {
							widgetFactory = plugin.factory;
						}
					})
					.fail(function(e){
						if(widgetType != $factory.data('widgetType')) return;
						console.error(e);
						$factory.html((typeof e == 'object' && e !== null && typeof e.message == 'string') ? e.message : (e || 'error'));
					});
			}
			
			var deviceSelect = new $.Form.ResourceSelect({
				filter: function(r){
					return r instanceof EThing.Device && WidgetCollection.getWidgetNameFromDevice(r);
				},
				readonly: editing,
				validators: [$.Form.validator.NotEmpty],
				onload: function(){
					if(editing){
						if(gridItem.device){
							this.value(gridItem.device);
							setWidgetDevice(gridItem.device);
						}
					}
					else {
						this.change(function(){
							setWidgetDevice(this.value());
						}).change();
					}
				},
				categorise: false,
				treeView: true
			});
			
			var select = new $.Form.Select({
					items: WidgetCollection.types,
					readonly: editing,
					onload: function(){
						if(editing){
							if(gridItem.type){
								this.value(gridItem.type);
								setWidgetType(gridItem.type);
							}
						}
						else {
							this.change(function(){
								setWidgetType(this.value());
							}).change();
						}
					}
				});
			
			
			
			$('<div>').prependTo($html).form(new $.Form.FormLayout({
				items:[{
					name: 'type',
					label: 'Type',
					item: select
				},{
					name: 'device',
					item: deviceSelect,
					dependencies: {
						'type': function(layoutItem){
							return this.getLayoutItemByName('type').item.value()==='device';
						}
					}
				}]
			}));
			
			
			
			$html.modal({
				title: editing ? 'Editing ...' : 'Create a widget',
				buttons: {
					'+Apply': function(){
						if(!plugin)
							return false;
						
						var opt, $this = $(this);
						
						if(widgetFactory===null){
							opt = {};
						} else if(typeof widgetFactory == 'function'){
							opt = widgetFactory.call(plugin);
						}
						else {
							opt = widgetFactory;
						}
						
						$.when(opt).done(function(options){
							if($.isPlainObject(options)){
								
								$this.modal('hide');
								
								if(editing){
									// replace
									gridItem.setWidget(/^device-/.test(widgetType) ? device : widgetType, options, callback);
									self.save();
								}
								else {
									var itemOpt = {
										options: options
									};
									/^device-/.test(widgetType) ? (itemOpt.device = device.id()) : (itemOpt.type = widgetType);
									self.currentPage().addDashboardItem(itemOpt, false, callback);
								}
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
				
				callback = $.proxy(callback, this);
				
				if(editing){
					page.setOptions(options, callback);
				} else {
					self.pages.push(Page($.extend({}, options, {
						dashboard: self
					})));
					self.gotoPage(self.pages.length-1, callback);
				}
				
				self.save();
			});
			
		},
		
		removePage: function(page, callback){
			for(var i in this.pages){
				if(page===this.pages[i]){
					this.pages.splice(i,1);
					page.destroy();
					this.gotoPage(this.pageIndex, callback);
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