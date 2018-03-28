(function (root, factory) {
    if (typeof define === 'function' && define.amd) {
        // AMD. Register as an anonymous module.
        define(['require', 'jquery','form','ething','jsonpath','ui/resourceselect'], factory);
    }
}(this, function (require, $, Form, EThing, JsonPath) {
	
	
	
	function mimetypeMatch(a, b){
		
		if(typeof a !== 'string') return false;
		if(typeof b !== 'string') return false;
		
		if(a === '*/*' || a === '*' || b === '*/*' || b === '*' || a === b) return true;
		
		if(a.indexOf('*')!==-1) {
			var re = new RegExp('^'+a.replace('*','[^/]*')+'$','i');
			if(re.test(b)){
				return true;
			}
		}
		
		if(b.indexOf('*')!==-1) {
			var re = new RegExp('^'+b.replace('*','[^/]*')+'$','i');
			if(re.test(a)){
				return true;
			}
		}
		
		return false;
	}
	
	
	/*
	
	options:
		
		filter : function(resource) -> boolean 
		or
		deviceForm : an external ressourceSelect instance.
		
		onApiCall: function(device, operation, api) executed once the api is loaded.
		onchange: function(device, operation) executed once the tupple [device,operation] changed. The API may not be loaded !
		onload: function() is executed once the form is loaded.
		
		value: { device: <deviceId>, operation: <operationId> [, parameters: <parameters>]} the initial value
		
		acceptedMimeType: <mime> or [<mime>] , only the following mime types for the returned data will be allowed.
		
		jsonPath: Boolean , allow the user to specify a json path for request returning JSON data.
		regexp: Boolean , allow the user to specify a regular expression for request returning text data.
		xpath: Boolean , allow the user to specify a xpath expression for request returning XML data.
		
		refreshPeriod: Boolean , allow the user to specify a pooling refresh period
	
	returned value:
	
	{
		device: <deviceId>,
		operation: <operationId>
		parameters: <parameters> // optionnal
	}
	
	*/
	
	
	var DeviceRequest = function(options){
		
		options = options || {};
		
		var self = this;
		var id = 0;
		var cache = {};
		var deviceForm = null;
		var formItems = [];
		
		if(options.deviceForm) {
			if(typeof options.deviceForm != 'string') deviceForm = options.deviceForm;
		} else {
			deviceForm = new Form.ResourceSelect({
				filter: function(r){
					return r instanceof EThing.Device && (typeof options.filter != 'function' || options.filter.call(self, r));
				},
				validators: [Form.validator.NotEmpty]
			});
			
			formItems.push({ // device selection
				name: 'device',
				item: deviceForm
			});
		}
		
		var operationForm = new Form.Select({
			title: 'Select an operation',
			items: [],
			validators: [Form.validator.NotEmpty]
		});
		
		var operationFormIndex = formItems.length;
		
		formItems.push({
			name: 'operation',
			item: operationForm
		});
		
		
		
		
		if(options.refreshPeriod){
			
			formItems.push({
				label: 'refresh period',
				name: 'refreshPeriod',
				item: new Form.Select({
					items: {
						'5 secondes': 5,
						'10 secondes': 10,
						'30 secondes': 30,
						'1 minute': 60,
						'2 minutes': 120,
						'5 minutes': 300
					},
					validators: [Form.validator.NotEmpty],
					value: 30
				})
			});
			
		}
		
		
		function onDeviceChange(){
			
			var self = this;
			var device = EThing.arbo.findOneById(deviceForm.value());
			var operation = operationForm.value();
			var id_ = ++id;
			var deviceId = device instanceof EThing.Device ? device.id() : null;
			
			// update the operation list ! (only if necessary !)
			if(deviceId !== operationForm.assocDevice){
				
				self.setVisible(operationForm, device instanceof EThing.Device);
				
				operationForm.assocDevice = deviceId;
				operationForm.assocOperation = null;
				operationForm.clear();
				
				if(device instanceof EThing.Device){
					
					var cacheKey = device.id();
					
					// load the api
					if(cache[cacheKey]){
						loadApis(cache[cacheKey]);
					} else {
						device.getApi().done(function(apis){
							cache[cacheKey] = apis;
							loadApis(apis);
						});
					}
					
					function loadApis(apis){
						
						if(id_ === id){
							
							var operationOptions = {};
							
							apis.forEach(function(api){
								var key = api.name;
								if(api.response)
									key += ' <span class="small" style="color: grey;">'+api.response+'</span>';
								
								var rejected = false;
								var mimeType = api.response;
						
								if(options.acceptedMimeType){
									rejected = 'wrong mime type';
									var allowedMimeTypes = options.acceptedMimeType || [];
									if(!Array.isArray(allowedMimeTypes)) allowedMimeTypes = [allowedMimeTypes];
									
									for(var i in allowedMimeTypes){
										if(mimeType && allowedMimeTypes[i] && mimetypeMatch(allowedMimeTypes[i], mimeType)){
											rejected = false;
											break;
										}
									}
								}
								
								if(!rejected && typeof options.onApiCall === 'function'){
									try{
										if(options.onApiCall.call(self, device, api.name, api)===false)
											rejected = true;
									} catch(e){
										rejected = e.toString();
									}
								}
								
								if(rejected){
									key = '!'+key;
									if(typeof rejected === 'string') key += ' <span class="small" style="color: #a94442;">'+rejected+'</span>';
								}
								operationOptions[key] = api.name;
							});
							
							operationForm.setOptions(operationOptions);
							
							var preset = self.parent()._preset;
							if(preset && preset.device === deviceId){
								operationForm.value(preset.operation);
							}
							
						}
						
					}
					
				}
				
			}
			
		}
		
		function onOperationChange(){
			
			var self = this;
			var device = EThing.arbo.findOneById(deviceForm.value());
			var operation = operationForm.value();
			var deviceId = device instanceof EThing.Device ? device.id() : null;
			
			if(deviceId && operation && operationForm.assocDevice === deviceId && operationForm.assocOperation !== operation){
				
				operationForm.assocOperation = operation;
				
				self.removeItem('parameters');
				self.removeItem('jsonPath');
				self.removeItem('regexp');
				self.removeItem('xpath');
				
				var api = null,
					apis = cache[device.id()];
				
				for(var i in apis){
					if(apis[i].name === operation){
						api = apis[i];
						break;
					}
				}
				
				if(api && api.schema){
					
					var positionIndex = operationFormIndex + 1;
					
					if(!(api.schema.type=='object' && $.isEmptyObject(api.schema.properties) && !api.schema.additionalProperties)){
						var schemaForm = Form.fromJsonSchema(api.schema)
						if(schemaForm){
							var layoutitem = self.addItem({
								name: 'parameters',
								item: schemaForm,
								emptyMessage: 'no parameters'
							}, positionIndex++);
							
							var preset = self.parent()._preset;
							if(preset && preset.operation === operation){
								layoutitem.item.value(preset.parameters);
							}
						}
					}
					
					if(options.jsonPath && api.response && mimetypeMatch(api.response,'application/json')){
						var layoutitem = self.addItem({
							name: 'jsonPath',
							label: 'JSON path',
							description: 'Retrieve the value from a JSON payload by locating a JSON Element using a JSON path expression.',
							item: new $.Form.Text({
								validators:[function(v){
									if(v){
										JsonPath.parse(v);
									}
								}]
							})
						},positionIndex++);
						
						var preset = self.parent()._preset;
						if(preset && preset.jsonPath && preset.operation === operation){
							layoutitem.item.value(preset.jsonPath);
						}
					}
					
					if(options.regexp && api.response && mimetypeMatch(api.response,'text/*')){
						var layoutitem = self.addItem({
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
							})
						},positionIndex++);
						
						var preset = self.parent()._preset;
						if(preset && preset.regexp && preset.operation === operation){
							layoutitem.item.value(preset.regexp);
						}
					}
					
					if(options.xpath && api.response && mimetypeMatch(api.response,'application/xml') && DOMParser){
						var layoutitem = self.addItem({
							name: 'xpath',
							label: 'XPath Expression',
							description: 'Retrieve the value from a XML payload by locating an element using a XPath expression.',
							item: new $.Form.Text({})
						},positionIndex++);
						
						var preset = self.parent()._preset;
						if(preset && preset.xpath && preset.operation === operation){
							layoutitem.item.value(preset.xpath);
						}
					}
					
				}
				
				if(typeof options.onchange === 'function')
					options.onchange.call(self, device, operation);
				
			}
			
		}
		
		
		
		
		
		Form.Wrapper.call(this, {
			item : new Form.FormLayout({
				items: formItems,
				onattach: function(){
					
					if(!deviceForm && typeof options.deviceForm == 'string'){
						deviceForm = this.form().findItem(options.deviceForm);
					}
					
					if(!deviceForm) return;
					
					operationForm.change($.proxy(onOperationChange, this));
					deviceForm.change($.proxy(onDeviceChange, this)).change();
					
					if(typeof options.onload === 'function')
						options.onload.apply(this, arguments);
					
				}
			}),
			value: options.value
		});
		
	};
	DeviceRequest.prototype = Object.create(Form.Wrapper.prototype);
	
	DeviceRequest.prototype.createView = function(){
		return Form.Wrapper.prototype.createView.call(this).addClass('f-devicerequest');
	}
	DeviceRequest.prototype.setValue = function(value){
		
		var preset_save = this._preset;
		this._preset = value;
		if(!Form.Wrapper.prototype.setValue.call(this,value)){
			if(typeof preset_save != 'undefined') this._preset = preset_save;
			return false;
		}
		
		return true;
	}
	
	DeviceRequest.prototype.getErrors = function(){
		var errors = [];
		if(this.error)
			errors.push(this.error);
		return errors.concat(this.item.getErrors());
	}
	
	
	
	
	DeviceRequest.makeRequest = function(options){
		
		var resource = EThing.arbo.findOneById(options.resource || options.device);
		if(!resource){
			throw 'The resource does not exist';
		}
		
		var operation = options.operation;
		var parameters = options.parameters || null;
		var jsonPath = options.jsonPath || null;
		var regexp = options.regexp || null;
		var xpath = options.xpath || null;
		
		if(regexp){
			var sep = regexp[0];
			var match = regexp.match(new RegExp('^\\'+sep+'(.*?)\\'+sep+'([gimuy]*)$'));
			regexp = new RegExp(match[1], match[2]);
		}
		
		var dfr = $.Deferred();
		
		resource.execute(operation, parameters).done(function(data, xhr){
			
			if(xpath && typeof data === 'string' && xhr.getResponseHeader('content-type')==='application/xml' && DOMParser){
				var parser = new DOMParser();
				var xmlDoc = parser.parseFromString(data, "text/xml"); 
				var list = xmlDoc.evaluate(xpath,xmlDoc,null,XPathResult.NUMBER_TYPE,null);
				data = isNaN(list.numberValue) ? null : list.numberValue;
			}
			
			if(jsonPath && $.isPlainObject(data)){
				require(['jsonpath'], function(JsonPath){
					var r = JsonPath.query(data, jsonPath, 1);
					data = r.length ? r[0] : null;
					dfr.resolve(data);
				});
				return;
			}
			
			if(regexp && typeof data === 'string'){
				var lines = data.split('\n'), matches;
				data = null;
				for(var i = 0;i < lines.length;i++){
					if(matches = lines[i].match(regexp)){
						data = matches.length === 1 ? matches[0] : matches[1];
						break;
					}
				}
			}
			
			dfr.resolve(data);
			return;
		}).fail(function(err){
			dfr.reject(err);
		});
		
		return dfr;
	}
	
	
	/* register as a Form plugin */
	
	Form.DeviceRequest = DeviceRequest;
	
	
	
	
}));
