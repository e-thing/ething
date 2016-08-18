(function(){
	
	$(window.document).ready(function() {
		
		if(!EThing.auth.isAuthenticated()){
			window.location.replace('signin.html?from='+encodeURIComponent(window.location.href));
		}
		else {
			EThing.auth.authorize(main || null);
		}
		
	});
	
})()