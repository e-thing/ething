(function (factory) {
	// AMD.
	define(['jquery','ething','form','ui/datasource'], factory);
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
					name: 'source',
					item: new $.Form.DataSource({
						tableColumn: true,
						deviceRequest: {
							acceptedMimeType: ['application/json', 'text/*']
						},
						resourceData: true
					})
				},{
					name: 'unit',
					item: new $.Form.Text()
				}]
			}), preset);
			
			return function(){
				return form.submit();
			}
		},
		
		require: ['widget/Label'],
		
		instanciate: function(options, Label){
			
			
			var resource = EThing.arbo.findOneById(options.source.resource || options.source.device);
			if(!resource){
				throw 'The resource does not exist anymore';
			}
			
			var title = resource.basename(), src = null;
			var dataType = (options.source.type || '');
			
			if(dataType === 'table.column'){
				
				var key = options.source.column;
				
				title += ' - '+key;
				
				src = function(){
					return resource.select({
						fields: ['date',key],
						length: 1,
						start: -1
					}).then(function(data){
						return data.length ? {
							date: new Date(data[0]['date']),
							value: data[0][key]
						} : null;
					});
				};
			} else if(dataType === 'device.request'){
				
				var operation = options.source.operation;
				var parameters = options.source.parameters || null;
				
				title += ' - '+operation;
				
				src = function(){
					return resource.execute(operation, parameters).then(function(data){
						return parseData(data);
					});
				}
			} else if(dataType === 'resource.data'){
				
				var key = options.source.data;
				
				title += ' - '+key;
				
				src = function(){
					return {
						value: resource.data(key)
					};
				}
			} else {
				src = function(){
					return false;
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