(function (root, factory) {
    if (typeof define === 'function' && define.amd) {
        // AMD. Register as an anonymous module.
        define(['jquery', 'ething', 'form'], factory);
    }
}(this, function ($, EThing) {
	
	return {
		
		'bases': ['Device'],
		
		'icon': '<text x="16" y="20" font-size="10" font-family="Bookman Old Style" text-anchor="middle">SSH</text>',
		
		'name': 'SSH',
		
		'path' : ['SSH'],
		
		'properties' : {
			"auth": {
				label: 'authentication',
				formatter: function(v){
					if(v){
						return v.user+':***';
					}
				},
				isOptional: true,
				editable: function(){
					return new $.Form.FormLayout({
						items:[
							{
								name: 'user',
								item: new $.Form.Text({
									validators: [$.Form.validator.NotEmpty],
									placeholder: 'user'
								})
							},{
								name: 'password',
								item: new $.Form.Text({
									password: true,
									validators: [$.Form.validator.NotEmpty],
									placeholder: 'password'
								})
							}
						]
					});
				}
			},
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
				default: 22,
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