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
				unit : '%',
				title: sensor.basename()
			});
			
			var setValue = function(value){
				widget.val(value);
				widget.setFooter(sensor.modifiedDate().toLocaleString());
			};
			
			var update = function(){
				var value = sensor.data('humidity', false);
				if(value===false){
					sensor.execute('getHumidity').done(setValue);
				} else {
					setValue(value);
				}
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