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
			} else {
				// first number
				var i;
				for(i=0; i<keys.length; i++){
					if(typeof keys[i] === 'number'){
						data = data[keys[i]];
						break;
					}
				}
				if(i==keys.length) data = null; // not found
			}
		}
		
		data = parseFloat(data);
		
		return isNaN(data) ? null : {
			date: new Date(),
			value: data
		};
	};
	
	
	
	return {
		description: 'Create a gauge widget showing either the lastest data stored in a table or the data returned by a device !',
		
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
					name: 'minimum',
					item: new $.Form.Number({
						validators: [$.Form.validator.NotEmpty],
						value: 0
					})
				},{
					name: 'maximum',
					item: new $.Form.Number({
						validators: [$.Form.validator.NotEmpty],
						value: 100
					})
				},{
					name: 'unit',
					item: new $.Form.Text()
				},{
					name: 'significant digits',
					item: new $.Form.Number({
						validators: [$.Form.validator.Integer],
						minimum: 0,
						maximum: 8,
						value: 1
					})
				},{
					name: 'color',
					item: new $.Form.Color({
						value: '#307bbb'
					})
				}]
			}), preset);
			
			return function(){
				return form.submit();
			}
		},
		
		require: ['widget/Gauge'],
		
		instanciate: function(options, Gauge){
			
			var resource = EThing.arbo.findOneById(options.source.resource || options.source.device);
			if(!resource){
				throw 'The resource does not exist anymore';
			}
			
			var title = resource.basename(), serieName, src,
				dataType = (options.source.type || '');
			
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
			
			var update = function(){
				$.when(src()).done(function(d){
				
					if(!d){
						return;
					}
					
					widget.val(d.value);
					widget.setFooter(d.date ? d.date.toLocaleString() : '');
				
				});
			};
			
			
			
			
			var gauge = Gauge({
				minimum : options.minimum,
				maximum : options.maximum,
				unit : options.unit,
				color : options.color,
				title : title
			});
			
			var widget = $.extend({}, gauge, {
				
				draw: function(){
					gauge.draw.call(this);
					resource.on('updated', update);
					update();
				},
				
				destroy: function(){
					gauge.destroy.call(this);
					resource.off('updated', update);
				}
				
			});
			
			
			
			return widget;
		}
	};
	
}));