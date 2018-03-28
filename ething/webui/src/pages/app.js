(function (root, factory) {
    if (typeof define === 'function' && define.amd) {
        // AMD. Register as an anonymous module.
        define(['ui/core', 'text!./app.html', 'ething'], factory);
    }
}(this, function (UI, template, EThing) {
	
	
	return function(data){
		
		var resource = EThing.arbo.findOneById(data.appid);
		
		if(!resource){
			UI.show404();
			return;
		}
		
		UI.Container.set(template).addClass('ui-container-absolute');
		
		//Header.setMobileTitle('app');
		
		var iframe = document.getElementById('sandboxFrame');
		iframe.src = EThing.toApiUrl('/apps/'+data.appid+'?exec=1', true);
		
		
	
	};
}));