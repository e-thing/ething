(function (root, factory) {
    if (typeof define === 'function' && define.amd) {
        // AMD. Register as an anonymous module.
        define(['jquery', 'widget/base/Number'], factory);
    }
}(this, function ($, Number) {
	
	return {
		
		instanciate: function(sensor){
			
			
			var widget = Number({
				unit : '&#8451;',
				title: sensor.basename()
			});
			
			var setValue = function(value){
				widget.val(value);
				widget.setFooter(sensor.modifiedDate().toLocaleString());
			};
			
			var update = function(){
				sensor.getTemperature().done(function(value){
					setValue(value);
				});
			};
			
			return $.extend({}, widget, {
				
				draw: function(){
					
					widget.draw.call(this);
					
					sensor.on('DeviceDataSet', update);
					
					// polling
					this.p_pollingTimerId = setInterval(update, 30000);
					
					update();
				},
				
				destroy: function(){
					sensor.off('DeviceDataSet', update);
					clearInterval(this.p_pollingTimerId);
					widget.destroy.call(this);
				}
				
			});
			
		}
		
	};
	
}));