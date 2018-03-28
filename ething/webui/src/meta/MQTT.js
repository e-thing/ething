(function (root, factory) {
    if (typeof define === 'function' && define.amd) {
        // AMD. Register as an anonymous module.
        define(['require', 'jquery', 'ething', 'form'], factory);
    }
}(this, function (require, $, EThing) {
	
	return {
		
		'bases': ['Device'],
		
		'icon': '<g transform="scale(0.08)"><text font-weight="bold" stroke-width="0" stroke-opacity="null" fill-opacity="null" x="92.86185" y="263.57692" font-size="24" font-family="Helvetica, Arial, sans-serif" text-anchor="start" xml:space="preserve" transform="matrix(3.761095958998766,0,0,3.710528337381942,-276.3656812632361,-615.3815860358596) " stroke="#000">MQTT</text><ellipse  cx="200" cy="200" id="svg_4" rx="34.5" ry="35"/><path stroke-width="0" transform="rotate(-45 145.000503540039,144.98031616210938) " d="m222.08805,165.16902c-0.87301,0 -1.74602,-0.34873 -2.41442,-1.03908c-41.17474,-42.97246 -108.17833,-42.96534 -149.35307,0c-1.32998,1.38782 -3.49204,1.38782 -4.82202,0s-1.32998,-3.64391 0,-5.03172c43.8347,-45.74809 115.16242,-45.74097 159.00393,0c1.32998,1.38782 1.32998,3.64391 0,5.03172c-0.6684,0.69035 -1.54141,1.03908 -2.41442,1.03908z"/><path stroke-width="0" transform="rotate(-45 124.50050354003898,123.48031616210935) " d="m225.28782,149.32539c-1.14141,0 -2.28283,-0.44644 -3.15671,-1.3302c-53.83351,-55.01224 -141.43665,-55.00312 -195.27016,0c-1.73886,1.77664 -4.56563,1.77664 -6.3045,0s-1.73886,-4.66484 0,-6.44148c57.31123,-58.56553 150.56793,-58.55643 207.88808,0c1.73886,1.77664 1.73886,4.66483 0,6.44148c-0.87389,0.88377 -2.0153,1.3302 -3.15671,1.3302z"/><path stroke-width="0" transform="rotate(-45 103.50049591064449,103.98033142089841) " d="m227.64904,136.54232c-1.40596,0 -2.81195,-0.56247 -3.88838,-1.67591c-66.31143,-69.30947 -174.21987,-69.29799 -240.5313,0c-2.14189,2.23836 -5.62388,2.23836 -7.7658,0s-2.14189,-5.87719 0,-8.11557c70.59525,-73.78623 185.46766,-73.77477 256.07388,0c2.14191,2.23837 2.14191,5.87717 0,8.11557c-1.07645,1.11344 -2.48242,1.67591 -3.88839,1.67591z"/></g>',
		
		'name': 'MQTT',
		
		'path' : ['MQTT'],
		
		'properties' : {
			"host": {
				editable:function(){
					return new $.Form.Text({
						validators: [$.Form.validator.NotEmpty],
						placeholder: "hostname"
					});
				},
				description: 'The hostname of the MQTT broker.'
			},
			"port": {
				default: 1883,
				editable:function(){
					return new $.Form.Number({
						validators: [$.Form.validator.Integer],
						placeholder: "port",
						value: 1883,
						minimum: 1,
						maximum: 65535,
					});
				},
				description: 'The port number of the MQTT broker.'
			},
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
			"subscription": {
				category: 'subscription',
				label: 'topic subscription',
				get: undefined, // only editable
				isOptional: false,
				editable:function(){
					
					var resource = this.resource;
					
					var jsonPathLibDfr = $.Deferred();
					require(['jsonpath'], function(JsonPath){
						jsonPathLibDfr.resolve(JsonPath);
					});
					
					var value=null;
					
					if(resource instanceof EThing.Device){
						value = $.Deferred();
						
						EThing.Device.MQTT.getSubscription(resource).then(function(subs){
							value.resolve(subs);
						}, function(){
							value.resolve([]);
						});
					}
					
					return $.when(
						value,
						jsonPathLibDfr
					).then(function(subs, JsonPath){
						
						return new $.Form.ArrayLayout({
							items: [],
							editable: true,
							value: subs,
							instanciator: function(){
								return new $.Form.FormLayout({
									items: [{
										name: 'topic',
										item: new $.Form.Text({
											validators: [$.Form.validator.NotEmpty],
											placeholder: "topic"
										})
									},{
										name: 'contentType',
										label: 'content type',
										item: new $.Form.Select({
											items: {
												'none <span style="color:grey;">(no data are stored)</span>': null,
												'JSON' : 'application/json',
												'text' : 'text/plain',
												'XML' : 'application/xml'
											}
										})
									},{
										name: 'jsonPath',
										label: 'JSON path',
										description: 'Retrieve the value from a JSON payload by locating a JSON Element using a JSON path expression.',
										item: new $.Form.Text({
											validators:[function(v){
												if(v){
													JsonPath.parse(v);
												}
											}]
										}),
										dependencies: {
											'contentType': function(currentlayoutItem, dependentLayoutItem){
												return dependentLayoutItem.item.value() === 'application/json';
											}
										}
										
									},{
										name: 'regexp',
										label: 'Regular Expression',
										description: 'Retrieve the value from a text payload by locating an element using a regular expression expression.',
										item: new $.Form.Text({
											placeholder: '/^startWith/i',
											validators:[function(v){
												if(v){
													var sep = v[0];
													var reEnd = new RegExp("\\"+sep+"[gimuy]*$");
													if(!(v.length>1 && reEnd.test(v.substr(1))))
														throw 'invalid regular expression';
												}
											}]
										}),
										dependencies: {
											'contentType': function(currentlayoutItem, dependentLayoutItem){
												return dependentLayoutItem.item.value() === 'text/plain';
											}
										}
									},{
										name: 'xpath',
										label: 'XPath Expression',
										description: 'Retrieve the value from a XML payload by locating an element using a XPath expression.',
										item: new $.Form.Text({}),
										dependencies: {
											'contentType': function(currentlayoutItem, dependentLayoutItem){
												return dependentLayoutItem.item.value() === 'application/xml';
											}
										}
									}]
								});
							}
						});
						
					});
				}
			}
		}
	}
}))