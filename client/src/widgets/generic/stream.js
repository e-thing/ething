(function (factory) {
	// AMD.
	define(['jquery','ething','form','ui/devicerequest'], factory);
}(function ($, EThing, Form) {


	
	var defaultOptions = {
		
	};
	
	
	return {
		
		description: 'Display a MJPEG stream from a device.',
		
		// must return a function which returns an options object
		factory: function(container, preset){
			
			preset = $.extend(true,{}, defaultOptions, preset);
			
			var form = new $.Form(container,new $.Form.DeviceRequest({
				acceptedMimeType: 'video/x-motion-jpeg'
			}), preset);
			
			return function(){
				return form.submit();
			}
		},
		
		require: ['widget/Widget','imageviewer'],
		
		instanciate: function(options, Widget){
			
			options = $.extend(true,{}, defaultOptions, options);
			
			var resource = EThing.arbo.findOneById(options.device);
			if(!resource)
				throw 'The resource does not exist anymore';
			
			var imageViewerOptions = {
				header: {
					enable: true,
					showOnHover: true
				}
			};
			
			if(resource instanceof EThing.Device){
				
				// load the image through a <img/> tag
				// this way, a MJPEG stream will work !
				
				var image = new Image(),
					ts = new Date().getTime(), // just to avoid caching
					url = resource.executeUrl(options.operation, options.parameters || null);
				url += url.indexOf('?') !== -1 ? '&' : '?';
				url += '_ts='+encodeURIComponent(ts);
				image.src = url;
				
				imageViewerOptions.elements = [{
					name: resource.basename()+':'+options.operation,
					content: image
				}];
			}
			
			
			var $iv;
			
			var widget = $.extend(Widget(), {
				
				draw: function(){
					
					$iv = $('<div>').css({
						'height': '100%',
						'background-color': '#ffffff',
						'color': '#4e4e4e'
					}).imageViewer(imageViewerOptions).appendTo(this.$element);
				},
				
				destroy: function(){
					$iv.imageViewer('destroy');
				}
				
			});
			
			
			return widget;
			
			
		}
	};
	
}));