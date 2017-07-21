(function (root, factory) {
    if (typeof define === 'function' && define.amd) {
        // AMD. Register as an anonymous module.
        define(['jquery','widget/Widget'], factory);
    }
}(this, function ($, Widget) {
	
	
	function Number(opt){
	
		var parent = Widget(opt);
		
		var self = {};
		
		var formatValue = function(v){
			return typeof v === 'number' ? v.toFixed(opt.decimal || 0) : 0;
		}
		
		var unit = opt.unit || '';
		var value = formatValue(opt.value);
		
		
		
		return $.extend(self, parent, {
			
			draw: function(){
				
				var color = 'white';
				var bgc = this.$element.css('background-color');
				
				var rgb = /^rgb/.test(bgc) ? bgc.match(/^rgba?\((\d+),\s*(\d+),\s*(\d+)/) : [0,0,0,0];
				if(rgb){
					var luma = 0.2126 * parseInt(rgb[1]) + 0.7152 * parseInt(rgb[2]) + 0.0722 * parseInt(rgb[3]); // per ITU-R BT.709
					if (luma < 40) {
						color = '#a0a0a0';
					}
				}
				
				this.$element.empty().append(
			
					$('<div>').append(
						$('<span class="value">').html(value).css({
							'font-size': '52px'
						}),
						$('<span>').html(unit).css({
							'font-size': '16px'
						})
					).css({
						'text-align': 'center'
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
				
			},
			
			val: function(v){
				value = formatValue(v);
				this.$element.find('.value').html(value);
			},
			
			setUnit: function(u){
				unit = u;
				this.draw();
			}
			
		});
		
	}
	
	
	return Number;
	
}));