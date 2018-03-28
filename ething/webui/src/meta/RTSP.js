(function (root, factory) {
    if (typeof define === 'function' && define.amd) {
        // AMD. Register as an anonymous module.
        define(['jquery', 'ething', 'form'], factory);
    }
}(this, function ($, EThing) {
	
	return {
		
		'bases': ['Device'],
		
		'icon': '<path transform="scale(0.05) translate(120,120)" stroke-width="0" d="M395.928,187.794l-272.1-135.687c-5.358-2.669-11.866-0.494-14.538,4.864L51.24,173.379 c-1.283,2.573-1.491,5.55-0.579,8.276c0.912,2.727,2.869,4.979,5.443,6.262l81.242,40.511l-7.208,14.455    c-2.671,5.358-0.494,11.866,4.864,14.538l2.561,1.278l-13.998,24.929H41.027C33.351,268.782,17.867,258.626,0,258.626v92.338 c17.454,0,32.642-9.688,40.49-23.978h95.766c7.838,0,15.065-4.229,18.903-11.063l21.255-37.85l3.695,1.842 c5.357,2.671,11.867,0.493,14.539-4.863l7.208-14.455l60.7,30.271c3.501,1.746,7.671,1.471,10.911-0.723l16.753-11.332 l29.912,14.916c1.518,0.758,3.174,1.14,4.837,1.14c1.159,0,2.32-0.188,3.439-0.562c2.727-0.91,4.979-2.869,6.262-5.441 l30.624-61.413l31.757-20.903c3.239-2.132,5.092-5.832,4.86-9.702C401.679,192.976,399.397,189.525,395.928,187.794z"/>',
		
		'name': 'IP camera',
		
		'path' : ['IP camera'],
		
		'properties' : {
			"url": {
				editable:function(){
					
					var url_re = new RegExp('^((.+:)?\\/\\/)?'+ // protocol
						'((([a-z\\d]([a-z\\d-]*[a-z\\d])*)\\.)+[a-z]{2,}|'+ // domain name
						'((\\d{1,3}\\.){3}\\d{1,3})|'+ // OR ip (v4) address
						'localhost)'+ // or localhost
						'(\\:\\d+)?(\\/[-a-z\\d%_.~+]*)*'+ // port and path
						'(\\?[;&a-z\\d%_.~+=-]*)?'+ // query string
						'(\\#[-a-z\\d_]*)?$','i'); // fragment locator
				
					return new $.Form.Text({
						prefix: 'rtsp://',
						validators: [$.Form.validator.NotEmpty, function(value){
							if(!url_re.test('rtsp://'+value)) throw 'invalid URL';
						}],
						placeholder: "hostname:port/path",
						format:{
							'in': function(value){
								return value.replace(/^rtsp:\/\//, '');
							},
							'out': function(value){
								return 'rtsp://'+value;
							}
						}
					});
				},
				description: 'The url of the device.'
			},
			"transport": {
				editable:function(){
					return new $.Form.Select(['tcp','udp','http']);
				},
				description: 'Lower transport protocol.'
			}
		},
		
		'widget': 'RTSP'
	}
}))