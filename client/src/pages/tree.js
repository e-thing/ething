(function (root, factory) {
    if (typeof define === 'function' && define.amd) {
        // AMD. Register as an anonymous module.
        define(['ui/core', 'jquery', 'tree'], factory);
    }
}(this, function (UI, $, Tree) {
	
	return {
		
		buildView: function(data){
			
			var $template = this.$template = UI.Container.set('<div>');
			
			Tree($template,{
				onopen: function(resource){
					if(!UI.open(resource))
						alert('Unable to open this resource !');
				}
			});
			
		},
		
		deleteView: function(){
			
		}
	};
}));