(function (root, factory) {
    if (typeof define === 'function' && define.amd) {
        // AMD. Register as an anonymous module.
        define(['jquery', 'ething', 'form'], factory);
    }
}(this, function ($, EThing) {
	
	return {
		'icon': '<g transform="scale(0.03) translate(220,220)" stroke-width="0"><path d="M178.624,242.367c-38.651,0-58.198,30.622-58.198,63.656c0,32.971,19.563,63.623,58.198,63.623c38.619,0,58.23-30.67,58.23-63.623C236.854,272.99,217.227,242.367,178.624,242.367z M178.624,351.625c-26.989,0-38.333-23.277-38.333-45.584c0-22.356,11.344-45.632,38.333-45.632c26.989,0,38.333,23.276,38.333,45.632C216.958,328.348,205.613,351.625,178.624,351.625z"/><path d="M592.611,136.855H19.436C8.711,136.855,0,145.518,0,156.26v299.511c0,10.758,8.711,19.389,19.436,19.389h573.175c10.726,0,19.404-8.631,19.404-19.389V156.26C612,145.518,603.321,136.855,592.611,136.855z M436.01,251.062h23.244v116.412H436.01V251.062z M38.793,175.665h264.113v260.701H38.793V175.665z"/></g>'
	}
}))