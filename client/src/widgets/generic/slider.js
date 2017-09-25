(function (factory) {
	// AMD.
	define(['jquery','ething','form','ui/resourceselect','ui/devicerequest', 'ui/resourcedataselect'], factory);
}(function ($, EThing, Form) {
	
	
	
	return {
		description: '', // todo
		
		// must return a function which returns an options object
		factory: function(container, preset){
			
			var form = new $.Form(container,new $.Form.FormLayout({
				items:[{
					name: 'resource',
					item: new $.Form.ResourceSelect({
						name: '#resource',
						validators: [$.Form.validator.NotEmpty]
					})
				},{
					name: 'getter',
					item: new $.Form.SelectPanels({
						items: [{
							name: 'device.request',
							label: 'get the data from a device\'s request',
							item: new $.Form.DeviceRequest({
								deviceForm: '#resource',
								acceptedMimeType: ['application/json'],
								jsonPath: true,
								regexp: true,
								xpath: true,
								refreshPeriod: true
							})
						},{
							name: 'resource.data',
							label: 'get the data from a resource\'s internal data',
							item: new Form.ResourceDataSelect({
								resourceForm: '#resource'
							})
						}],
						format: $.Form.SelectPanels.format.Merge,
						validators: [$.Form.validator.NotEmpty]
					}),
					dependencies: {
						'resource': function(layoutItem){
							var r = EThing.arbo.findOneById(this.getLayoutItemByName('resource').item.value());
							layoutItem.item.setEnable('device.request', r instanceof EThing.Device);
							return r instanceof EThing.Resource;
						}
					}
				},{
					name: 'setter',
					item: new $.Form.SelectPanels({
						items: [{
							name: 'device.request',
							label: 'get the data from a device\'s request',
							item: new $.Form.DeviceRequest({
								deviceForm: '#resource',
								onApiCall: function(device, operation, api){
									if(!(Array.isArray(api.required) && api.required.length===1 && api.parameters[0].type === 'number'))
										throw 'only methods with an unique argument of type number is allowed.';
								}
							})
						},{
							name: 'resource.data',
							label: 'get the data from a resource\'s internal data',
							item: new Form.ResourceDataSelect({
								resourceForm: '#resource'
							})
						}],
						format: $.Form.SelectPanels.format.Merge,
						validators: [$.Form.validator.NotEmpty]
					}),
					dependencies: {
						'resource': function(layoutItem){
							var r = EThing.arbo.findOneById(this.getLayoutItemByName('resource').item.value());
							layoutItem.item.setEnable('device.request', r instanceof EThing.Device);
							return r instanceof EThing.Resource;
						}
					}
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
					name: 'title',
					item: new $.Form.Text()
				}]
			}), preset);
			
			return function(){
				return form.submit();
			}
		},
		
		require: ['widget/Widget', '//cdnjs.cloudflare.com/ajax/libs/noUiSlider/10.1.0/nouislider.min.js', 'css!//cdnjs.cloudflare.com/ajax/libs/noUiSlider/10.1.0/nouislider.min'],
		
		instanciate: function(options, Widget, noUiSlider){
			
			
			
			var minIntervalMs = 500;
			var timeoutId = null;
			var lastExecute = null;
			
			function temporizedSet(setFn, self){
				
				var delay = 0;
				var diff = lastExecute ? (Date.now() - lastExecute) : (minIntervalMs + 1);
				
				if(timeoutId) clearTimeout(timeoutId);
				
				if(diff < minIntervalMs){
					delay = minIntervalMs - diff;
				}
				
				var args = Array.prototype.slice.call(arguments);
				args.shift();
				args.shift();
				self = self || this;
				
				timeoutId = setTimeout(function(){
					lastExecute = Date.now();
					
					if(typeof setFn === 'function')
						setFn.apply(self, args);
					
				}, delay);
				
			}
			
			
			var resource = EThing.arbo.findOneById(options.resource);
			if(!resource){
				throw 'The resource does not exist anymore';
			}
			
			var getter_exe;
			var dataType = (options.getter.type || '');
			
			if(dataType === 'table.column'){
				
				var key = options.getter.column;
				
				getter_exe = function(){
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
				
				getter_exe = function(){
					return $.Form.DeviceRequest.makeRequest(options.source).then(function(data){
						return {
							value: data,
							date: new Date()
						};
					});
				}
				
			} else if(dataType === 'resource.data'){
				
				var key = options.getter.data;
				
				getter_exe = function(){
					return {
						value: resource.data(key),
						date: resource.modifiedDate()
					};
				}
			} else {
				getter_exe = function(){
					return false;
				}
			}
			
			var setter_exe;
			dataType = (options.setter.type || '');
			
			if(dataType === 'device.request'){
				
				var operation = options.setter.operation;
				var parameters = options.setter.parameters || null;
				
				setter_exe = function(value){
					return resource.execute(operation, value);
				}
			} else if(dataType === 'resource.data'){
				
				var key = options.setter.data;
				
				setter_exe = function(value){
					return resource.setData(key, value);
				}
			} else {
				setter_exe = function(v){}
			}
			
			
			var widget = Widget({
				title: options.title || null
			});
			
			return $.extend({}, widget, {
				draw: function(){
					var self = this;
					
					widget.draw.call(this);
					
					color = 'white';
					var bgc = this.$element.css('background-color');
					
					var rgb = bgc.match(/^rgba?\((\d+),\s*(\d+),\s*(\d+)/);
					if(rgb){
						var luma = 0.2126 * parseInt(rgb[1]) + 0.7152 * parseInt(rgb[2]) + 0.0722 * parseInt(rgb[3]); // per ITU-R BT.709
						if (luma < 40) {
							color = '#a0a0a0';
						}
					}
					
					this.$element.empty().append(
				
						$('<div>').append(
							$('<span class="value">').css({
								'font-size': '32px'
							}),
							$('<span>').html(options.unit || null).css({
								'font-size': '16px'
							}),
							'<div class="sliders"></div>'
						).css({
							'text-align': 'center',
							'padding': '0 10px'
						})
					).attr('style','display: -webkit-box;display: -moz-box;display: -ms-flexbox;display: -webkit-flex;display: flex;').css({
						'display': 'flex',
						'-webkit-flex-direction': 'column',
						'-moz-flex-direction': 'column',
						'-ms-flex-direction': 'column',
						'-o-flex-direction': 'column',
						'flex-direction': 'column',
						'justify-content': 'center',
						'color': color
					});
					
					var sliderCssClasses = {
						target: 'target',
						base: 'base',
						origin: 'origin',
						handle: 'round-handle',
						handleLower: 'handle-lower',
						handleUpper: 'handle-upper',
						horizontal: 'horizontal',
						vertical: 'vertical',
						background: 'background',
						connect: 'connect',
						ltr: 'ltr',
						rtl: 'rtl',
						draggable: 'draggable',
						drag: 'state-drag',
						tap: 'state-tap',
						active: 'active',
						tooltip: 'tooltip',
						pips: 'pips',
						pipsHorizontal: 'pips-horizontal',
						pipsVertical: 'pips-vertical',
						marker: 'marker',
						markerHorizontal: 'marker-horizontal',
						markerVertical: 'marker-vertical',
						markerNormal: 'marker-normal',
						markerLarge: 'marker-large',
						markerSub: 'marker-sub',
						value: 'value',
						valueHorizontal: 'value-horizontal',
						valueVertical: 'value-vertical',
						valueNormal: 'value-normal',
						valueLarge: 'value-large',
						valueSub: 'value-sub'
					};
					
					var slider = this.slider = noUiSlider.create(this.$element.find('.sliders')[0], {
						start: options.minimum,
						animate: false,
						range: {
							min: options.minimum,
							max: options.maximum
						},
						cssClasses: sliderCssClasses
					});
					
					this.$element.find('.sliders').css({
						'height': '10px',
						'margin' : '10px 0'
					});
					
					this.$element.find('.sliders .noUi-round-handle').css({
						'position': 'relative',
						'width': '20px',
						'height': '20px',
						'left': '-10px',
						'top': '-5px',
						'border-radius': '10px',
						'background-color': '#f3f3f3',
						'cursor': 'pointer',
						'border': '1px solid #d2d2d2'
					});
					
					slider.on('update', function( values, handle ){
						var value = values[handle];
						self.$element.find('.value').html(value);
					});
					
					slider.on('slide', function( values, handle ){
						var value = values[handle];
						temporizedSet(self.set, self, value);
					});
					
					if(dataType === 'table.column' || dataType === 'resource.data'){
						this.onResourceUpdate = dataType === 'table.column' ? function(evt,updatedKeys){
							if(updatedKeys.indexOf('contentModifiedDate')!==-1) self.get();
						} : $.proxy(this.get, this);
						resource.on('updated', this.onResourceUpdate);
					} else if(dataType === 'device.request'){
						this.refeshIntervalId = setInterval($.proxy(this.get, this), (options.refreshPeriod || 30)*1000);
					}
					
					this.get();
					
				},
				
				set: function(value){
					
					setter_exe(value);
					
				},
				
				get: function(){
					var self = this;
					$.when(getter_exe()).done(function(d){
				
						if(!d){
							return;
						}
						
						console.log('get value = ',d.value);
						
						self.slider.set(d.value);
						self.setFooter(d.date ? d.date.toLocaleString() : '');
					
					});
				},
				
				destroy: function(){
					widget.destroy.call(this);
					
					if(this.onResourceUpdate){
						resource.off('updated', this.onResourceUpdate);
					}
					if(this.refeshIntervalId){
						clearInterval(this.refeshIntervalId);
					}
				}
				
			});
		}
	};
	
}));