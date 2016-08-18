(function(){
	
	
	
	window.main = function() {
		
		$('#device-add-btn').click(function(){
			EThing.ui.createDevice(function(){
				location.reload();
			});
		});
		
		var addKeyToTable = function(name, apikey){
			$('tbody','table#apikey-table').append(
				$('<tr>').append(
					'<td>'+name+'</td>',
					'<td>'+apikey.key+'</td>',
					'<td>'+EThing.utils.dateToString(apikey.createdDate)+'</td>'
				)
			);
		}
		
		EThing.list('type == "Device"').done(function(rs){
			
			var $tbody = $('tbody','table#apikey-table');
			
			if(!rs.length){
				
				$tbody.html(
					$('<tr>').html(
						$('<td colspan="3" class="text-center">').append(
							'<p>empty ! Create a device first !</p>'
						)
					)
				);
				
				return;
			}
			
			$tbody.empty();
				
			rs.forEach(function(r){
				
				EThing.request('/'+r.type().toLowerCase()+'/'+r.id()+'/apikey',function(data,status){
						addKeyToTable('<span style="color:grey;">'+r.type()+':</span>'+r.name(),data);
					});
				
			});
			
		});
		
		
	};
	
})()