(function (root, factory) {
    if (typeof define === 'function' && define.amd) {
        // AMD. Register as an anonymous module.
        define(['jquery', 'ething', 'form'], factory);
    }
}(this, function ($, EThing) {
	
	return {
		
		'bases': ['MihomeDevice'],
		
		'name': 'MiHome Humidity Temperature and Pressure sensor',
		
		'creatable' : false
		
	}
}))