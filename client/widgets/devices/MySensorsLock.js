(function (root, factory) {
    if (typeof define === 'function' && define.amd) {
        // AMD. Register as an anonymous module.
        define(['jquery'], factory);
    }
}(this, function ($) {
	
	
	return {
		
		require: ['widget/Label', 'css!font-awesome'],
		
		instanciate: function(sensor, options, Label){
			
			var widget = Label({
				fontSize: 52,
				title: sensor.basename()
			});
			
			var update = function(){
				var locked = sensor.val('V_LOCK_STATUS');
				if(typeof locked !== 'boolean') locked = null;
				var icl = 'fa-'+(locked===null?'question':(locked?'lock':'unlock'));
				widget.val('<i class="fa '+icl+'" aria-hidden="true"></i>');
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