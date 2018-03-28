(function (root, factory) {
    if (typeof define === 'function' && define.amd) {
        // AMD. Register as an anonymous module.
        define(['jquery', 'ething', 'form'], factory);
    }
}(this, function ($, EThing) {
	
	return {
		
		'bases': ['Device'],
		
		'description' : 'See <a href="https://zigate.fr/" target="_blank">Zigate website</a>',
		
		'name': 'Zigate Gateway',
		
		'creatable' : false,
		
		'properties' : {
			"appVersion": {
				
			},
			"sdkVersion": {
				
			}
		}
	}
}))