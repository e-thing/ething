(function (root, factory) {
    if (typeof define === 'function' && define.amd) {
        // AMD. Register as an anonymous module.
        define(['ui/core', 'jquery', 'tree', 'ui/infopanel', 'css!./tree'], factory);
    }
}(this, function (UI, $, Tree, Infopanel) {
	
	return {
		
		buildView: function(data){
			
			var $template = this.$template = UI.Container.set('<div>');
			
			Infopanel.enable();
				
			var open = function(resource){
				if(!UI.open(resource))
					alert('Unable to open this resource !');
			};
			
			var select = function(resource){
				Infopanel.setResource(resource);
			};
			
			var clickSave = { t: 0, r: null};
			
			this.tree = new Tree($template,{
				onopen: UI.isMobile() ? open : function(resource){
					var clickT = Date.now();
					if(clickT - clickSave.t < 200 && clickSave.r === resource){
						// db click
						open(resource);
						clickSave = { t: 0, r: null};
					}
					else {
						select(resource);
						clickSave = { t: clickT, r: resource};
					}
				}
			});
			
		},
		
		deleteView: function(){
			if(this.tree) this.tree.destroy();
		}
	};
}));