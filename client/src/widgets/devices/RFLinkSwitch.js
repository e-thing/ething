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
						return sensor.execute('on').update(update);
					}
				},{
					label: 'Off',
					onClick: function(){
						return sensor.execute('off').update(update);
					}
				}],
				title: sensor.basename()
			});
			
			var update = function(){
				widget.setActiveBtn(sensor.data('status', false) ? 0 : 1);
				widget.setFooter(sensor.modifiedDate().toLocaleString());
			};
			
			return $.extend({}, widget, {
				
				draw: function(){
					widget.draw.call(this);
					
					sensor.on('updated', update);
					
					update();
				},
				
				destroy: function(){
					sensor.off('updated', update);
					widget.destroy.call(this);
				}
				
			});
			
		}
		
	};
	
	
}));