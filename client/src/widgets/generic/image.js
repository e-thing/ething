(function (factory) {
	// AMD.
	define(['jquery','ething','form','ui/datasource'], factory);
}(function ($, EThing, Form) {

	
	var defaultOptions = {
		
	};
	
	
	
	
	return {
		
		description: 'Display an image comming from either a file or a device (e.g. the latest picture of an IP camera).',
		
		// must return a function which returns an options object
		factory: function(container, preset){
			
			preset = $.extend(true,{}, defaultOptions, preset);
			
			var form = new $.Form(container,new $.Form.FormLayout({
				items:[{
					name: 'source',
					item: new $.Form.DataSource({
						fileContent: {
							filter: function(r){
								return /image/i.test(r.mime()) || /jpg|jpeg|png|gif|bmp|tif/i.test(r.extension());
							}
						},
						deviceRequest: {
							acceptedMimeType: 'image/*'
						}
					})
				}]
			}), preset);
			
			return function(){
				return form.submit();
			}
		},
		
		require: ['widget/Widget','imageviewer'],
		
		instanciate: function(options, Widget){
			
			options = $.extend(true,{}, defaultOptions, options);
			
			var resource = EThing.arbo.findOneById(options.source.resource || options.source.device);
			if(!resource)
				throw 'The resource does not exist anymore';
			
			var imageViewerOptions = {
				header: {
					enable: true,
					showOnHover: true
				}
			};
			
			var dataType = (options.source.type || '');
			
			if(dataType === 'file.content'){
				imageViewerOptions.elements = [resource];
			}
			else if(dataType === 'device.request'){
				
				var operation = options.source.operation;
				var parameters = options.source.parameters || null;
				
				imageViewerOptions.elements = [{
					name: resource.basename()+':'+operation,
					content: function(){
						return resource.execute(operation, parameters, true);
					}
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