(function (root, factory) {
    if (typeof define === 'function' && define.amd) {
        // AMD. Register as an anonymous module.
        define(['jquery', 'ething', 'form'], factory);
    }
}(this, function ($, EThing) {
	
	return {
		
		'bases': ['BleaGateway'],
		
		'name': 'BLEA ethernet gateway',
		
		'path' : ['Blea', 'Ethernet gateway'],
		
		'description' : 'This device is used to connect to a distant bluetooth low energy gateway. To get it working, install first (on a raspberry pi for instance) this <a href="https://github.com/e-thing/ething/tree/master/resources/blead" target="_blank">project</a>.',
		
		'properties' : {
			"host": {
				editable:function(){
						return new $.Form.LocalIpSelect({
							validators: [$.Form.validator.NotEmpty],
							placeholder: "IP address"
						});
					},
					description: 'The IP address or hostname of the device.'
			},
			"port": {
				default: 5005,
				editable:function(){
					return new $.Form.Number({
						validators: [$.Form.validator.Integer],
						placeholder: "port",
						minimum: 1,
						maximum: 65535,
					});
				},
				description: 'The port number of the device.'
			}
		}
	}
}))