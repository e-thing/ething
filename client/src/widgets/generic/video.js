(function (factory) {
	// AMD.
	define(['jquery','ething','form','ui/resourceselect'], factory);
}(function ($, EThing, Form) {

	
	var defaultOptions = {
		
	};
	
	
	
	
	return {
		
		description: 'Display a video comming from either a file or a custom URL. Only ogg or mp4 videos are compatible !',
		
		// must return a function which returns an options object
		factory: function(container, preset){
			
			preset = $.extend(true,{}, defaultOptions, preset);
			
			var videoElement = document.createElement('video');
			
			var form = new $.Form(container,new $.Form.FormLayout({
				items:[{
					name: 'source',
					item: new $.Form.DataSource({
						fileContent: {
							filter: function(r){
								return /ogg|mp4/i.test(r.extension()) || !!(videoElement.canPlayType && videoElement.canPlayType(r.mime()).replace(/no/, ''));
							}
						},
						deviceRequest: {
							acceptedMimeType: 'video/*'
						}
					})
				}]
			}), preset);
			
			
			return function(){
				return form.submit();
			}
		},
		
		require: ['widget/Widget'],
		
		instanciate: function(options, Widget){
			
			options = $.extend(true,{}, defaultOptions, options);
			
			var resource = EThing.arbo.findOneById(options.source.resource || options.source.device);
			if(!resource)
				throw new Error('The resource does not exist anymore');
			
			var url = null;
			
			var dataType = (options.source.type || '');
			
			if(dataType === 'file.content'){
				url = resource.getContentUrl(true);
			}
			else if(dataType === 'device.request'){
				
				var operation = options.source.operation;
				var parameters = options.source.parameters || null;
				
				url = resource.executeUrl(operation, parameters);
			}
			
			var widget = $.extend(Widget(), {
				
				draw: function(){
					
					var $video = $('<video controls>Your browser does not support the video tag.</video>').css({
						'max-width': '100%',
						'max-height': '100%',
						'display': 'block',
						'margin': 'auto'
					}).prepend(
						'<source src="'+url+'" type="video/mp4">',
						'<source src="'+url+'" type="video/ogg">'
					);
					
					this.$element.html($video).attr('style','display: -webkit-box;display: -moz-box;display: -ms-flexbox;display: -webkit-flex;display: flex;').css({
						'display': 'flex',
						'-webkit-flex-direction': 'column',
						'-moz-flex-direction': 'column',
						'-ms-flex-direction': 'column',
						'-o-flex-direction': 'column',
						'flex-direction': 'column',
						'justify-content': 'center'
					});
					
				}
				
			});
			
			
			
			
			return widget;
			
		}
	};
	
}));