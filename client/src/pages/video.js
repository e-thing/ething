(function (root, factory) {
    if (typeof define === 'function' && define.amd) {
        // AMD. Register as an anonymous module.
        define(['ui/core', 'jquery', 'ething'], factory);
    }
}(this, function (UI, $, EThing) {
	
	return function(data){
		
		var resource = EThing.arbo.findOneById(data.rid);
		
		if(resource){
			UI.Header.setTitle(resource.basename());
			
			UI.Container.set($('<div>').append($('<video controls style="width: 100%;">').append($('<source>').attr('src', resource.getContentUrl(true)).attr('type', resource.mime()))));
		} else {
			UI.show404();
		}
		
	};
	
}));