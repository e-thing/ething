(function (factory) {
	// AMD.
	define(['jquery','ething','form', 'widget/base/Gauge', 'ui/datasource'], factory);
}(function ($, EThing, Form, Gauge) {
	
	
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
							acceptedMimeType: ['application/json', 'text/*', 'application/xml'],
							jsonPath: true,
							regexp: true,
							xpath: true,
							refreshPeriod: true
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
		
		instanciate: function(options){
			
			var resource = EThing.arbo.findOneById(options.source.resource || options.source.device);
			if(!resource){
				throw 'The resource does not exist anymore';
			}
			
			var title = resource.basename(), src,
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
				
				title += ' - '+options.source.operation;
				
				src = function(){
					return $.Form.DeviceRequest.makeRequest(options.source).then(function(data){
						return {
							value: data,
							date: new Date()
						};
					});
				}
			} else if(dataType === 'resource.data'){
				
				var key = options.source.data;
				
				title += ' - '+key;
				
				src = function(){
					return {
						value: resource.data(key),
						date: resource.modifiedDate()
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
					
					if(dataType === 'table.column' || dataType === 'resource.data'){
						this.onResourceUpdate = dataType === 'table.column' ? function(evt,updatedKeys){
							if(updatedKeys.indexOf('contentModifiedDate')!==-1) update();
						} : update;
						resource.on('updated', this.onResourceUpdate);
					} else if(dataType === 'device.request'){
						this.refeshIntervalId = setInterval(update, (options.refreshPeriod || 30)*1000);
					}
					
					update();
				},
				
				destroy: function(){
					gauge.destroy.call(this);
					
					if(this.onResourceUpdate){
						resource.off('updated', this.onResourceUpdate);
					}
					if(this.refeshIntervalId){
						clearInterval(this.refeshIntervalId);
					}
				}
				
			});
			
			
			
			return widget;
		}
	};
	
}));