(function(){
		
	
	return {
		
		description: "Display resource position on map.",
		
		// must return a function which returns an options object
		factory: function(container, preset){
			var form = new $.Form(container,{
				'resource': new $.Form.ResourceSelect({
					filter: function(r){
						return !!r.location();
					}
				})
			});
			
			if(preset)
				form.setValue(preset);
			
			return function(){
				return form.validate();
			}
		},
		
		instanciate: function(element, options){
			return EThing.get(options.resource).done(function(resource){
				new $.MapViewer(element,{
					resources: [resource]
				});
			});
		}
	};
	
})()