(function (root, factory) {
    if (typeof define === 'function' && define.amd) {
        // AMD. Register as an anonymous module.
        define(['jquery'], factory);
    }
}(this, function ($) {
	
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
		
		require: ['widget/Widget', '//cdnjs.cloudflare.com/ajax/libs/noUiSlider/10.1.0/nouislider.min.js', 'css!//cdnjs.cloudflare.com/ajax/libs/noUiSlider/10.1.0/nouislider.min'],
		
		instanciate: function(sensor, options, Widget, noUiSlider){
			
			var minIntervalMs = 500;
			
			
			var widget = Widget({
				title: sensor.basename()
			});
			
			return $.extend({}, widget, {
				draw: function(){
					var self = this;
					
					widget.draw.call(this);
					
					this.$element.empty().append(
				
						$('<div>').append(
							'<svg class="state" width="40" height="40" viewBox="0 0 512 512"><g><path d="m338.6,136.1c-23.6-22.7-54.6-34.4-87.4-33.2-62.9,2.5-114.2,55.7-114.4,118.7-0.1,27.9 9.7,55.1 27.6,76.5 25.8,31 40,70.1 40,110.2 0,0-2.7,18.4 10.4,18.4h82.4c13.4,0 10.4-18.4 10.4-18.4 0-39.2 14.4-78 41.7-112.2 16.9-21.3 25.9-46.9 25.9-74.1 0-32.7-13-63.3-36.6-85.9zm-5.6,147c-29.7,37.2-45.6,79.6-46.2,122.8h-61.6c-0.6-44.1-16.4-87-44.8-121.1-14.7-17.7-22.8-40.1-22.7-63.1 0.2-52 42.5-95.9 94.4-98 27.1-1 52.7,8.7 72.1,27.4 19.5,18.7 30.2,43.9 30.2,70.9-0.1,22.5-7.4,43.6-21.4,61.1z"/><path d="m393.2,67.8c-4.1-4.1-10.7-4.1-14.7,0l-25.4,25.4c-4.1,4.1-4.1,10.7 0,14.7s10.7,4.1 14.7,0l25.4-25.4c4.1-4 4.1-10.6 0-14.7z"/><path d="m297.6,440.9h-83.2c-5.8,0-10.4,4.7-10.4,10.4 0,5.8 4.7,10.4 10.4,10.4h83.2c5.8,0 10.4-4.7 10.4-10.4 0-5.7-4.7-10.4-10.4-10.4z"/><path d="m281.9,480.1h-51.7c-5.8,0-10.4,4.7-10.4,10.4 0,5.8 4.7,10.4 10.4,10.4h51.7c5.8,0 10.4-4.7 10.4-10.4 5.68434e-14-5.7-4.7-10.4-10.4-10.4z"/><path d="M256,67.7c5.8,0,10.4-4.7,10.4-10.4V21.4c0-5.8-4.7-10.4-10.4-10.4s-10.4,4.7-10.4,10.4v35.9    C245.6,63.1,250.2,67.7,256,67.7z"/><path d="m158.9,108c4.1-4.1 4.1-10.7 0-14.7l-25.4-25.4c-4.1-4.1-10.7-4.1-14.7,0s-4.1,10.7 0,14.7l25.4,25.4c4.1,4 10.7,4 14.7,0z"/><path d="m439.6,194.6h-35.9c-5.8,0-10.4,4.7-10.4,10.4s4.7,10.4 10.4,10.4h35.9c5.8,0 10.4-4.7 10.4-10.4s-4.7-10.4-10.4-10.4z"/><path d="m108.3,194.6h-35.9c-5.8,0-10.4,4.7-10.4,10.4s4.7,10.4 10.4,10.4h35.9c5.8,0 10.4-4.7 10.4-10.4s-4.6-10.4-10.4-10.4z"/></g></svg>',
							'<div class="sliders brightness"></div>',
							'<div class="sliders color"></div>'
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
					
					var brightSlider = this.brightSlider = noUiSlider.create(this.$element.find('.brightness')[0], {
						start: 0,
						animate: false,
						range: {
							min: 0,
							max: 100
						},
						cssClasses: sliderCssClasses
					});
					
					var colorSlider = this.colorSlider = noUiSlider.create(this.$element.find('.color')[0], {
						start: 0,
						animate: false,
						range: {
							min: 0,
							max: 360
						},
						cssClasses: sliderCssClasses
					});
					
					
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
						
						var brightness = parseInt(self.brightSlider.get());
						
						if(brightness){
							self.brightSlider.set(0);
						} else {
							self.brightSlider.set(100);
						}
						
						self.sendValueToSensor();
					});
					
					
					colorSlider.on('update', function( values, handle ){
						
						var rgb = HSVtoRGB(values[handle]/360, 1, 1);
						var hex = rgbToHex(rgb.r, rgb.g, rgb.b);
						
						self.$element.find('.sliders.brightness .noUi-base').css({
							'background': 'linear-gradient(to right, grey, '+hex+')'
						});
						
						self.updateState();
					});
					
					brightSlider.on('update', function( values, handle ){
						self.updateState();
					});
					
					brightSlider.on('slide', function( values, handle ){
						self.sendValueToSensor();
					});
					colorSlider.on('slide', function( values, handle ){
						self.sendValueToSensor();
					});
					
					
					sensor.on('updated', this.refreshFromSensorState);
					
					setTimeout(function(){
						self.refreshFromSensorState();
					}, 1);
					
					
					
				},
				
				setColor: function (hex){
					
					var $cc = this.$element.find('.color');
					
					$cc.css('background-color', hex);
					
					color = 'white';
					var bgc = $cc.css('background-color');
					
					var rgb = bgc.match(/^rgba?\((\d+),\s*(\d+),\s*(\d+)/);
					if(rgb){
						var luma = 0.2126 * parseInt(rgb[1]) + 0.7152 * parseInt(rgb[2]) + 0.0722 * parseInt(rgb[3]); // per ITU-R BT.709
						if (luma > 200 || luma === 0) {
							color = '#a0a0a0';
						}
					}
					
					$cc.css('color', color);
				},
				
				setBrightness: function(brightness){
					this.val(brightness);
				},
				
				refreshFromSensorState: function(){
					// get the sensor value
					var brightness = 0;
					var colorMode = sensor.data('color_mode', 0);
					var color = '#FFFFFF';
					
					if(sensor.data('power', 'off') === 'on'){
						brightness = sensor.data('bright', 100);
					}
					if(!colorMode){
						if(sensor.data('rgb', false))
							colorMode = 1;
						else if(sensor.data('ct', false))
							colorMode = 2;
						else if(sensor.data('hue', false))
							colorMode = 3;
					}
					if(colorMode === 1){ // rgb
						color = '#' + pad(parseInt(sensor.data('rgb', 0)).toString(16), 6, '0');
					} else if (colorMode === 2){ // color temperature
						var c = colorTemperatureToRGB(sensor.data('ct', 5000));
						color = rgbToHex(c.r, c.g, c.b);
					} else if (colorMode === 3){ // hsv
						var c = HSVtoRGB(sensor.data('hue', 50)/359, sensor.data('sat', 50)/100, brightness/100);
						color = rgbToHex(c.r, c.g, c.b);
					} 
					
					var rgb = hexToRgb(color);
					var hsl = rgbToHsl(rgb.r, rgb.g, rgb.b);
					var hue = hsl[0] * 360;
					
					this.colorSlider.set(hue);
					this.brightSlider.set(brightness);
					
				},
				
				sendValueToSensor: function(){
				
					var hue = parseInt(this.colorSlider.get());
					var brightness = parseInt(this.brightSlider.get());
					
					var rgb = HSVtoRGB(hue/360, 1, 1);
					var hex = rgbToHex(rgb.r, rgb.g, rgb.b);
					
					var color = parseInt(hex.replace(/^#/,''), 16);
					
					var self = this;
					var delay = 0;
					var diff = this.lastExecute ? (Date.now() - this.lastExecute) : (minIntervalMs + 1);
					
					if(this.timeoutId) clearTimeout(this.timeoutId);
					
					if(diff < minIntervalMs){
						delay = minIntervalMs - diff;
					}
					
					this.timeoutId = setTimeout(function(){
						self.lastExecute = Date.now();
						if(brightness>0){
							sensor.execute('setColor', {
								'color': color,
								'brightness': brightness
							});
						} else {
							sensor.execute('off');
						}
					}, delay);
					
				},
				
				updateState: function(){
					var brightness = parseInt(this.brightSlider.get());
					
					if(brightness){
						var hue = parseInt(this.colorSlider.get());
						var rgb = HSVtoRGB(hue/360, 1, 1);
						var hex = rgbToHex(rgb.r, rgb.g, rgb.b);
					}
					
					this.$element.find('svg.state').css('fill',brightness===0 ? '#cacaca' : hex);
				},
				
				destroy: function(){
					sensor.off('updated', this.refreshFromSensorState);
					widget.destroy.call(this);
				}
				
			});
			
		}
		
	};
	
	
}));