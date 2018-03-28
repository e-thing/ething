(function (root, factory) {
    if (typeof define === 'function' && define.amd) {
        // AMD. Register as an anonymous module.
        define(['jquery','ui/widget'], factory);
    }
}(this, function ($, Widget) {
	
	
	function Buttons(opt){
		
		opt = opt || {};
		
		var parent = Widget(opt);
		
		var self = {};
		
		var buttons = opt.buttons || [];
		var readonly = !!opt.readonly;
		
		return $.extend(self, parent, {
			
			draw: function(){
				
				parent.draw.call(this);
				
				this.$element.append(
					$('<div>').append(
						$('<div class="btn-group" role="group">')
					).css({
						/*'margin': 'auto 0px',*/
						'text-align': 'center',
						'position': 'relative',
						'width': '100%'
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
				
				buttons.forEach(function(btn, index){
					
					var self = this;
					
					var $btn = $('<button type="button" class="btn btn-default">').html(btn.label || index);
					
					if(readonly || btn.readonly){
						$btn.attr('disabled',"disabled");
					}
					
					$btn.click(function(){
						if(typeof btn.onClick === 'function'){
							var dfr = btn.onClick.call(self);
							if(typeof dfr !== 'undefined' && dfr!==null){
								self.setEnabled(false);
								$.when( dfr ).always(function(){
									self.setEnabled(true);
								});
							}
						}
					});
					
					if(btn.bgColor){
						
						var color = 'white';
						var bgc = btn.bgColor;
						var rgb = null;
						
						if(/^rgb/.test(bgc)){
							rgb = bgc.match(/^rgba?\((\d+),\s*(\d+),\s*(\d+)/).shift();
						} else if (/^#/.test(bgc)){
							rgb = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(bgc);
							rgb = [
								parseInt(rgb[1], 16),
								parseInt(rgb[2], 16),
								parseInt(rgb[3], 16)
							];
						}
						if(rgb){
							var luma = 0.2126 * parseInt(rgb[0]) + 0.7152 * parseInt(rgb[1]) + 0.0722 * parseInt(rgb[2]); // per ITU-R BT.709
							if (luma < 40) {
								color = '#a0a0a0';
							}
						}
						
						$btn.css('background-color', bgc);
						$btn.css('color', color);
					}
					
					this.$element.find('.btn-group').append($btn);
					
				}, this);
				
			},
			
			setActiveBtn: function(index){
				this.$element.find('.btn-group').children().removeClass('btn-primary').eq(index).addClass('btn-primary');
			},
			
			setEnabled: function(enabled, index){
				var $btns = this.$element.find('.btn');
				if(typeof index === 'number')
					$btns = this.$element.find('.btn').get(index);
				enabled ? 
					$btns.removeAttr('disabled') :
					$btns.attr('disabled', 'disabled');
			}
			
		});
		
	}
	
	
	return Buttons;
	
}));