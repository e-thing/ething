(function (factory) {
	// AMD.
	define(['jquery','ething','form','resourceselect'], factory);
}(function ($, EThing, Form) {
	
	var parseData = function(data){
		if(Array.isArray(data))
			data = data[data.length-1];
		
		if($.isPlainObject(data)){
			
			var keys = Object.keys(data);
			if(keys.length === 1){
				data = data[keys[0]];
			} else if(keys.indexOf('value')!==-1) {
				data = data['value'];
			} else if(keys.indexOf('y')!==-1) {
				data = data['y'];
			} else if(keys.indexOf('data')!==-1) {
				data = data['data'];
			}
		}
		
		return data;
	};
	
	var Label = function(widget){
		
		var self = this;
		
		var options = $.extend(true,{
			unit: null
		}, widget.options);
		
		var $element = this.$element = widget.$element;
		
		$element.on('resize', function(){
			self.resize();
		});
		
		$element.css({
			'position': 'relative',
			'font-size': '14px',
			'text-align': 'center',
			'color': '#6B6B6B',
			'height': '100%',
			'padding': '10px 0 0 0',
			'color': 'rgb(179, 179, 179)'
		});
		
		var resource = EThing.arbo.findOneById(options.resource);
		if(!resource){
			widget.setError('The resource does not exist anymore');
		}
		
		var title = resource.basename(), serieName;
		
		if(resource instanceof EThing.Table){
			
			title += ' - '+options.key;
			
			this.src = function(){
				return resource.select({
					fields: ['date',options.key],
					length: 1,
					start: -1
				}).then(function(data){
					return data.length ? {
						date: new Date(data[0]['date']),
						value: data[0][options.key]
					} : null;
				});
			};
		} else if(resource instanceof EThing.Device){
			
			title += ' - '+options.operation;
			
			this.src = function(){
				return resource.execute(options.operation, options.parameters).then(function(data){
					return parseData(data);
				});
			}
		}
		
		var unit = (options.unit || '').trim();
		
		$element.empty().append('<div class="title">'+title+'</div>', '<div class="content"><span class="value">-</span><span class="unit">'+unit+'</span></div>', '<div class="update">-</div>');
		
		$element.find('.content').css({
			'font-size': '32px',
			'width': '100%',
			'white-space': 'nowrap',
			'text-overflow': 'ellipsis',
			'overflow': 'hidden',
			'color': '#307bbb'
		});
		
		$element.find('.unit').css({
			'color': '#9C9C9C',
			'font-size': '24px'
		});
		
		this.src().done(function(d){
			
			if(!d){
				widget.setError('invalid data');
				return;
			}
			
			$element.find('.value').text(d.value);
			
			$element.find('.update').text(d.date.toLocaleString());
		
		}).fail(function(){
			widget.setError('invalid data');
		});
		
	}
	
	Label.prototype.resize = function(){
		
		var availableHeight = this.$element.height() - this.$element.find('.title').height() - this.$element.find('.update').height();
		var height = this.$element.find('.content').height();
		var verticalMargin = availableHeight - height;
		this.$element.find('.content').css({
			'margin-top': (verticalMargin/2)+'px',
			'margin-bottom': (verticalMargin/2)+'px'
		});
		
	};
	
	
	return {
		description: 'Draw a label containing either the lastest data stored in a table or the data returned by a device !',
		
		// must return a function which returns an options object
		factory: function(container, preset){
			var form = new $.Form(container,new $.Form.FormLayout({
				items:[{
					name: 'resource',
					item: new $.Form.ResourceSelect({
						filter: function(r){
							return r instanceof EThing.Table || r instanceof EThing.Device;
						},
						validators: [$.Form.validator.NotEmpty]
					})
				},{
					name: 'key',
					item: new $.Form.Text({
						validators: [$.Form.validator.NotEmpty],
					}),
					dependencies: {
						'resource': function(layoutItem){
							var r = EThing.arbo.findOneById(this.getLayoutItemByName('resource').item.value());
							layoutItem.item.setComboboxValues( r instanceof EThing.Table ? r.keys() : []);
							return r instanceof EThing.Table;
						}
					}
				},{
					name: 'operation',
					item: new $.Form.Select(),
					dependencies: {
						'resource': function(layoutItem){
							var r = EThing.arbo.findOneById(this.getLayoutItemByName('resource').item.value());
							layoutItem.item.setOptions( r instanceof EThing.Device ? r.operations() : []);
							return r instanceof EThing.Device;
						}
					}
				},{
					name: 'unit',
					item: new $.Form.Text()
				}],
				onload: function(){
					
					var self = this;
					var resourceForm = this.getLayoutItemByName('resource').item;
					var operationForm = this.getLayoutItemByName('operation').item;
					var id = 0;
					
					function update(){
						
						var resource = EThing.arbo.findOneById(resourceForm.value());
						var operation = operationForm.value();
						var id_ = ++id;
						
						self.removeItem('parameters');
						
						if(resource instanceof EThing.Device && operation){
							
							// get the json schema specification for this operation
							resource.getApi(operation).done(function(api){
								
								if(api.schema && id_ === id){
									
									var layoutitem = self.addItem({
										name: 'parameters',
										item: Form.fromJsonSchema(api.schema)
									},3);
									
									if(preset && preset.operation === operation){
										layoutitem.item.value(preset.parameters);
									}
								}
								
							});
							
						}
						
					}
					
					operationForm.change(update);
					resourceForm.change(update).change();
					
				}
			}), preset);
			
			return function(){
				return form.submit();
			}
		},
		
		instanciate: function(widget){
			new Label(widget);
		}
	};
	
}));