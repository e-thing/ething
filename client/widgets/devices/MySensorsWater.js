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
				unit : 'L'
			});
			
			var update = function(){
				
				var vol = sensor.val('V_VOLUME');
				var unit = 'L';
				
				if(vol < 1){
					unit = 'mL';
					vol = vol * 1000;
				}
				
				widget.val(vol);
				widget.setUnit(unit);
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