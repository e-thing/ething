(function (root, factory) {
    if (typeof define === 'function' && define.amd) {
        // AMD. Register as an anonymous module.
        define(['jquery', 'ething', 'form'], factory);
    }
}(this, function ($, EThing) {
	
	return {
		
		'bases': ['MySensorsGateway'],
		
		'name': 'MySensors Ethernet Gateway',
		
		'path' : ['MySensors', 'Gateway', 'Ethernet'],
		
		'properties' : {
			"address": {
				editable: function(){
					return new $.Form.Text({
						placeholder: '192.168.1.116:5003',
						validators: [$.Form.validator.NotEmpty, function(value){
							if(!/^(([0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3})|([\w-.]+))(:[0-9]{1,5})?$/.test(value))
								throw 'invalid address';
						}]
					});
				}
			}
		}
	}
}))