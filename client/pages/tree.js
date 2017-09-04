(function (root, factory) {
    if (typeof define === 'function' && define.amd) {
        // AMD. Register as an anonymous module.
        define(['js/ui', 'jquery', 'tree'], factory);
    }
}(this, function (UI, $, Tree) {
	
	return {
		
		buildView: function(data){
			
			var $template = this.$template = UI.Container.set('<div>');
			
			Tree($template);
			
		},
		
		deleteView: function(){
			
		}
	};
}));