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
					name: 'resource',
					label: 'source',
					item: new $.Form.ResourceSelect({
						filter: function(r){
							return ((r instanceof EThing.File) && (/ogg|mp4/i.test(r.extension()) || !!(videoElement.canPlayType && videoElement.canPlayType(r.mime()).replace(/no/, '')))) || r instanceof EThing.Device;
						},
						validators: [$.Form.validator.NotEmpty]
					})
				},{
					name: 'operation',
					item: new $.Form.Select(),
					dependencies: {
						'resource': function(layoutItem){
							var r = EThing.arbo.findOneById(this.getLayoutItemByName('resource').item.value());
							layoutItem.item.setOptions( r instanceof EThing.Device ? r.operations() : []);
							return r instanceof EThing.Device;
						}
					}
				}],
				onload: function(){
					
					var self = this;
					var resourceForm = this.getLayoutItemByName('resource').item;
					var operationForm = this.getLayoutItemByName('operation').item;
					var id = 0;
					
					function update(){
						
						var resource = EThing.arbo.findOneById(resourceForm.value());
						var operation = operationForm.value();
						var id_ = ++id;
						
						self.removeItem('parameters');
						
						if(resource instanceof EThing.Device && operation){
							
							// get the json schema specification for this operation
							resource.getApi(operation).done(function(api){
								
								if(api.schema && id_ === id){
									
									var layoutitem = self.addItem({
										name: 'parameters',
										item: Form.fromJsonSchema(api.schema)
									});
									
									if(preset && preset.operation === operation){
										layoutitem.item.value(preset.parameters);
									}
								}
								
							});
							
						}
						
					}
					
					operationForm.change(update);
					resourceForm.change(update).change();
					
				}
			}), preset);
			
			
			return function(){
				return form.submit();
			}
		},
		
		require: ['widget/Widget'],
		
		instanciate: function(options, Widget){
			
			options = $.extend(true,{
				resource: null, // either a device or a file
				operation: null, // operation id if the resource is a Device
				parameters: null // optional parameters if the resource is a Device
			}, defaultOptions, options);
			
			var resource = EThing.arbo.findOneById(options.resource);
			if(!resource)
				throw new Error('The resource does not exist anymore');
			
			var url = null;
			
			if(resource instanceof EThing.File){
				url = resource.getContentUrl(true);
			}
			else if(resource instanceof EThing.Device){
				url = resource.executeUrl(options.operation, options.parameters);
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
					
					this.$element.html($video);
					
				}
				
			});
			
			
			
			
			return widget;
			
		}
	};
	
}));