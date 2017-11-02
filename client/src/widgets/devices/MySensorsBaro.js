(function (root, factory) {
    if (typeof define === 'function' && define.amd) {
        // AMD. Register as an anonymous module.
        define(['jquery'], factory);
    }
}(this, function ($) {
	
	
	return {
		
		require: ['widget/Number'],
		
		instanciate: function(sensor, options, Number){
			
			var widget = Number({
				unit : 'hPa',
				title: sensor.basename()
			});
			
			var update = function(){
				var pressure = sensor.val('pressure');
				
				if(typeof pressure === 'number'){
					if(pressure > 80000){
						// in Pa
					} else if(pressure > 800){
						// in hPa
						pressure *= 100;
					}
				} else pressure = null;
				
				widget.val(pressure!==null ? Math.round(pressure/100) : '?');
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