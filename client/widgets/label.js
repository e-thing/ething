(function (root, factory) {
    if (typeof define === 'function' && define.amd) {
        // AMD. Register as an anonymous module.
        define(['jquery','widget/Widget'], factory);
    }
}(this, function ($, Widget) {
	
	
	function Label(opt){
	
		var parent = Widget(opt);
		
		var self = {};
		
		var value = opt.value;
		var fontSize = opt.fontSize || 52;
		
		return $.extend(self, parent, {
			
			draw: function(){
				
				var color = 'white';
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
						$('<span class="value">').html(value).css({
							'font-size': fontSize+'px'
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
				value = v;
				this.$element.find('.value').html(value);
			},
			
			setFontSize: function(fs){
				fontSize = fs;
				this.draw();
			}
			
		});
		
	}
	
	
	return Label;
	
}));