(function(){
	
var contentTypesList = [
	"application/javascript",
	"application/json", 
	"application/xml", 
	"image/bmp", 
	"image/gif", 
	"image/jpeg", 
	"image/png", 
	"text/css", 
	"text/html", 
	"text/plain", 
	"text/xml"
];
var headersList = {
	"Accept": contentTypesList,
	"Accept-Charset": null,
	"Accept-Encoding": null,
	"Accept-Language": null,
	"Accept-Datetime": null,
	"Authorization": null,
	"Cache-Control": null,
	"Connection": ["keep-alive","close",""],
	"Cookie": null,
	"Content-Length": null,
	"Content-MD5": null,
	"Content-Type": contentTypesList,
	"Date": null,
	"Expect": null,
	"Forwarded": null,
	"From": null,
	"Host": null,
	"If-Match": null,
	"If-Modified-Since": null,
	"If-None-Match": null,
	"If-Range": null,
	"If-Unmodified-Since": null,
	"Max-Forwards": null,
	"Origin": null,
	"Pragma": null,
	"Proxy-Authorization": null,
	"Range": null,
	"Referer": null,
	"TE": null,
	"Transfer-Encoding": ["chunked", "compress", "deflate", "gzip", "identity"],
	"User-Agent": null,
	"Upgrade": null,
	"Via": null,
	"Warning": null
};
	
var sheet = document.createElement('style')
sheet.innerHTML = ".typeahead {max-height: 200px; overflow-y: auto;}";
document.body.appendChild(sheet);

	
	/*
	
	{
		"type": "url",
		"method": "GET",
		"url": "test",
		"auth': {
			"type": "",
			"user": "",
			"password": ""
		},
		"headers": [
			{
				"header": "head",
				"value": "value"
			}
		]
	}
	
	{
		"type": "device",
		"operation": {
			"deviceId": "71VLEuL",
			"operation": "get_pets"
		},
		"parameters":{
			"key": "value",
			"key2":{
				'requestContentType':'',
				'requestBody': '',
				'isRequestBodyParam': true
			}
		}
	}
	
	*/
	
	var defaultOptions = {
		
	};
	
	
	var ImageWidget = function(element,opt){
		
		var options = $.extend(true,{
			type: null, // 'device', 'url', 'file'
		}, defaultOptions, opt);
		
		var $element = $(element), self = this;
		
		function setContent(element){
			
			if(!$.isPlainObject(element) || typeof element.promise == 'function')
				element = {
					content: element
				};
			
			$('<div>').css({
				'height': '100%'
			}).imageViewer({
				elements: [element],
				header: {
					enable: true,
					showOnHover: true
				}
			}).appendTo($element);
		}
		
		if(options.type == 'url'){
			
			var headers = {}, auth, content;
			if(Array.isArray(options.headers))
				options.headers.forEach(function(h){
					headers[h.header] = h.value;
				});
			
			if(options.auth){
				auth = encodeURIComponent(options.auth.type) + ';' + encodeURIComponent(options.auth.user) + ';' + encodeURIComponent(options.auth.password);
			}
			
			if(/get/i.test(options.method) && Object.keys(headers).length == 0 && !options.body){
				// load the image through a <img/> tag
				// this way, a MJPEG stream will work !
				var url = 'proxy?url='+encodeURIComponent(options.url);
				if(auth)
					url += '&auth='+encodeURIComponent(auth);
				
				content = function(){
					var image = new Image(),
						ts = new Date().getTime(); // just to avoid caching
					image.src = EThing.utils.updateQueryStringParameter(EThing.toApiUrl(url,true),'_ts',ts);
					return image;
				};
			}
			else {
				if(auth) headers['X-AUTH'] = auth;
				content = function(){
					return EThing.request({
						method: options.method,
						url: 'proxy?url='+encodeURIComponent(options.url),
						data: options.body,
						headers: headers,
						dataType: 'blob'
					});
				};
			}
			
			setContent({
				content: content,
				name: options.url.split('/').pop().split('?').shift()
			});
			
		}
		else if(options.type == 'device'){
			
			// extract the content-type in the body parameter
			var requestContentType;
			for(var name in options.parameters){
				var param = options.parameters[name];
				if($.isPlainObject(param) && param.isRequestBodyParam===true){
					requestContentType = param.requestContentType;
					options.parameters[name] = param.requestBody;
				}
			}
			
			var deviceId = options.operation.deviceId,
				operationName = options.operation.operation;
			
			setContent({
				content: function(){
					var dfr = $.Deferred();
					
					EThing.arbo.load(function(){
						var device = EThing.arbo.findOneById(deviceId);
						if(device){
							device.getSwaggerClient().done(function(client){
								if(client.operations.hasOwnProperty(operationName)){
									var operation = client.operations[operationName];
									operation.execute(options.parameters, {
										requestContentType: requestContentType
										}, function(success){
											dfr.resolve(success.data);
										},
										function(error) {
											console.log('failed with the following: ', error);
											dfr.reject(error);
										});
								}
							}).fail(function(e){
								dfr.reject(e);
							});
						}
					});
					
					return dfr.promise();
				},
				name: operationName
			});
			
		}
		else if(options.type == 'file'){
			
			var fileId = options.fileId;
			
			setContent(EThing.get(fileId));
			
		}
		
	}
	
	
	
	var SwaggerParamTypeToFormStandardItem = function(type){
		var options = {
			input: 'text'
		};
		
		switch(type){
			case 'number':
			case 'integer':
				options.input = 'number';
				break;
			case 'string':
				options.input = 'text';
				break;
			case 'boolean':
				options.input = ['true','false'];
				options.get = function($input){
					return $input.val() == 'true';
				}
				break;
		}
		
		return new $.Form.StandardItem(options);
	}
	
	
	return {
		
		description: 'Display an image comming from either a file or a device (e.g. the latest picture of an IP camera) or a custom URL. If the source is a device or an URL, it is also possible to display a MJPEG stream.',
		
		// must return a function which returns an options object
		factory: function(container, preset){
			
			preset = $.extend(true,{}, defaultOptions, preset);
			
			var form = new $.Form(container,
				new $.Form.SelectPanels({
					name: 'source',
					items: [{
						name: 'file',
						item: new $.Form.FormLayout({
							items:[{
								label: 'file',
								name: 'fileId',
								item: new $.Form.ResourceSelect({
									filter: function(r){
										return (r instanceof EThing.File) && (/image/i.test(r.mime()) || /jpg|jpeg|png|gif|bmp|tif/i.test(r.extension()));
									}
								})
							}]
						})
					},{
						name: 'device',
						item: new $.Form.FormLayout({
							items:[{
								label: 'operation',
								item: new $.Form.DeviceOperationSelect({
									onChange: function(device,operation,swaggerClient){
										
										var operationApi = swaggerClient.operations[operation].api,
											parameters = operationApi.parameters,
											parametersForm = this.form().findItem('parameters');
										
										parametersForm.clear();
										
										parameters.forEach(function(parameter){
											var item;
											
											switch(parameter.in){
												case 'path':
												case 'query':
												case 'formData':
													item = SwaggerParamTypeToFormStandardItem(parameter.type);
													break;
												case 'body':
													item = new $.Form.FormLayout([{
														name: 'requestContentType',
														label: 'Content type',
														item: {
															input: operationApi.consumes || ['text/plain']
														}
													},{
														name: 'requestBody',
														label: 'body',
														item: 'textarea'
													},{
														name: 'isRequestBodyParam',
														item: {
															input: 'checkbox',
															value: true
														},
														hidden: true
													}]);
												default:
													// todo !
													break;
											}
											
											if(item){
												parametersForm.addItem(item,{
													name: parameter.name,
													checkable: !parameter.required,
													checked: parameter.required!==false,
													description: parameter.description
												});
												
												if(preset && preset.parameters && preset.operation && preset.operation.operation === operation)
													parametersForm.setValue(preset.parameters);
											}
										});
										
										parametersForm.parent().setVisible('parameters',!!parametersForm.length());
										
									}
								})
							},{
								label: 'parameters',
								item: new $.Form.FormLayout({
									name: 'parameters',
									items: []
								})
							}]
						})
					},{
						name: 'url',
						item: new $.Form.FormLayout({
							name: 'urlForm',
							items:[{
								name: 'method',
								item: new $.Form.Select({
									items: ['GET','POST','PUT','PATCH','DELETE'],
									onChange: function(method){
										this.form().findItem('urlForm').toggle('body',method!='GET');
									}
								})
							},{
								name: 'url',
								item: {
									input: 'text',
									validator: $.Form.validator.NotEmpty,
									attr:{
										placeholder: 'http://example.com'
									}
								}
							},{
								name: 'auth',
								label: 'authentication',
								item: new $.Form.FormLayout([{
									label: 'type',
									item: {
										input: ['basic','digest']
									}
								},{
									label: '_',
									item: '<input type="text" name="user_f5f7tyjh"/><input type="password" name="pass_f5f7tyjh"/>',
									hidden: true,
									skip: true
								},{
									label: 'user',
									item: {
										input: '<input type="text" placeholder="user" autocomplete="off">',
										validator: $.Form.validator.NotEmpty
									}
								},{
									label: 'password',
									item: {
										input: '<input type="password" placeholder="password" autocomplete="off">',
										validator: $.Form.validator.NotEmpty
									}
								}]),
								checkable: true,
								check: false
							},{
								name: 'headers',
								item: new $.Form.ArrayLayout({
									instanciator: function(){
										return new $.Form.FormLayout({inline: true, items: [{
											name: 'header',
											label: false,
											item: {
												input: function(){
													var $input = $('<input type="text">');
													
													EThing.utils.require('//cdnjs.cloudflare.com/ajax/libs/bootstrap-3-typeahead/4.0.1/bootstrap3-typeahead.min.js').done(function(){
														$input.typeahead({
															source: Object.keys(headersList),
															showHintOnFocus: true,
															items: 'all'
														});
													});
													
													return $input;
												},
												validator: $.Form.validator.NotEmpty,
												attr:{
													'placeholder': 'header'
												},
												on: {
													'change': function(){
														var header = this.getValue();
														if(header && headersList[header]){
															this.parent().findItem('value').input().typeahead({
																source: headersList[header],
																showHintOnFocus: true
															});
														}
													}
												}
											}
										},{
											name: 'value',
											label: false,
											item: {
												input: 'text',
												validator: $.Form.validator.NotEmpty,
												attr:{
													'placeholder': 'value'
												}
											}
										}]});
									}
								}),
								checkable: true,
								check: false
							},{
								name: 'body',
								item: 'textarea',
								checkable: true
							}]
						})
					}]
				})
			);
			
			if(preset)
				form.setValue(preset);
			
			
			
			return function(){
				return form.validate();
			}
		},
		
		instanciate: function(element, options){
			new ImageWidget(element,options);
		}
	};
	
})()