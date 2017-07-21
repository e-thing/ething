(function (root, factory) {
    if (typeof define === 'function' && define.amd) {
        // AMD. Register as an anonymous module.
        define(['js/ui', 'text!./developer.html', 'jquery', 'ething', 'css!./developer'], factory);
    }
}(this, function (UI, template, $, EThing) {
	
	
	
	return function(){
		
		UI.Container.set(template);
		
		var addKeyToTable = function(name, apikey){
			$('tbody','table#apikey-table').append(
				$('<tr>').append(
					'<td data-title="Name">'+name+'</td>',
					'<td data-title="API key">'+apikey+'</td>'
				)
			);
		}
		
		var rs = EThing.arbo.find(function(r){
			return (r instanceof EThing.App) || r.type() === "Device\\Http";
		});
		
		if(!rs.length){
			
			$('table#apikey-table').replaceWith('<p class="text-center"><strong>empty ! Create a device first !</strong></p>');
			
			return;
		}
		
		
		
		$('tbody','table#apikey-table').empty();
			
		rs.forEach(function(r){
			
			addKeyToTable('<span style="color:grey;">'+r.type()+':</span>'+r.name(),r.json().apikey);
			
		});
		
	};
}));