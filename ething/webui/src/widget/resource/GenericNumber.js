(function (root, factory) {
    if (typeof define === 'function' && define.amd) {
        // AMD. Register as an anonymous module.
        define(['jquery', 'widget/base/Number'], factory);
    }
}(this, function ($, Number) {
	
	return {
		
		instanciate: function(sensor, options, Number){
			
			/*
			options = {
				property: 'temperature',
				unit: '&#8451;'
			}
			*/
			
			var widget = Number({
				unit : typeof options.unit === 'string' ? options.unit : null,
				title: sensor.basename()
			});
			
			var setValue = function(value){
				widget.val(value);
				widget.setFooter(sensor.modifiedDate().toLocaleString());
			};
			
			var update = function(){
				var value = sensor.data(options.property);
				if(typeof options.formatter === 'function')
					value = options.formatter.call(this, value);
				setValue( value );
				if(typeof options.unit === 'function')
					widget.setUnit(options.unit.call(this, value));
				
			};
			
			return $.extend({}, widget, {
				
				draw: function(){
					
					widget.draw.call(this);
					
					this.resourceUpdateFn = function(evt,updatedKeys){
						if(updatedKeys.indexOf('data')!==-1) update();
					};
					
					sensor.on('updated', this.resourceUpdateFn);
					update();
				},
				
				destroy: function(){
					if(this.resourceUpdateFn) sensor.off('updated', this.resourceUpdateFn);
					widget.destroy.call(this);
				}
				
			});
			
		}
		
	};
	
}));