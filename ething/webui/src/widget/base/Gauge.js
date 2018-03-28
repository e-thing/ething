(function (root, factory) {
    if (typeof define === 'function' && define.amd) {
        // AMD. Register as an anonymous module.
        define(['jquery','ui/widget','circleBar'], factory);
    }
}(this, function ($, Widget) {
	
	function Gauge(opt){
		
		opt = opt || {};
		
		var parent = Widget(opt);
		
		var self = {};
		
		var title = opt.title || '';
		var footer = opt.footer || '';
		var unit = opt.unit || '';
		var minimum = typeof opt.minimum === 'number' ? opt.minimum : 0;
		var maximum = typeof opt.maximum === 'number' ? opt.maximum : 100;
		var color = opt.color || '#307bbb';
		var value = opt.value || 0;
		
		
		return $.extend(self, parent, {
			
			draw: function(){
				
				this.$element.css({
					'text-align': 'center',
					'padding': '10px 0 0 0',
					'font-size': '14px',
					'color': '#b3b3b3'
				});
				
				
				this.$circleBar = $('<div>').circleBar({
					min: minimum,
					max: maximum,
					unit: unit,
					value: value,
					color: color
				}).css({
					'margin': '10px auto'
				});
				
				this.$element.empty().append('<div class="title">'+title+'</div>', this.$circleBar, '<div class="clearfix"></div>', '<div class="footer">'+footer+'</div>');
				
				this.$element.find('.title, .footer').css({
					'white-space': 'nowrap',
					'font-size': 'smaller'
				});
				
				
			},
			
			val: function(v){
				value = v;
				
				this.$circleBar.circleBar('val', value);
			},
			
			setFooter: function(f){
				footer = f;
				this.$element.find('.footer').html(footer);
				this.resize();
			},
			
			resize: function(){
				
				var circleHeight = this.$element.height() - this.$element.find('.title').height() - this.$element.find('.footer').height() -10*2;
				var elemWidth = this.$element.width()-10;
				var marginLeft = 5;
				var verticalMargin = 0;
				
				if(circleHeight>elemWidth){
					verticalMargin += circleHeight - elemWidth;
					circleHeight = elemWidth;
				} else {
					marginLeft += (elemWidth - circleHeight) / 2;
				}
				
				this.$element.find('.c100').css({
					'font-size': circleHeight+'px',
					'margin-left': marginLeft+'px'
				});
				
				this.$element.children().first().css('margin-bottom', (verticalMargin/2)+'px');
				this.$element.children().last().css('margin-top', (verticalMargin/2)+'px');
				
			}
			
		});
		
	}
	
	
	
	return Gauge;
	
}));