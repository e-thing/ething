(function (root, factory) {
    if (typeof define === 'function' && define.amd) {
        // AMD. Register as an anonymous module.
        define(['jquery'], factory);
    }
}(this, function ($) {
	
	
	return {
		
		require: ['widget/Buttons'],
		
		instanciate: function(sensor, options, Buttons){
			
			var widget = Buttons({
				buttons: [{
					label: 'On',
					onClick: function(){
						return sensor.execute('on').update(update);
					}
				},{
					label: 'Off',
					onClick: function(){
						return sensor.execute('off').update(update);
					}
				}],
				title: sensor.basename()
			});
			
			var setValue = function(value){
				widget.setActiveBtn(value ? 0 : 1);
				widget.setFooter(sensor.modifiedDate().toLocaleString());
			};
			
			var update = function(){
				var value = sensor.data('status');
				if(typeof value==='undefined'){
					if(sensor.operations().indexOf('getStatus') !== -1){
						sensor.execute('getStatus').done(setValue);
					}
				} else {
					setValue(value);
				}
			};
			
			return $.extend({}, widget, {
				
				draw: function(){
					var self = this;
					
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