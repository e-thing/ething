(function (root, factory) {
    if (typeof define === 'function' && define.amd) {
        // AMD. Register as an anonymous module.
		define(['jquery', 'ui/event', 'jquery.gridster'], factory);
    }
}(this, function ($, EventEngine) {
	
	
	
	var GridItem = function(opt){
		
		var self = {
			x: opt.x || null,
			y: opt.y || null,
			width: opt.width || 1,
			height: opt.height || 1,
			
			widget: opt.widget || null,
			
			grid: opt.grid,
			
			removable: typeof opt.removable != 'undefined' ? opt.removable : true,
			
			actions: opt.actions || [],
			
			$gridItem: $('<div>')
		};
		
		var drawn = false;
		
		EventEngine(self);
		
		return $.extend(self, {
			
			
			setWidget: function(widget){
				
				if(self.widget){
					self.removeWidget();
				}
				
				self.widget = widget
				
				self.draw();
				
				self.trigger('updated', [self]);
			},
			
			draw: function(){
				
				var self = this;
				
				if(!drawn){
					
					drawn = true;
					
					var $gridItem = this.$gridItem;
					
					$gridItem.children('.db-widget-wrapper').remove();
					
					var $wrapper = $('<div>').addClass('db-widget-wrapper');
					
					var $btns = [];
					
					//btns.push('<button class="btn btn-link gs-drag-handle" data-name="move"><span class="glyphicon glyphicon-move" aria-hidden="true"></span></button>');
					
					var defaultActions = [];
					
					if(this.removable){
						defaultActions.push({
							name: 'remove',
							icon: 'trash',
							fn: function(){
								self.grid.removeWidget(self);
							}
						});
					}
					
					var actions = [].concat(this.actions || [], defaultActions)
					
					$btns = actions.map(function(action){
						
						var $btn = null;
						
						if(action.render){
							$btn = action.render();
						} else {
						
							var $btn = $('<button class="btn btn-link"></button>');
							
							if(action.icon) {
								$btn.prepend('<span class="glyphicon glyphicon-'+action.icon+'" aria-hidden="true">');
							} else {
								$btn.text(action.name);
							}
						}
						
						if(action.fn){
							$btn.click(function(){
								action.fn.call(self);
							});
						}
						
						return $btn;
						
					}, this);
					
					var $widgetEdit = $('<div>').addClass('db-widget-edit').html('<div><div class="btn-group btn-group-xs"></div></div>');
					
					$widgetEdit.find('.btn-group').append($btns);
					
					$wrapper.append($widgetEdit, '<div class="db-widget-err">').appendTo($gridItem);
					
					$gridItem.data('gridItem',self);
					
				}
				
				self.widget.$element.addClass('db-widget-type-'+name.replace('/','-'));
				self.$gridItem.find('.db-widget-wrapper').prepend(self.widget.$element);
				self.widget.draw();
				
				
			},
			
			destroy: function(){
				this.removeWidget();
				this.$gridItem.empty();
				drawn = false;
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
			
			setError: function(err, showremoveBtn){
				
				if(err===false){
					this.$gridItem.find('.db-widget-err').hide();
					return this;
				}
				console.error(err);
				
				var $html = $('<p><span class="glyphicon glyphicon-warning-sign" aria-hidden="true"></span><br>'+((typeof err == 'object' && err !== null && typeof err.message == 'string') ? err.message : (err || 'error'))+'</p>');
				
				if(showremoveBtn && this.removable){
					var self = this;
					$('<button class="btn btn-link">remove</button>').click(function(){
						self.grid.removeWidget(self);
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
	
	
	
	var Grid = function(opt){
		
		var self = {
			
			gridItems: [],
			
			grid: null, // the grid instance
			
			$element: opt.$element || $('<div>'),
			
			columns: opt.columns || 8,
			
			id: opt.id || 'grid-'+Math.round(Math.random()*100000)
			
		};
		
		
		EventEngine(self);
		
		return $.extend(self, {
			
			addWidget: function(widget, options){
				
				var self = this;
				
				options = options || {};
				
				var actions = options.actions || [];
				
				var gridItem = GridItem({
					grid: this,
					widget: widget,
					actions: actions,
					removable: options.removable,
					x: options.x,
					y: options.y,
					width: options.width,
					height: options.height
				});
				
				this.gridItems.push(gridItem);
				
				if(this.grid){
					// add this item to the grid
					this.grid.add_widget(gridItem.$gridItem, gridItem.width, gridItem.height, gridItem.x, gridItem.y, null, null, function(){
						if(self.grid)
							gridItem.draw();
					});
				}
				
				this.update();
				
				this.trigger('gridItemAdded', [gridItem]);
				
				return gridItem;
			},
			
			removeWidget: function(item, nodestroy){
				
				var gi = null;
				
				for(var i in this.gridItems){
					if(this.gridItems[i].widget === item || this.gridItems[i] === item){
						gi = i;
						break;
					}
				}
				
				if(gi===null) return;
				
				var gridItem = this.gridItems[gi];
				
				if(!nodestroy) this.gridItems.splice(gi, 1)[0];
				
				// remove this item from the grid
				if(gridItem.$gridItem) this.grid.remove_widget(gridItem.$gridItem);
				
				gridItem.destroy();
				
				this.update();
				
				if(!nodestroy) this.trigger('gridItemRemoved');
				
			},
			
			setOptions: function(opt){
				
				var redraw = false;
				
				if(opt.columns != this.columns){
					redraw = true;
					this.columns = opt.columns;
				}
					
				if(redraw){
					this.redraw();
					//this.destroy();
					//this.draw();
				}
			},
			
			draw: function(){
				
				var self = this;
				
				this.$element.attr('id', this.id).addClass('db-page').html(
					'<div class="text-center db-page-empty">'+
						'<p>Your dashboard is empty !</p>'+
					'</div>'+
					'<div class="gridster">'+
						'<div></div>'+
					'</div>'
				);
				
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
							var timeoutId = setTimeout(function(){self.saveLayout();self.trigger('gridLayoutChanged');}, 500);
						},
						handle: '.db-widget-edit *'
					},
					resize: {
						enabled: true,
						stop: function(e, ui, $widget){
							if(timeoutId!==null) clearTimeout(timeoutId);
							var timeoutId = setTimeout(function(){self.saveLayout();self.trigger('gridLayoutChanged');}, 500);
							
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
				
				this.gridItems.forEach(function(gridItem){
					// add this item to the grid
					gridItem.$gridItem.data('gridItem', gridItem);
					
					this.grid.add_widget(gridItem.$gridItem, gridItem.width, gridItem.height, gridItem.x, gridItem.y, null, null, function(){});
					
				}, this);
				
				this.update();
				
				this.grid.recalculate_faux_grid();
				
			},
			
			saveLayout: function(force){
				
				var widgetPositions = this.grid.serialize();
				
				widgetPositions.forEach(function(widgetPos){
					var gridItem = widgetPos.$el.data('gridItem');
					
					gridItem.x = widgetPos.col;
					gridItem.y = widgetPos.row;
					gridItem.width = widgetPos.width;
					gridItem.height = widgetPos.height;
				});
			},
			
			redraw: function(){
				
				if(this.grid){
					this.grid.destroy();
					this.grid = null;
				}
				
				this.draw();
				
			},
			
			update: function(){
				if(this.$element) this.$element.find('.db-page-empty').toggle(this.gridItems.length==0);
			},
			
			destroy: function(){
				
				[].concat(this.gridItems).forEach(function(gridItem){
					this.removeWidget(gridItem, true);
				}, this);
				
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
	
	
	return Grid;
	
	
}))