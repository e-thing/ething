(function (root, factory) {
    if (typeof define === 'function' && define.amd) {
        // AMD. Register as an anonymous module.
        define(['ui/core', 'text!./error404.html', 'css!./error404'], factory);
    }
}(this, function (UI, template) {
	
	return function(){
		UI.Container.set(template);
	};
	
}));