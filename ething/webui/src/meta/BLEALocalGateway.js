(function (root, factory) {
    if (typeof define === 'function' && define.amd) {
        // AMD. Register as an anonymous module.
        define(['jquery', 'ething', 'form'], factory);
    }
}(this, function ($, EThing) {
	
	return {
		
		'bases': ['BleaGateway'],
		
		'name': 'BLEA local gateway',
		
		'path' : ['Blea', 'Local gateway'],
		
		'properties' : {
			"device": {
				default: 'hci0',
				editable:function(){
					return new $.Form.Text({
						placeholder: 'hci0',
						validators: [$.Form.validator.NotEmpty]
					});
				},
				description: 'The name of the bluetooth device. Usually hci0.'
			}
		}
	}
}))