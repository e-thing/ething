(function (root, factory) {
    if (typeof define === 'function' && define.amd) {
        // AMD. Register as an anonymous module.
        define(['jquery', 'ething', 'form'], factory);
    }
}(this, function ($, EThing) {
	
	return {
		'icon': '<g transform="scale(0.6) translate(10,10)" ><path d="M21.59,23.694L21.59,23.694l-10.413-0.003c-0.253,0-0.467-0.189-0.497-0.441c-0.121-1.022-0.478-2.465-1.499-3.526c-0.001-0.002-0.002-0.003-0.004-0.005c-2.524-2.132-3.971-5.241-3.971-8.54C5.207,5.015,10.222,0,16.385,0s11.178,5.015,11.178,11.179c0,3.321-1.465,6.449-4.019,8.581c-0.98,1.026-1.337,2.47-1.458,3.493C22.058,23.505,21.844,23.694,21.59,23.694z M11.611,22.691l9.545,0.003c0.187-1.127,0.64-2.552,1.708-3.664c2.366-1.979,3.7-4.828,3.7-7.852C26.563,5.566,21.998,1,16.385,1S6.207,5.566,6.207,11.179c0,3.021,1.333,5.869,3.659,7.812c0.03,0.025,0.057,0.054,0.08,0.085C10.983,20.18,11.426,21.58,11.611,22.691z"/><path d="M21.59,26.718H11.177c-0.276,0-0.5-0.224-0.5-0.5s0.224-0.5,0.5-0.5H21.59c0.276,0,0.5,0.224,0.5,0.5S21.867,26.718,21.59,26.718z"/><path d="M21.59,29.744H11.177c-0.276,0-0.5-0.224-0.5-0.5s0.224-0.5,0.5-0.5H21.59c0.276,0,0.5,0.224,0.5,0.5S21.867,29.744,21.59,29.744z"/><path d="M18.564,32.771h-4.36c-0.276,0-0.5-0.224-0.5-0.5s0.224-0.5,0.5-0.5h4.36c0.276,0,0.5,0.224,0.5,0.5S18.84,32.771,18.564,32.771z"/></g>',
		
		'widget': 'Light'
	}
}))