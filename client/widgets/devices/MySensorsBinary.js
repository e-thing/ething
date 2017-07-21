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
				}
			});
			
			var update = function(){
				var value = sensor.val('V_STATUS');
			
				if(value===null){
					value = sensor.val('V_LIGHT');
				}
				
				widget.val(!!value);
			};
			
			return $.extend({}, widget, {
				
				draw: function(){
					this.$element.attr('data-title',sensor.basename());
					this.$element.attr('data-footer',sensor.modifiedDate().toLocaleString());
					
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