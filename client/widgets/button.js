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
		title: 'Action !'
	};
	
	
	var Button = function(element,opt){
		
		var options = $.extend(true,{
			source: null
		}, defaultOptions, opt);
		
		var source = options.source;
		
		var $element = $(element), self = this, execute;
		
		var $error = $('<span class="glyphicon glyphicon-exclamation-sign" aria-hidden="true" ></span>').css({
			'color': '#d9534f',
			'position': 'absolute',
			'right': '10px',
			'top': '10px'
		}).appendTo($element).tooltip({
			title: function(){
				return $(this).data('error') || 'unknown error';
			},
			placement: 'bottom',
			html: true,
			template: '<div class="tooltip" role="tooltip"><div class="tooltip-arrow" style="border-bottom-color: #D9534F;"></div><div class="tooltip-inner" style="background-color: #D9534F;"></div></div>'
		}).hide();
		
		function setError(e){
			$error.data('error',e && e.message ? e.message : e);
			if(e===false)
				$error.hide().tooltip('hide');
			else
				$error.show();
		}
		
		var $button = $('<button type="button" class="btn btn-primary btn-lg">'+options.title+'</button>')
			.click(function(){
				if(typeof execute == 'function'){
					setError(false);
					var dfr = execute.call(self);
					if(dfr){
						$button.attr('disabled','disabled')
						$.when(dfr)
							.done(function(){
								$button.css({
									'background-color': '#5cb85c'
								});
							})
							.fail(function(e){
								console.log(e);
								
								$button.css({
									'background-color': '#d9534f'
								});
								setError(e);
							})
							.always(function(){
								$button.removeAttr('disabled')
								
								// restore color
								setTimeout(function(){
									$button.animate({
										'background-color': '#337ab7'
									},1000);
								},2000);
							});
					}
				}
			})
			.attr('disabled','disabled');
		
		var $wrapper = $('<div>').append($button).appendTo($element);
		
		$element.css({
			'display': 'table'
		});
		$wrapper.css({
			'display': 'table-cell',
			'vertical-align': 'middle',
			'text-align': 'center'
		});
		
		function setExecuteFn(fn){
			execute = fn;
			$button.removeAttr('disabled')
		}
		
		if(source.type == 'url'){
			
			var headers = {};
			if(Array.isArray(source.headers))
				source.headers.forEach(function(h){
					headers[h.header] = h.value;
				});
			
			setExecuteFn(function(){
				
				if(source.auth){
					headers['X-AUTH'] = encodeURIComponent(source.auth.type) + ';' + encodeURIComponent(source.auth.user) + ';' + encodeURIComponent(source.auth.password);
				}
				
				return EThing.request({
					method: source.method,
					url: 'proxy?url='+encodeURIComponent(source.url),
					data: source.body,
					headers: headers
				});
			})
			
		}
		else if(source.type == 'device'){
			
			// extract the content-type in the body parameter
			var requestContentType;
			for(var name in source.parameters){
				var param = source.parameters[name];
				if($.isPlainObject(param) && param.isRequestBodyParam===true){
					requestContentType = param.requestContentType;
					source.parameters[name] = param.requestBody;
				}
			}
			
			var deviceId = source.operation.deviceId,
				operationName = source.operation.operation;
			EThing.arbo.load(function(){
				var device = EThing.arbo.findOneById(deviceId);
				if(device){
					device.getSwaggerClient().done(function(client){
						if(client.operations.hasOwnProperty(operationName)){
							var operation = client.operations[operationName];
							setExecuteFn(function(){
								var dfr = $.Deferred();
								operation.execute(source.parameters, {
									requestContentType: requestContentType
									}, function(success){
										dfr.resolve(success.data);
									},
									function(error) {
										console.log('failed with the following: ', error);
										dfr.reject(error);
									});
								return dfr.promise();
							});
						}
					})
				}
			})
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
		require: '//cdnjs.cloudflare.com/ajax/libs/jquery-color/2.1.2/jquery.color.min.js',
		
		description: "Execute a request by clicking a button.",
		
		// must return a function which returns an options object
		factory: function(container, preset){
			
			preset = $.extend(true,{}, defaultOptions, preset);
			
			var form = new $.Form(container,
				new $.Form.FormLayout({
					merge: true,
					items:[{
						name: 'title',
						item: {
							input: 'text',
							validator: $.Form.validator.NotEmpty
						}
					},{
						name: 'source',
						item: new $.Form.SelectPanels({
								label: false,
								items: [{
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
															
															if(preset && preset.source.parameters && preset.source.operation && preset.source.operation.operation === operation)
																parametersForm.setValue(preset.source.parameters);
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
			new Button(element,options);
		}
	};
	
})()