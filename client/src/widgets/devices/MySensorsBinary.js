(function (root, factory) {
    if (typeof define === 'function' && define.amd) {
        // AMD. Register as an anonymous module.
        define(['jquery'], factory);
    }
}(this, function ($) {
	
	
	return {
		
		require: ['widget/Switch'],
		
		instanciate: function(sensor, options, Switch){
			
			var widget = Switch({
				onChange: function(value){
					return sensor.execute(value?'on':'off').always(function(){
						sensor.update();
					});
				},
				title: sensor.basename()
			});
			
			var update = function(){
				var value = sensor.val('status');
				
				widget.val(!!value);
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