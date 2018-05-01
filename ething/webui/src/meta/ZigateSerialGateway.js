(function (root, factory) {
    if (typeof define === 'function' && define.amd) {
        // AMD. Register as an anonymous module.
        define(['jquery', 'ething', 'form'], factory);
    }
}(this, function ($, EThing) {
	
	return {
		
		'bases': ['ZigateGateway'],
		
		'name': 'Zigate Serial Gateway',
		
		'path' : ['Zigate', 'Gateway', 'Serial'],
		
		'properties' : {
			"port": {
				editable: function(){
					return $.getJSON('/api/utils/serial_ports_list').then(function(ports){
						
						return new $.Form.Text({
							placeholder: '/dev/ttyS0',
							validators: [$.Form.validator.NotEmpty],
							comboboxValues: ports.map(function(port){
								return {
									'name': port.device,
									'label': port.device+' <small style="color:grey;">'+(port.product || port.description)+(port.manufacturer ? (', '+port.manufacturer) : '')+'</small>'
								};
							})
						});
						
					});
					
				}
			}
		}
	}
}))