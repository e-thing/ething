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
					var self =  this;
					widget.draw.call(this);
					this.resourceUpdateFn = function(evt,updatedKeys){
						if(updatedKeys.indexOf('data')!==-1) self.update();
					};
					
					sensor.on('updated', this.resourceUpdateFn);
					update();
				},
				
				destroy: function(){
					sensor.off('updated', this.resourceUpdateFn);
					widget.destroy.call(this);
				}
				
			});
			
		}
		
	};
	
}));