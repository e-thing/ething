(function(){
	
	
	Header.setMobileTitle('Device');
	
	var notFound = function(){
		$(function() {
			$('body')
				.html('<div class="jumbotron"><h1>Error 404</h1><p>This device was not found !</p></div>')
				.addClass("container")
				.css({
					'margin-top':'20px',
					'margin-bottom':'20px'
				});
		});
	};
	
	window.main = function() {
		
		var p = function(device){
			
			$('#main').deviceViewer({
				device: device
			});
			
		}
		
		var rArg = EThing.utils.getParameterByName('r');
		
		if(rArg && EThing.utils.isId(rArg)){
			EThing.get(rArg)
				.done(p)
				.fail(notFound);
		} else notFound();
	};
	
})()