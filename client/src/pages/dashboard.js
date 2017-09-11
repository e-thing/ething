(function (root, factory) {
    if (typeof define === 'function' && define.amd) {
        // AMD. Register as an anonymous module.
        define(['ui/core', 'jquery', 'ething', 'widgetcollection', 'css!./dashboard', 'form', 'ui/resourceselect', 'ui/modal', 'jquery.gridster'], factory);
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
			
			grid: opt.grid,
			widget: null
		};
		
		var $gridItem = $('<div>').data('gridItem',self);
		
		
		var dashboard = opt.dashboard;
		
		var onRemove = opt.onRemove;
		
		
		return $.extend(self, {
			
			// remove this item from the grid !
			remove: function(){
				
				this.removeWidget();
				
				// remove this widget from the grid
				self.grid.remove_widget($gridItem);
				
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
				return self.load(callback);
			},
				
			load: function(callback){
				if(self.widget){
					self.removeWidget();
				}
				
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
				
				
				// add this widget to the grid
				self.grid.add_widget($gridItem, self.width, self.height, self.x, self.y, null, null, function(){
					
				});
				
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
					$wrapper.prepend(widget.$element);
					widget.draw();
					
				}).always(callback).fail(function(err){
					self.setError(err, true);
				});
				
			},
			
			removeWidget: function(){
				// destroy the widget only, but not the grid item
				if(self.widget) {
					self.widget.destroy();
					$gridItem.empty();
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
					$gridItem.find('.db-widget-err').hide();
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
				
				$gridItem
					.find('.db-widget-err')
					.html($html)
					.show();
				return this;
			}
			
		});
		
	}
	
	
	
	// dashboard module :
	
	var Dashboard = {
		
		configFilename : '.dashboard.json',
		
		options: {},
		
		file: null,
		
		$element: null,
		
		gridItems: [],
		
		grid: null,
		
		
		
		load: function(element, callback){
			
			var self = this;
			
			function done(){
				
				var resizeTimeout = null;
				
				$(window).on('resize.dashboard',function(e){
					if(e.target !== window) return;
					
					if(resizeTimeout!==null) clearTimeout(resizeTimeout);
					resizeTimeout = setTimeout(function(){
						Dashboard.resize();
					}, 500);
				});
				
				if(typeof callback === 'function')
					callback.call(self);
				
			}
			
			this.gridItems = [];
			this.options = {
				widgets:[]
			};
			
			this.$element = $(element);
			
			
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
					
					self.draw(done);
				});
			}
			else {
				// no dashboard file found !
				self.draw(done);
			}
			
			
			
		},
		
		update: function(){
			this.$element.children('.db-content').toggle(!!this.gridItems.length);
			this.$element.children('.db-init').toggle(!this.gridItems.length);
		},
		
		draw: function(callback){
			var self = this;
			
			this.$element.html(
				'<div class="db-content">'+
					'<div class="db-header">'+
						'<button class="btn btn-link db-header-add-btn"><span class="glyphicon glyphicon-plus" aria-hidden="true"></span> Add Widget</button>'+
						'<button class="btn btn-link db-header-edit-btn"><span class="glyphicon glyphicon-cog" aria-hidden="true"></span> toggle editing</button>'+
					'</div>'+
					'<div class="gridster"><div></div></div>'+
				'</div>'+
				'<div class="db-init jumbotron text-center">'+
					'<p>'+
						'No widget :-('+
					'</p>'+
					'<p>'+
						'<button class="btn btn-primary  db-header-add-btn"><span class="glyphicon glyphicon-plus" aria-hidden="true"></span> Add Widget</button>'+
					'</p>'+
					'<p>'+
						'<img src="images/dashboard-overview.png">'+
					'</p>'+
				'</div>'
			);
			
			this.$element.find('.db-header-edit-btn').click(function(){
				self.setEditMode(!self.isEditMode());
			});
			
			this.$element.find('.db-header-add-btn').click(function(){
				self.createWidget();
			});
			
			
			var timeoutId = null;
			
			// create the grid
			var $grid = this.$element.find('.gridster > div').gridster({
				autogenerate_stylesheet: true,
				widget_margins: [10, 10],
				/*widget_base_dimensions: ['auto', 240],
				min_cols: 4,
				max_cols: 4,*/
				widget_base_dimensions: ['auto', 160],
				min_cols: 8,
				max_cols: 8,
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
				
				widget_selector: 'div'
			});
			
			this.grid = $grid.data('gridster');
			
			var dfrs = [];
			this.options.widgets.forEach(function(item){
				
				var dfr = $.Deferred();
				var gridItem = this.addDashboardItem(item, true, function(){
					dfr.resolve();
				});
				dfrs.push(dfr);
			},this);
			
			
			this.update();
			
			$.when.apply($, dfrs).done(function(){
				if(typeof callback === 'function')
					callback.call(self);
			});
			
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
				
				var options = $.extend({}, this.options, {widgets:[]});
				
				this.gridItems.forEach(function(gridItem){
					options.widgets.push(gridItem.serialize());
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
		
		resize: function(){
			this.gridItems.forEach(function(gridItem){
				gridItem.resize();
			});
		},
		
		addDashboardItem: function(item, noSave, callback){
			var self = this;
			
			var gridItem = GridItem($.extend({
				dashboard: this,
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
			
			self.gridItems.push(gridItem);
			
			gridItem.load(callback);
			
			if(!noSave){
				self.save();
			}
			
			self.update();
			
			return gridItem;
			
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
									self.addDashboardItem(itemOpt, false, callback);
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
		destroy: function(){
			
			$(window).off('resize.dashboard');
			
			this.gridItems.forEach(function(gridItem){
				gridItem.removeWidget();
			});
			
			if(this.grid)
				this.grid.destroy();
			
			this.$element.empty();
		}
		
	};
	
	return {
		
		buildView: function(){
			UI.Container.set('<div>');
			
			Dashboard.load('#dashboard > .ui-container');
		},
		
		deleteView: function(){
			Dashboard.destroy();
		}
		
	};
}));