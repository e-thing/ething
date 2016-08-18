(function(){
		
	function getParameterByName(name) {
		name = name.replace(/[\[]/, "\\[").replace(/[\]]/, "\\]");
		var regex = new RegExp("[\\?&]" + name + "=([^&#]*)"),
			results = regex.exec(location.search);
		return results === null ? "" : decodeURIComponent(results[1].replace(/\+/g, " "));
	};
	
	var from = getParameterByName('from');
	if(from)
		from += window.location.hash;
	else
		from = 'explore.html';
	
	$(function() {
		$( "#signin-form" ).submit(function( event ) {
			
			$("#access-err").hide(100);
			
			EThing.auth.login($('#login').val(),$('#pass').val())
				.done(function(){
					window.location.replace(from);
				})
				.fail(function(){
					$("#access-err").show(100);
				});
			
			event.preventDefault();
		});
	});
	
})()
