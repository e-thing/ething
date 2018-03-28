(function (factory) {
	// AMD.
	define(['jquery','ething','form','ui/widget','imageviewer', 'ui/datasource'], factory);
}(function ($, EThing, Form, Widget) {

	
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
							acceptedMimeType: 'image/*',
							refreshPeriod: true
						}
					})
				}]
			}), preset);
			
			return function(){
				return form.submit();
			}
		},
		
		instanciate: function(options){
			
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
					
					var update = function(){
						$iv.imageViewer('refresh');
					}
					
					if(dataType === 'file.content'){
						this.onResourceUpdate = function(evt,updatedKeys){
							if(updatedKeys.indexOf('contentModifiedDate')!==-1) update();
						};
						resource.on('updated', this.onResourceUpdate);
					} else if(dataType === 'device.request'){
						this.refeshIntervalId = setInterval(update, (options.refreshPeriod || 30)*1000);
					}
					
				},
				
				destroy: function(){
					$iv.imageViewer('destroy');
					
					if(this.onResourceUpdate){
						resource.off('updated', this.onResourceUpdate);
					}
					if(this.refeshIntervalId){
						clearInterval(this.refeshIntervalId);
					}
				}
				
			});
			
			
			return widget;
			
			
		}
	};
	
}));