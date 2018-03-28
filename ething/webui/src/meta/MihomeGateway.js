(function (root, factory) {
    if (typeof define === 'function' && define.amd) {
        // AMD. Register as an anonymous module.
        define(['jquery', 'ething', 'form'], factory);
    }
}(this, function ($, EThing) {
	
	return {
		
		'bases': ['Device'],
		
		'name': 'MiHome gateway',
		
		'path' : ['MiHome'],
		
		'properties' : {
			"ip": {
				editable:function(){
					return new $.Form.Text({
						placeholder: '192.168.xx.xx',
						validators: [$.Form.validator.NotEmpty, function(value){
							if(!/^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?).(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?).(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?).(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/.test(value)) throw 'invalid IP address';
						}]
					});
				},
				description: 'The IP address of the device.'
			},
			"sid": {
				editable:function(){
					return new $.Form.Text({
						placeholder: 'SID',
						validators: [$.Form.validator.NotEmpty]
					});
				},
				description: 'The SID of the gateway.'
			},
			"password": {
				editable:function(){
					return new $.Form.Text({
						placeholder: 'password',
						validators: [$.Form.validator.NotEmpty]
					});
				},
				description: 'The password of the gateway. This password must retrieved from the MiHome app.'
			}
		}
	}
}))