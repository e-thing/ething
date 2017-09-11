(function (factory) {
	// AMD.
	define(['jquery','ething','form','ui/resourceselect'], factory);
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
		
		require: ['widget/Label'],
		
		instanciate: function(options, Label){
			
			
			var resource = EThing.arbo.findOneById(options.resource);
			if(!resource){
				throw 'The resource does not exist anymore';
			}
			
			var title = resource.basename(), src = null;
			
			if(resource instanceof EThing.Table){
				
				title += ' - '+options.key;
				
				src = function(){
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
				
				src = function(){
					return resource.execute(options.operation, options.parameters).then(function(data){
						return parseData(data);
					});
				}
			}
			
			var unit = (options.unit || '').trim();
			
			
			
			var update = function(){
		
				$.when(src()).done(function(d){
				
					if(!d){
						return;
					}
					
					var str = d.value;
					if(unit) str += ' '+unit;
					widget.val(str);
					widget.setFooter(d.date ? d.date.toLocaleString() : '');
				
				});
			};
			
			
			var label = Label({
				color : options.color,
				title : title
			});
			
			var widget = $.extend({}, label, {
				
				draw: function(){
					label.draw.call(this);
					resource.on('updated', update);
					update();
				},
				
				destroy: function(){
					label.destroy.call(this);
					resource.off('updated', update);
				}
				
			});
			
			
			
			return widget;
		}
	};
	
}));