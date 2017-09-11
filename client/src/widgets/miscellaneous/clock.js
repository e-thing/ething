(function (factory) {
	// AMD.
	define(['jquery','ething','form','ui/resourceselect'], factory);
}(function ($, EThing, Form) {
	
	
	return {
		description: 'Draw a clock.',
		
		
		require: ['widget/Label'],
		
		instanciate: function(options, Label){
			
			
			var update = function(){
				var currentdate = new Date();
				var monthNames = [ "Jan", "Feb", "Mar", "Apr", "May", "Jun","Jul", "Aug", "Sep", "Oct", "Nov", "Dec" ];
				var min = currentdate.getMinutes();
				widget.val(currentdate.getHours()+':'+((min<10) ? ('0'+min) : min)+'<div style="font-size:20px;">'+currentdate.getDay()+' '+monthNames[currentdate.getMonth()]+'</div>');
			};
			
			
			var label = Label();
			
			var widget = $.extend({}, label, {
				
				draw: function(){
					label.draw.call(this);
					this.timerId = setInterval(update, 1000);
				},
				
				destroy: function(){
					label.destroy.call(this);
					clearInterval(this.timerId);
				}
				
			});
			
			
			
			return widget;
		}
	};
	
}));