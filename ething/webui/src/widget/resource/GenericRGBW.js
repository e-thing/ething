(function (root, factory) {
    if (typeof define === 'function' && define.amd) {
        // AMD. Register as an anonymous module.
        define(['jquery', 'ui/widget', '//cdnjs.cloudflare.com/ajax/libs/noUiSlider/10.1.0/nouislider.min.js', 'css!//cdnjs.cloudflare.com/ajax/libs/noUiSlider/10.1.0/nouislider.min'], factory);
    }
}(this, function ($, Widget, noUiSlider) {
	
	// https://gist.github.com/paulkaplan/5184275
	function colorTemperatureToRGB(kelvin){

		var temp = kelvin / 100;
		var red, green, blue;

		if( temp <= 66 ){ 
			red = 255; 
			green = temp;
			green = 99.4708025861 * Math.log(green) - 161.1195681661;

			if( temp <= 19){
				blue = 0;
			} else {
				blue = temp-10;
				blue = 138.5177312231 * Math.log(blue) - 305.0447927307;
			}
		} else {
			red = temp - 60;
			red = 329.698727446 * Math.pow(red, -0.1332047592);
			green = temp - 60;
			green = 288.1221695283 * Math.pow(green, -0.0755148492 );
			blue = 255;
		}

		return {
			r : clamp(red,   0, 255),
			g : clamp(green, 0, 255),
			b : clamp(blue,  0, 255)
		}

	}

	function clamp( x, min, max ) {
		if(x<min){ return min; }
		if(x>max){ return max; }
		return x;
	}
	
	function componentToHex(c) {
		var hex = parseInt(c).toString(16);
		return hex.length == 1 ? "0" + hex : hex;
	}

	function rgbToHex(r, g, b) {
		return "#" + componentToHex(r) + componentToHex(g) + componentToHex(b);
	}
	
	function hexToRgb(hex) {
		var result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
		return result ? {
			r: parseInt(result[1], 16),
			g: parseInt(result[2], 16),
			b: parseInt(result[3], 16)
		} : null;
	}
	
	/* accepts parameters
	 * h  Object = {h:x, s:y, v:z}
	 * OR 
	 * h, s, v
	*/
	function HSVtoRGB(h, s, v) {
		var r, g, b, i, f, p, q, t;
		if (arguments.length === 1) {
			s = h.s, v = h.v, h = h.h;
		}
		i = Math.floor(h * 6);
		f = h * 6 - i;
		p = v * (1 - s);
		q = v * (1 - f * s);
		t = v * (1 - (1 - f) * s);
		switch (i % 6) {
			case 0: r = v, g = t, b = p; break;
			case 1: r = q, g = v, b = p; break;
			case 2: r = p, g = v, b = t; break;
			case 3: r = p, g = q, b = v; break;
			case 4: r = t, g = p, b = v; break;
			case 5: r = v, g = p, b = q; break;
		}
		return {
			r: Math.round(r * 255),
			g: Math.round(g * 255),
			b: Math.round(b * 255)
		};
	}
	
	function rgbToHsl(r, g, b){
		r /= 255, g /= 255, b /= 255;
		var max = Math.max(r, g, b), min = Math.min(r, g, b);
		var h, s, l = (max + min) / 2;

		if(max == min){
			h = s = 0; // achromatic
		}else{
			var d = max - min;
			s = l > 0.5 ? d / (2 - max - min) : d / (max + min);
			switch(max){
				case r: h = (g - b) / d + (g < b ? 6 : 0); break;
				case g: h = (b - r) / d + 2; break;
				case b: h = (r - g) / d + 4; break;
			}
			h /= 6;
		}

		return [h, s, l];
	}
	
	
	function pad(n, width, z) {
	  z = z || '0';
	  n = n + '';
	  return n.length >= width ? n : new Array(width - n.length + 1).join(z) + n;
	}
	
	return {
				
		instanciate: function(device, options){
			
			var minIntervalMs = 500;
			
			options = $.extend(true, {
				readonly: false,
				pollingRefreshPeriod: 30000
			}, options);
			
			var parent = Widget({
				title: device.basename()
			});
			
			var destroyFn = {};
			var readonly = !!options.readonly;
			var pollingRefreshPeriod = options.pollingRefreshPeriod || 30000;
			var capabilities = {};

			function setCapabilities(){
				['color', 'status', 'brightness'].forEach(function(type){
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
				
				['setColor', 'setBrightness', 'on', 'off'].forEach(function(cmd){
					capabilities[cmd] = false;
					
					if(device.methods().indexOf(cmd)!==-1){
						capabilities[cmd] = 'api';
					}
				});
			}

			function getDeviceValue(type, callback, fallback){
				
				if(capabilities[type]==='prop'){
					callback(type, device.data(type));
					return;
				}
				
				if(capabilities[type]==='api'){
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

			function setDeviceValue(type, value, callback, fallback){
				if(!readonly) {
					var cmd = '';
					
					if(type === 'status') {
						cmd = value ? 'on' : 'off';
						value = undefined;
					} else {
						cmd = 'set' + type.charAt(0).toUpperCase() + type.slice(1);
					}
					
					if(capabilities[cmd]){
						device.execute(cmd, value).then(callback, fallback);
						return;
					}
				}
				
				fallback('not capable');
			}

			function onViewChanged(type, value, oldValue){
				// is fired, each time the user change the state of the view
				
				// start loader
				toggleLoader(type, true);
				// disable buttons
				toggleView(type, false);
				
				function always(){
					// remove loader
					toggleLoader(type, false);
					// enable buttons
					toggleView(type, true);
				}
				
				function success(){
					always();
					setViewValue(type, value);
				}
				
				function error(){
					always();
					setViewValue(type, oldValue); // restore the old value !
				}
				
				setDeviceValue(type, value, success, error);
				
			}

			function setViewValue(type, value){
				if(type==='status'){
					widget.setStatus(value);
				} else if(type==='color'){
					widget.setColor(value);
				} else if(type==='brightness'){
					widget.setBrightness(value);
				}
			}

			function notifyViewError(type, message){
				
			}

			function toggleView(type, enable){
				
			}

			function toggleLoader(type, enable){
				
			}

			function updateView(types){
				
				if(typeof types === 'undefined') types = ['color', 'status', 'brightness'];
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
				
				['color', 'status', 'brightness'].forEach(function(type){
					
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
					
					var $wrapper = $('<div>').css({
						'text-align': 'center',
						'padding': '0 10px'
					});
					
					this.$element.empty().append(
						$wrapper
					).attr('style','display: -webkit-box;display: -moz-box;display: -ms-flexbox;display: -webkit-flex;display: flex;').css({
						'display': 'flex',
						'-webkit-flex-direction': 'column',
						'-moz-flex-direction': 'column',
						'-ms-flex-direction': 'column',
						'-o-flex-direction': 'column',
						'flex-direction': 'column',
						'justify-content': 'center'
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
					
					
					if(capabilities['status'] || (capabilities['on'] && capabilities['off'])){
						
						var $status = $('<svg class="state" width="40" height="40" viewBox="0 0 512 512"><g><path d="m338.6,136.1c-23.6-22.7-54.6-34.4-87.4-33.2-62.9,2.5-114.2,55.7-114.4,118.7-0.1,27.9 9.7,55.1 27.6,76.5 25.8,31 40,70.1 40,110.2 0,0-2.7,18.4 10.4,18.4h82.4c13.4,0 10.4-18.4 10.4-18.4 0-39.2 14.4-78 41.7-112.2 16.9-21.3 25.9-46.9 25.9-74.1 0-32.7-13-63.3-36.6-85.9zm-5.6,147c-29.7,37.2-45.6,79.6-46.2,122.8h-61.6c-0.6-44.1-16.4-87-44.8-121.1-14.7-17.7-22.8-40.1-22.7-63.1 0.2-52 42.5-95.9 94.4-98 27.1-1 52.7,8.7 72.1,27.4 19.5,18.7 30.2,43.9 30.2,70.9-0.1,22.5-7.4,43.6-21.4,61.1z"/><path d="m393.2,67.8c-4.1-4.1-10.7-4.1-14.7,0l-25.4,25.4c-4.1,4.1-4.1,10.7 0,14.7s10.7,4.1 14.7,0l25.4-25.4c4.1-4 4.1-10.6 0-14.7z"/><path d="m297.6,440.9h-83.2c-5.8,0-10.4,4.7-10.4,10.4 0,5.8 4.7,10.4 10.4,10.4h83.2c5.8,0 10.4-4.7 10.4-10.4 0-5.7-4.7-10.4-10.4-10.4z"/><path d="m281.9,480.1h-51.7c-5.8,0-10.4,4.7-10.4,10.4 0,5.8 4.7,10.4 10.4,10.4h51.7c5.8,0 10.4-4.7 10.4-10.4 5.68434e-14-5.7-4.7-10.4-10.4-10.4z"/><path d="M256,67.7c5.8,0,10.4-4.7,10.4-10.4V21.4c0-5.8-4.7-10.4-10.4-10.4s-10.4,4.7-10.4,10.4v35.9    C245.6,63.1,250.2,67.7,256,67.7z"/><path d="m158.9,108c4.1-4.1 4.1-10.7 0-14.7l-25.4-25.4c-4.1-4.1-10.7-4.1-14.7,0s-4.1,10.7 0,14.7l25.4,25.4c4.1,4 10.7,4 14.7,0z"/><path d="m439.6,194.6h-35.9c-5.8,0-10.4,4.7-10.4,10.4s4.7,10.4 10.4,10.4h35.9c5.8,0 10.4-4.7 10.4-10.4s-4.7-10.4-10.4-10.4z"/><path d="m108.3,194.6h-35.9c-5.8,0-10.4,4.7-10.4,10.4s4.7,10.4 10.4,10.4h35.9c5.8,0 10.4-4.7 10.4-10.4s-4.6-10.4-10.4-10.4z"/></g></svg>');
						
						$wrapper.append($status);
						
					}
					
					if(capabilities['brightness'] || capabilities['setBrightness']){
						
						var $brightness = $('<div class="sliders brightness"></div>'); 
						
						$wrapper.append($brightness);
						
						var brightSlider = this.brightSlider = noUiSlider.create($brightness[0], {
							start: 0,
							animate: false,
							range: {
								min: 0,
								max: 100
							},
							cssClasses: sliderCssClasses
						});
						
						brightSlider.on('update', function( values, handle ){
							self.updateViewState();
						});
						
						var oldBrightnessValue = 0;
						brightSlider.on('slide', function( values, handle ){
							
							var brightness = parseInt(brightSlider.get());
							
							onViewChanged('brightness', brightness, oldBrightnessValue);
							oldBrightnessValue = brightness;
						});
					}
					
					if(capabilities['color'] || capabilities['setColor']){
						var $color = $('<div class="sliders color"></div>'); 
						
						$wrapper.append($color);
						
						var colorSlider = this.colorSlider = noUiSlider.create($color[0], {
							start: 0,
							animate: false,
							range: {
								min: 0,
								max: 360
							},
							cssClasses: sliderCssClasses
						});
						
						colorSlider.on('update', function( values, handle ){
							
							var rgb = HSVtoRGB(values[handle]/360, 1, 1);
							var hex = rgbToHex(rgb.r, rgb.g, rgb.b);
							
							self.$element.find('.sliders.brightness .noUi-base').css({
								'background': 'linear-gradient(to right, grey, '+hex+')'
							});
							
							self.updateViewState();
						});
						
						
						
						var oldColorValue = '#FFFFFF';
						colorSlider.on('slide', function( values, handle ){
							
							var hue = parseInt(colorSlider.get());
							var rgb = HSVtoRGB(hue/360, 1, 1);
							var hex = rgbToHex(rgb.r, rgb.g, rgb.b);
							
							onViewChanged('color', hex, oldColorValue);
							oldColorValue = hex;
						});
					}
					
					this.$element.find('.sliders.color .noUi-base').css({
						'background': 'linear-gradient(to right, #ff0000 0%, #ffff00 17%, #00ff00 33%, #00ffff 50%, #0000ff 67%, #ff00ff 83%, #ff0000 100%)'
					});
					
					this.$element.find('.sliders').css({
						'height': '10px',
						'margin' : '10px 0'
					});
					
					this.$element.find('.sliders.color').css({
						'margin-top': '20px'
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
					
					this.$element.find('svg.state').css({
						'cursor': 'pointer'
					}).click(function(){
						
						var status = !self.$element.find('svg.state').data('status');
						onViewChanged('status', status, !status);
					});
					
					
					updateView();
					setRefreshStrategy();
					
					
				},
				
				updateViewState: function(){
					var brightness = this.brightSlider ? parseInt(this.brightSlider.get()) : 100;
					var hex = '#f4f142';
					var $status = this.$element.find('svg.state');
					var status = $status.length>0 ? (!!$status.data('status')) : true;
					
					if(brightness && this.colorSlider){
						var hue = parseInt(this.colorSlider.get());
						var rgb = HSVtoRGB(hue/360, 1, 1);
						hex = rgbToHex(rgb.r, rgb.g, rgb.b);
					}
					
					this.$element.find('svg.state').css('fill',status ? hex : '#cacaca');
				},
				
				setColor: function(hex){
					var rgb = hexToRgb(hex);
					var hsl = rgbToHsl(rgb.r, rgb.g, rgb.b);
					var hue = hsl[0] * 360;
					
					if(this.colorSlider) this.colorSlider.set(hue);
				},
				
				setBrightness: function(brightness){
					if(this.brightSlider) this.brightSlider.set(brightness);
				},
				
				setStatus: function(status){
					this.$element.find('svg.state').data('status', !!status);
					this.updateViewState();
				},
				
				destroy: function(){
					destroy()
					parent.destroy.call(this);
				}
				
			});
			
		}
		
	};
	
	
}));