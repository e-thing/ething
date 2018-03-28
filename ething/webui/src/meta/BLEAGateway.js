(function (root, factory) {
    if (typeof define === 'function' && define.amd) {
        // AMD. Register as an anonymous module.
        define(['jquery', 'ething', 'form'], factory);
    }
}(this, function ($, EThing) {
	
	return {
		
		'bases': ['Device'],
		
		'icon': '<g transform="scale(0.4) translate(15,15)" stroke-width="0"><path d="M 24 1.5625 L 24 20.0625 L 16.46875 12.53125 L 13.65625 15.375 L 23.1875 24.875 L 13.625 34.46875 L 16.46875 37.28125 L 24 29.71875 L 24 48.5 L 27.40625 45.0625 L 36.78125 35.625 L 38.1875 34.21875 L 36.78125 32.8125 L 28.8125 24.875 L 36.75 16.90625 L 38.15625 15.5 L 36.71875 14.09375 L 27.40625 4.90625 Z M 28 11.09375 L 32.5 15.5 L 28 20.03125 Z M 28 29.6875 L 32.5625 34.21875 L 28 38.8125 Z "></path></g>',
		
		'name': 'BLEA Gateway',
		
		'creatable' : false,
		
		'properties' : {}
	}
}))