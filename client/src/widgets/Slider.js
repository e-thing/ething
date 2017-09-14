(function (root, factory) {
    if (typeof define === 'function' && define.amd) {
        // AMD. Register as an anonymous module.
        define(['jquery','widget/Widget','//cdnjs.cloudflare.com/ajax/libs/bootstrap-slider/9.8.1/bootstrap-slider.min.js', 'css!//cdnjs.cloudflare.com/ajax/libs/bootstrap-slider/9.8.1/css/bootstrap-slider.min'], factory);
    }
}(this, function ($, Widget) {
	
	
	function Slider(opt){
		
		opt = $.extend( {
			min: 0,
			max: 100,
			value: 0,
			onchange: null
		}, opt || {} );
		
		var parent = Widget(opt);
		
		var self = {};
		
		return $.extend(self, parent, {
			
			draw: function(){
				var self = this;
				
				parent.draw.call(this);
				
				var color = opt.color;
				if(!color){
					color = 'white';
					var bgc = this.$element.css('background-color');
					
					var rgb = bgc.match(/^rgba?\((\d+),\s*(\d+),\s*(\d+)/);
					if(rgb){
						var luma = 0.2126 * parseInt(rgb[1]) + 0.7152 * parseInt(rgb[2]) + 0.0722 * parseInt(rgb[3]); // per ITU-R BT.709
						if (luma < 40) {
							color = '#a0a0a0';
						}
					}
				}
				
				var $slider = $('<input class="value" type="text"/>');
				
				$slider.on('change', function(evt){
					if(typeof opt.onchange === 'function')
						opt.onchange.call(self, evt.value.newValue);
				});
				
				this.$element.empty().append(
			
					$('<div>').append(
						$slider
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
				

				$slider.bootstrapSlider({
					value: opt.value || 0,
					min: opt.min,
					max: opt.max
				});
				
				this.$element.find('.slider').css('width','100%');
				
			},
			
			val: function(v){
				if(typeof v === 'undefined') return this.$element.find('.value').bootstrapSlider('getValue');
				else this.$element.find('.value').bootstrapSlider('setValue', v);
			},
			
			destroy: function(){
				this.$element.find('.value').bootstrapSlider('destroy');
				parent.destroy.call(this);
			}
			
		});
		
	}
	
	
	return Slider;
	
}));