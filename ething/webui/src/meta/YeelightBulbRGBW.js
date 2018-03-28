(function (root, factory) {
    if (typeof define === 'function' && define.amd) {
        // AMD. Register as an anonymous module.
        define(['jquery', 'ething', 'form'], factory);
    }
}(this, function ($, EThing) {
	
	return {
		
		'bases': ['Device'],
		
		'name': 'Yeelight RGBW Bulb',
		
		'path' : ['Yeelight', 'LED Bulb (Color)'],
		
		'properties' : {
			"host": {
				editable:function(){
					return new $.Form.LocalIpSelect({
						validators: [$.Form.validator.NotEmpty],
						placeholder: "IP address"
					});
				},
				description: 'The IP address or hostname of the device.'
			}
		}
	}
}))