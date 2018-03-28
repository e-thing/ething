(function (root, factory) {
    if (typeof define === 'function' && define.amd) {
        // AMD. Register as an anonymous module.
        define(['jquery'], factory);
    }
}(this, function ($) {
	
	
	return {
		
		require: ['widget/Widget','css!font-awesome'],
		
		instanciate: function(device, options, Widget){
			
			options = $.extend({
				pollingRefreshPeriod: 30000
			}, options);
			
			var parent = Widget({
				title: device.basename()
			});
			
			
			var destroyFn = {};
			var pollingRefreshPeriod = options.pollingRefreshPeriod || 30000;
			var capabilities = {};

			function setCapabilities(){
				['temperature', 'humidity', 'pressure'].forEach(function(type){
					capabilities[type] = false;
					
					if(device.data().hasOwnProperty(type)){
						capabilities[type] = 'prop';
					} else {
					
						var apiCmd = 'get' + type.charAt(0).toUpperCase() + type.slice(1);
						if(device.methods().indexOf(apiCmd)!==-1){
							capabilities[type] = 'api';
						}
					}
				});
			}

			function getDeviceValue(type, callback, fallback){
				
				if(capabilities[type] === 'prop'){
					callback(type, device.data(type));
					return;
				}
				
				
				if(capabilities[type] === 'api'){
					var apiCmd = 'get' + type.charAt(0).toUpperCase() + type.slice(1);
					device.execute(apiCmd).then(function(value){
						callback(type, value);
					}, function(err){
						fallback(type, err);
					});
					return;
				}
				
				// unable to get data
				fallback(type, 'no data');
			}

			function setViewValue(type, value){
				if(type==='temperature'){
					widget.setTemperature(value);
				} else if(type==='humidity'){
					widget.setHumidity(value);
				} else if(type==='pressure'){
					widget.setPressure(value);
				}
			}

			function notifyViewError(type, message){
				
			}

			function updateView(types){
				
				if(typeof types === 'undefined') types = ['temperature', 'humidity', 'pressure'];
				if(typeof types === 'string') types = [types];
				
				function set(type, value){
					// update the view state here
					setViewValue(type, value);
				}
				
				function error(type, err){
					// unable to get the data : notify the user
					notifyViewError(type, err.toString());
				}
				
				types.forEach(function(type){
					if(capabilities[type])
						getDeviceValue(type, set, error);
				});
				
			}

			function setRefreshStrategy(){
				
				['temperature', 'humidity', 'pressure'].forEach(function(type){
					
					if(capabilities[type]==='prop'){
					
						// update the view each time the data attribute change.
						var resourceUpdate = function(event, updatedAttributes){
							if(updatedAttributes.indexOf('data')!==-1){
								updateView(type);
							}
						}
						device.on('updated', resourceUpdate);
						
						destroyFn['resourceUpdate'+type] = function(){
							device.off('updated', resourceUpdate);
						};
					} else if(capabilities[type]==='api'){
						
						// polling mode !
						var timerId = setInterval(function(){
							updateView(type);
						}, pollingRefreshPeriod);
						
						destroyFn['pollingRefresh'+type] = function(){
							clearInterval(timerId);
						};
					}
					
				});
				
			}

			function destroy(){
				for(var i in destroyFn){
					destroyFn[i].call(this);
				}
			}
			
			setCapabilities();
			
			return widget = $.extend({}, parent, {
				
				draw: function(){
					var self = this;
					
					parent.draw.call(this);
					
					this.$element.empty();
					
					var $wrapper = $('<div>').appendTo(this.$element).css({
						'text-align': 'center'
					});
					
					
					
					if(capabilities['temperature']){
						$wrapper.append(
							$('<div class="item temperature">').html([
								'<i class="fa fa-thermometer-full" aria-hidden="true"></i> ',
								$('<span class="value">'),
								$('<span class="unit">').html('&#8451;')
							])
						);
					}
					
					if(capabilities['humidity']){
						$wrapper.append(
							$('<div class="item humidity">').html([
								'<i class="fa fa-tint" aria-hidden="true"></i> ',
								$('<span class="value">'),
								$('<span class="unit">').html('%')
							])
						);
					}
					
					if(capabilities['pressure']){
						$wrapper.append(
							$('<div class="item pressure">').html([
								'<i class="fa fa-tachometer" aria-hidden="true"></i> ',
								$('<span class="value">'),
								$('<span class="unit">').html('hPa')
							])
						);
					}
					
					this.$element.find('.value').css({
						'font-size': '52px'
					});
					this.$element.find('.unit').css({
						'font-size': '16px'
					});
					
					this.$element.attr('style','display: -webkit-box;display: -moz-box;display: -ms-flexbox;display: -webkit-flex;display: flex;').css({
						'display': 'flex',
						'-webkit-flex-direction': 'column',
						'-moz-flex-direction': 'column',
						'-ms-flex-direction': 'column',
						'-o-flex-direction': 'column',
						'flex-direction': 'column',
						'justify-content': 'center',
						'color': this.getDefaultColor()
					});
					
					updateView();
					setRefreshStrategy();
					
					this.resize();
				},
				
				adjustFont: function(){
					
					
					var fontSize, display, space = 0;
					var height = this.$element.height() || 160;
					var width = this.$element.width() || 160;
					
					var itemNb = 0;
					
					if(capabilities['temperature']) itemNb++;
					if(capabilities['humidity']) itemNb++;
					if(capabilities['pressure']) itemNb++;
					
					if(itemNb==0) itemNb = 1;
					
					if(width > 3 * height && itemNb > 1){
						// landscape
						fontSize = 40;
						display = 'inline-block';
						space = 20;
						if(width > 500) space = 40;
					} else {
						// portrait
						
						var innerHeight = height - 2 * 30;
						fontSize = Math.round((innerHeight / itemNb) - 10);
						
						var maxFontSize = width < 250 ? 40 : 56;
						
						if(fontSize>maxFontSize) fontSize = maxFontSize;
						
						display = 'block';
					}
					
					this.$element.find('.value').css({
						'font-size': fontSize+'px'
					});
					
					this.$element.find('.fa').css({
						'font-size': fontSize+'px'
					});
					
					this.$element.find('.item').css({
						'display': display
					});
					
					this.$element.find('.item:not(:first)').css({
						'margin-left': space ? (space + 'px') : ''
					});
					
				},
				
				resize: function(){
					this.adjustFont();
				},
				
				setTemperature: function(value){
					if(typeof value !== 'number') value = '?';
					else value = Math.round(value);
					this.$element.find('.temperature .value').html(value);
				},
				
				setHumidity: function(value){
					if(typeof value !== 'number') value = '?';
					else value = Math.round(value);
					this.$element.find('.humidity .value').html(value);
				},
				
				setPressure: function(value){
					if(typeof value !== 'number') value = '?';
					else value = Math.round(value);
					if(value > 80000){
						// in Pa, convert into hPa
						value = Math.round(value / 100);
					}
					this.$element.find('.pressure .value').html(value);
				},
				
				destroy: function(){
					destroy();
					parent.destroy.call(this);
				}
				
			});
			
		}
		
	};
	
	
}));