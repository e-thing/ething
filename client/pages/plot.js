(function (root, factory) {
    if (typeof define === 'function' && define.amd) {
        // AMD. Register as an anonymous module.
        define(['js/ui', 'jquery', 'ething', 'ui/infopanel', 'plot'], factory);
    }
}(this, function (UI, $, EThing, Infopanel) {
	
	return {
		
		buildView: function(data){
			
			var resource = this.resource = EThing.arbo.findOneById(data.rid);
			
			if(resource){
				
				if(data.fields && typeof data.fields === 'string')
					data.fields = data.fields.split(',');
				
				data.fields = data.fields || resource.keys();
				
				if(data.fields.indexOf('date')===-1)
					data.fields.push('date');
				
				UI.Header.setTitle(resource.basename());
				
				Infopanel.enable();
				Infopanel.setResource(resource);
				
				var $element = UI.Container.set('<div class="ui-container-absolute">');
				
				$element.plot({
					data: function(){
						return resource.select({
							fields: data.fields,
							datefmt: 'TIMESTAMP_MS'
						});
					}
				});
				
				this.update = function(){
					$element.plot('refresh');
				};
				
				resource.on('updated', this.update);
				
				
			} else {
				UI.show404();
			}
		},
		
		deleteView: function(){
			
			if(this.resource){
				this.resource.off('updated', this.update);
			}
		}
		
	};
}));