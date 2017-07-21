(function (root, factory) {
    if (typeof define === 'function' && define.amd) {
        // AMD. Register as an anonymous module.
        define(['jquery'], factory);
    }
}(this, function ($) {
	
	
	return {
		
		require: ['widget/Buttons'],
		
		instanciate: function(sensor, options, Buttons){
			
			var widget = Buttons({
				buttons: [{
					label: 'On',
					onClick: function(){
						return sensor.execute('on');
					}
				},{
					label: 'Off',
					onClick: function(){
						return sensor.execute('off');
					}
				}]
			});
			
			return $.extend({}, widget, {
				
				draw: function(){
					this.$element.attr('data-title',sensor.basename());
					this.$element.attr('data-footer',sensor.modifiedDate().toLocaleString());
					
					widget.draw.call(this);
				}
				
			});
			
		}
		
	};
	
	
}));