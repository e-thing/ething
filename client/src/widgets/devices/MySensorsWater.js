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
				unit : 'L',
				title: sensor.basename()
			});
			
			var update = function(){
				
				var vol = sensor.val('volume');
				var unit = 'L';
				
				if(vol < 1){
					unit = 'mL';
					vol = vol * 1000;
				}
				
				widget.val(vol);
				widget.setUnit(unit);
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