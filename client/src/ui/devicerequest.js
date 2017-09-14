(function (root, factory) {
    if (typeof define === 'function' && define.amd) {
        // AMD. Register as an anonymous module.
        define(['jquery','form','ething','./resourceselect'], factory);
    } else {
        // Browser globals
        factory(root.jQuery,root.Form,root.EThing);
    }
}(this, function ($, Form, EThing) {
	
	
	/*
	
	options:
		
		filter : function(resource) -> boolean 
		
		onApiCall: function(device, operation, api) executed once the api is loaded.
		onchange: function(device, operation) executed once the tupple [device,operation] changed. The API may not be loaded !
		onload: function() is executed once the form is loaded.
		
		value: { device: <deviceId>, operation: <operationId> [, parameters: <parameters>]} the initial value
		
		acceptedMimeType: <mime> or [<mime>] , only the following mime types for the returned data will be allowed.
	
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
		
		Form.Wrapper.call(this, {
			item : new Form.FormLayout({
				items: [{ // device selection
					name: 'device',
					item: new Form.ResourceSelect({
						filter: function(r){
							return r instanceof EThing.Device && (typeof options.filter != 'function' || options.filter.call(self, r));
						},
						validators: [Form.validator.NotEmpty]
					})
				},{
					name: 'operation',
					item: new Form.Select({
						items: [],
						validators: [function(v){
							if(this.rejected !== false && this.rejectedValue===v)
								throw new Error('operation not accepted'+(typeof this.rejected === 'string' ? (': '+this.rejected) : ''));
						}],
						onload: function(){
							this.rejected = false;
						}
					}),
					dependencies: {
						'device': function(layoutItem){
							var r = EThing.arbo.findOneById(this.getLayoutItemByName('device').item.value());
							layoutItem.item.setOptions( r instanceof EThing.Device ? r.operations() : []);
							return r instanceof EThing.Device;
						}
					}
				}],
				onload: function(){
					
					var self = this;
					var deviceForm = this.getLayoutItemByName('device').item;
					var operationForm = this.getLayoutItemByName('operation').item;
					var id = 0;
					
					var cache = {};
					
					function update(){
						
						var device = EThing.arbo.findOneById(deviceForm.value());
						var operation = operationForm.value();
						var id_ = ++id;
						
						self.removeItem('parameters');
						
						if(device instanceof EThing.Device && operation){
							
							operationForm.rejected = false;
							operationForm.rejectedValue = null;
							
							var cacheKey = device.id()+"."+operation;
							
							if(cache[cacheKey]){
								loadApi(cache[cacheKey]);
							} else {
								device.getApi(operation).done(function(api){
									cache[cacheKey] = api;
									loadApi(api);
								});
							}
							
							// get the json schema specification for this operation
							function loadApi(api){
								
								if(api.schema && id_ === id){
									
									var rejected = false;
									
									if(options.acceptedMimeType){
										var allowedMimeTypes = options.acceptedMimeType || [];
										if(!Array.isArray(allowedMimeTypes)) allowedMimeTypes = [allowedMimeTypes];
										
										var mimeType = api.response;
										
										if(allowedMimeTypes.length && mimeType!=='*/*' && mimeType!=='*'){
										
											rejected = 'wrong mime type';
											
											if(typeof mimeType === 'string' && mimeType.length){
												for(var i in allowedMimeTypes){
													var allowedMimeType = allowedMimeTypes[i];
													
													if(allowedMimeType instanceof RegExp){
														if(allowedMimeType.test(mimeType)){
															rejected = false;
															break;
														}
													}
													else if(mimeType === allowedMimeType){
														rejected = false;
														break;
													}
													else if(mimeType.indexOf('*')!==-1) {
														var re = new RegExp('^'+mimeType.replace('*','[^/]*')+'$','i');
														if(re.test(allowedMimeType)){
															rejected = false;
															break;
														}
													}
													else if(allowedMimeType.indexOf('*')!==-1) {
														var re = new RegExp('^'+allowedMimeType.replace('*','[^/]*')+'$','i');
														if(re.test(mimeType)){
															rejected = false;
															break;
														}
													}
													
												}
											}
											
										}
									}
									
									if(typeof options.onApiCall === 'function')
										if(options.onApiCall.call(self, device, operation, api)===false)
											rejected = true;
									
									if(rejected === false){
										if(!(api.schema.type=='object' && $.isEmptyObject(api.schema.properties) && !api.schema.additionalProperties)){
											var schemaForm = Form.fromJsonSchema(api.schema)
											if(schemaForm){
												var layoutitem = self.addItem({
													name: 'parameters',
													item: schemaForm,
													emptyMessage: 'no parameters'
												});
												
												var preset = self.parent()._preset;
												if(preset && preset.operation === operation){
													layoutitem.item.value(preset.parameters);
												}
											}
										}
									} else {
										operationForm.rejectedValue = operation;
										operationForm.setError(new Error('operation not accepted'+(typeof rejected === 'string' ? (': '+rejected) : '')));
									}
									
									operationForm.rejected = rejected;
									
								}
								
							};
							
						}
						
						if(typeof options.onchange === 'function')
							options.onchange.call(self, device, operation);
						
					}
					
					operationForm.change(update);
					deviceForm.change(update).change();
					
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
	
	
	
	/* register as a Form plugin */
	
	Form.DeviceRequest = DeviceRequest;
	
	
	
	
}));
