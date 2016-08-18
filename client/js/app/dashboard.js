(function(){
	
	
	Header.setMobileTitle('Dashboard');
	
	
	

	var cachedWidgetPluginObject = {};
	
	
	
	
	
	
	var Dashboard = {
		
		widgetTypes: ['video','image','button','label','chart','gauge','map'],
		
		configFilename : '.dashboard.json',
		
		options: null,
		
		file: null,
		
		$element: null,
		
		loadWidgetPlugin: function(widgetType){
			var dfr = $.Deferred();
			
			if(cachedWidgetPluginObject.hasOwnProperty(widgetType)){
				$
					.when(cachedWidgetPluginObject[widgetType])
					.done(function(plugin){
						dfr.resolve(plugin);
					})
					.fail(function(e){
						dfr.reject(e);
					});
			}
			else {
				cachedWidgetPluginObject[widgetType] = dfr;
				$.ajax({
					url: 'widgets/'+widgetType+'.js',
					dataType: "text"
				}).done(function(data){
					var plugin = eval(data);
					if(plugin){
						
						$.extend(true,plugin,{
							type: widgetType
						});
						
						// load the dependencies
						EThing.utils.require({
							url: plugin.require,
							base: 'widgets'
						}).done(function(){
							cachedWidgetPluginObject[widgetType] = plugin;
							dfr.resolve(plugin);
						}).fail(function(){
							dfr.reject('dependency error');
						});
					}
					else
						dfr.reject('invalid widget plugin "'+widgetType+'"');
				}).fail(function(){
					dfr.reject('widget plugin "'+widgetType+'" not found');
				});
			}
			
			return dfr.promise();
		},
		
		load: function(element){
			
			var options = {}, self = this;
			
			this.$element = $(element);
			
			
			// prepare the dom
			this.$element.addClass('db container-fluid').html(
				'<p class="db-info text-center">'+
					'loading ...'+
				'</p>'
			);
			
			
			var readConfig = function(){
				self.file.read().done(function(opt){
					
					// try to decode json string
					if(typeof opt == 'string')
						try{
							options = JSON.parse(opt);
						}
						catch(e){}
					else
						options = opt;
					
					init();
				});
			}
			
			var init = function(){
				self.options = $.extend(true,{
					widgets:[]
				},options);
				
				self.updateDom();
			}
			
			if(self.file)
				readConfig();
			else
				EThing.list('name == "'+self.configFilename+'" AND type == "File"').done(function(files){
					if(files.length){
						self.file = files[0];
						readConfig();
					}
					else
						init();
				});
			
		},
		
		updateDom: function(){
			var self = this;
			
			if(this.options.widgets.length){
				this.$element.html(
					'<div class="db-header">'+
						'<button class="btn btn-default db-header-add-btn"><span class="glyphicon glyphicon-plus" aria-hidden="true"></span> Add Widget</button>'+
					'</div>'+
					'<div class="db-widgets row"></div>'
				);
				
				var $widgets = this.$element.find('.db-widgets');
				this.options.widgets.forEach(function(widget){
					$widgets.append(
						this.drawWidget(widget.type,widget.options)
					);
				},this);
				
			} else {
				// empty
				
				this.$element.html(
					'<div class="db-info jumbotron text-center">'+
						'<p>'+
							'No widget set :-('+
						'</p>'+
						'<p>'+
							'<button class="btn btn-primary  db-header-add-btn"><span class="glyphicon glyphicon-plus" aria-hidden="true"></span> Add Widget</button>'+
						'</p>'+
					'</div>'
				);
			}
			
			this.$element.find('.db-header-add-btn').click(function(){
				self.editWidget();
			});
		},
		
		save: function(){
			var self = this;
			
			function save(){
				self.file.write( JSON.stringify(self.options, null, 4) );
			}
			
			if(self.file)
				save();
			else {
				EThing.File.create({
					name: self.configFilename
				}).done(function(file){
					self.file = file;
					save();
				})
			}
		},
		
		addWidget: function(widgetType, widgetOptions){
			var self = this;
			
			this.options.widgets.push({
				type: widgetType,
				options: widgetOptions
			});
			
			this.save();
			
			if(this.options.widgets.length<=1)
				this.updateDom();
			else
				this.$element.find('.db-widgets').append(
					this.drawWidget(widgetType, widgetOptions)
				);
		},
		
		drawWidget: function(widgetType, widgetOptions){
			
			var self = this;
			
			var $widget = $('<div>').addClass('db-widget').addClass('db-widget-type-'+widgetType);
			
			var $widgetEdit = $('<div>').addClass('db-widget-edit')
				.html('<div class="btn-group">'+
					'<button class="btn btn-default btn-xs" data-name="up"><span class="glyphicon glyphicon-plus" aria-hidden="true"></span></button> '+
					'<button class="btn btn-default btn-xs" data-name="down"><span class="glyphicon glyphicon-minus" aria-hidden="true"></span></button> '+
					'<button class="btn btn-default btn-xs" data-name="edit"><span class="glyphicon glyphicon-edit" aria-hidden="true"></span></button> '+
					'<button class="btn btn-default btn-xs" data-name="remove"><span class="glyphicon glyphicon-trash" aria-hidden="true"></span></button>'+
				'</div>');
			
			$widgetEdit.find('button[data-name="up"]').click(function(){
				var $widgetBox = $(this).closest('.db-widget-box'), index = $widgetBox.index();
				if(index>0){
					var w = self.options.widgets[index];
					self.options.widgets[index] = self.options.widgets[index-1];
					self.options.widgets[index-1] = w;
					
					self.save();
					
					$widgetBox.insertBefore($widgetBox.prev());
				}
			});
			
			$widgetEdit.find('button[data-name="down"]').click(function(){
				var $widgetBox = $(this).closest('.db-widget-box'), index = $widgetBox.index();
				if(index<self.options.widgets.length-1){
					var w = self.options.widgets[index];
					self.options.widgets[index] = self.options.widgets[index+1];
					self.options.widgets[index+1] = w;
					
					self.save();
					
					$widgetBox.insertAfter($widgetBox.next());
				}
			});
			
			$widgetEdit.find('button[data-name="edit"]').click(function(){
				var $widgetBox = $(this).closest('.db-widget-box'), index = $widgetBox.index();
				self.editWidget(index);
			});
			
			$widgetEdit.find('button[data-name="remove"]').click(function(){
				var $widgetBox = $(this).closest('.db-widget-box'), index = $widgetBox.index();
				
				self.options.widgets.splice(index,1);
				
				self.save();
				
				$widgetBox.remove();
				
				if(!self.options.widgets.length){
					self.updateDom();
				}
			});
			
			
			this.loadWidgetPlugin(widgetType)
				.done(function(plugin){
					if(typeof plugin.instanciate == 'function'){
						try{
							plugin.instanciate.call(plugin, $widget, widgetOptions);
						}
						catch(e){}
					}
					else
						$widget.html('error');
				})
				.fail(function(error){
					$widget.html(error);
				});
			
			var $w = $('<div>').addClass('db-widget-box col-xs-12 col-sm-6 col-lg-4')
				.append(
					$('<div>').addClass('db-widget-ctnr').append($widget),
					$widgetEdit
				);
			
			if(!EThing.utils.isTouchDevice){
				$w.hover(function(){
					$widgetEdit.css('visibility', 'visible');
				}, function(){
					$widgetEdit.css('visibility', 'hidden');
				});
				$widgetEdit.css('visibility', 'hidden');
			}
			return $w;
		},
		
		editWidget: function(index){
			
			var self = this, widget;
			
			if(typeof index == 'number'){
				widget = self.options.widgets[index];
			}
			
			var $html = $('<div>'+
			  '<div class="form-group">'+
				'<label>Type</label>'+
				'<select class="form-control"></select>'+
			  '</div>'+
			  '<div class="factory"></div>'+
			'</div>');
			
			var widgetFactory = null, plugin = null;
			
			var $selectWidgetType = $html.find('select').change(function(){
				var $this = $(this),
					widgetType = $this.val(),
					$factory = $html.children('.factory').html('loading ...');
				
				widgetFactory = null;
				plugin = null;
				
				self.loadWidgetPlugin(widgetType)
					.done(function(w){
						$factory.empty();
						plugin = w;
						if(typeof plugin.factory == 'function'){
							widgetFactory = plugin.factory.call(plugin,$factory[0],widget ? widget.options : null);
						}
						else {
							widgetFactory = plugin.factory;
						}
					})
					.fail(function(){
						$factory.html('error');
					});
			});
			
			if(widget)
				$selectWidgetType.append('<option>'+widget.type+'</option>').prop('disabled',true);
			else
				self.widgetTypes.forEach(function(type){
					$selectWidgetType.append('<option>'+type+'</option>');
				})
			
			
			$html.modal({
				title: widget ? 'Editing ...' : 'Add a new widget ...',
				buttons: {
					'+Apply': function(){
						if(!plugin)
							return false;
						
						var opt, $this = $(this);
						
						if(typeof widgetFactory == 'function'){
							opt = widgetFactory.call(plugin);
						}
						else {
							opt = widgetFactory;
						}
						
						$.when(opt).done(function(options){
							$this.modal('hide');
							
							if(widget){
								widget.options = options;
								
								self.save();
								
								self.$element.find('.db-widgets').children().eq(index).replaceWith(
									self.drawWidget(plugin.type, options)
								);
							}
							else
								self.addWidget(plugin.type, options);
						})
						
						return false;
					},
					'Cancel': null
				}
			});
			
			$selectWidgetType.trigger('change');
			
		}
		
	};
	
	
	
	window.main = function() {
		
		Dashboard.load('#dashboard');
		
	};
	
})()