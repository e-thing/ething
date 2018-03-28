(function (root, factory) {
    if (typeof define === 'function' && define.amd) {
        // AMD. Register as an anonymous module.
        define(['jquery', 'ething', 'form'], factory);
    }
}(this, function ($, EThing) {
	
	return {
		
		'bases': ['RFLinkGateway'],
		
		'name': 'RFLink Serial Gateway',
		
		'path' : ['RFLink', 'Gateway', 'Serial'],
		
		'properties' : {
			"port": {
				editable: function(){
					return $.getJSON('../utils/serial_ports_list').then(function(ports){
						
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
			},
			"baudrate": {
				editable: function(resource){
					return new $.Form.Select({
						items: [
							110,
							150,
							300,
							600,
							1200,
							2400,
							4800,
							9600,
							19200,
							38400,
							57600,
							115200
						],
						value: 57600
					});
				}
			}
		}
	}
}))