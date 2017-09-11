(function (factory) {
	// AMD.
	define(['jquery','ething','form','ui/resourceselect'], factory);
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
					name: 'resource',
					label: 'source',
					item: new $.Form.ResourceSelect({
						filter: function(r){
							return ((r instanceof EThing.File) && (/image/i.test(r.mime()) || /jpg|jpeg|png|gif|bmp|tif/i.test(r.extension()))) || r instanceof EThing.Device;
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
									}, 3);
									
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
		
		require: ['widget/Widget','imageviewer'],
		
		instanciate: function(options, Widget){
			
			options = $.extend(true,{
				resource: null, // either a device or a file
				operation: null, // operation id if the resource is a Device
				parameters: null // optional parameters if the resource is a Device
			}, defaultOptions, options);
			
			var resource = EThing.arbo.findOneById(options.resource);
			if(!resource)
				throw 'The resource does not exist anymore';
			
			var imageViewerOptions = {
				header: {
					enable: true,
					showOnHover: true
				}
			};
			
			if(resource instanceof EThing.File){
				imageViewerOptions.elements = [resource];
			}
			else if(resource instanceof EThing.Device){
				
				imageViewerOptions.elements = [{
					name: resource.basename()+':'+options.operation,
					content: function(){
						return resource.execute(options.operation, options.parameters, true);
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