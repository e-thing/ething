(function(){
		
	var getParameterByName = function(name) {
		name = name.replace(/[\[]/, "\\[").replace(/[\]]/, "\\]");
		var regex = new RegExp("[\\?&]" + name + "=([^&#]*)"),
			results = regex.exec(location.search);
		return results === null ? "" : decodeURIComponent(results[1].replace(/\+/g, " "));
	};
	
	var notFound = function(){
		$(function() {
			$('body')
				.html('<div class="jumbotron"><h1>Error 404</h1><p>This application was not found !</p></div>')
				.addClass("container")
				.css({
					'margin-top':'20px',
					'margin-bottom':'20px'
				});
		});
	};
	
	
	window.main = function(){
		// get the appId from the query string
		var appId = getParameterByName('appid');
		
		if(!(appId && EThing.utils.isId(appId)))
			return notFound();
		
		
		EThing.get(appId).done(function(app){
			Header.setMobileTitle(app.name());
			
			var frame = document.getElementById('sandboxFrame');
			
			frame.onload = function(){
				
				// update the displayed url according to the iframe url
				var queryString = this.contentWindow.location.search;
					
				queryString = queryString.replace(/[?&]access_token=[^&]*/,'');
				if(!queryString.length || queryString[0]!='?')
					queryString = '?'+queryString.replace(/^&/,'');
							
				history.replaceState(null, "", queryString);
				
			};
			
			frame.src = EThing.toApiUrl('app/'+appId, true) + '&' + window.location.search.replace(/^[?]/,'');
			
		}).fail(notFound);
		
	}
	
})()