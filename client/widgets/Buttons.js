(function (root, factory) {
    if (typeof define === 'function' && define.amd) {
        // AMD. Register as an anonymous module.
        define(['jquery','widget/Widget'], factory);
    }
}(this, function ($, Widget) {
	
	
	function Buttons(opt){
	
		var parent = Widget(opt);
		
		var self = {};
		
		var setEnabled = function(enabled){
			enabled ? 
				self.$element.find('.btn').removeAttr('disabled') :
				self.$element.find('.btn').attr('disabled', 'disabled');
		};
		
		var buttons = opt.buttons || [];
		
		
		return $.extend(self, parent, {
			
			draw: function(){
				
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
					
					$btn.click(function(){
						if(typeof btn.onClick === 'function'){
							setEnabled(false);
							$.when( btn.onClick.call(self) ).always(function(){
								setEnabled(true);
							})
							
						}
					});
					
					this.$element.find('.btn-group').append($btn);
					
				}, this);
				
			}
			
		});
		
	}
	
	
	return Buttons;
	
}));