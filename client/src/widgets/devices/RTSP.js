(function (root, factory) {
    if (typeof define === 'function' && define.amd) {
        // AMD. Register as an anonymous module.
        define(['jquery'], factory);
    }
}(this, function ($) {
	
	
	return {
		
		require: ['widget/Widget','imageviewer'],
		
		instanciate: function(device, options, Widget){
			
			
			var imageViewerOptions = {
				header: {
					enable: true,
					showOnHover: true
				},
				elements: [{
					name: '<span class="glyphicon glyphicon-facetime-video" aria-hidden="true"></span> '+device.basename(),
					content: function(){
						return device.execute('snapshot', null, true);
					}
				}]
			};
			
			
			var $iv, timerId;
			
			var widget = $.extend(Widget(), {
				
				draw: function(){
					
					$iv = $('<div>').css({
						'height': '100%',
						'background-color': '#ffffff',
						'color': '#4e4e4e'
					}).imageViewer(imageViewerOptions).appendTo(this.$element);
					
					timerId = setInterval(function(){
						$iv.imageViewer('refresh');
					}, 60000);
				},
				
				destroy: function(){
					$iv.imageViewer('destroy');
					clearInterval(timerId);
				}
				
			});
			
			return widget;
			
		}
		
	};
	
	
}));