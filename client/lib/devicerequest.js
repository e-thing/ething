(function (root, factory) {
    if (typeof define === 'function' && define.amd) {
        // AMD. Register as an anonymous module.
        define(['jquery','form','ething','resourceselect'], factory);
    } else {
        // Browser globals
        factory(root.jQuery,root.Form,root.EThing);
    }
}(this, function ($, Form, EThing) {
	
	
	
	
	/*
	*
	{
		device: #deviceId,
		mode: "http" | "swagger"
		
		// extended with the mode properties
	}
	*
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
						name: 'device',
						validators: [Form.validator.NotEmpty]
					})
				},{
					name: 'operation',
					item: new Form.Select({
						name: 'operation',
						items: []
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
					var deviceForm = this.findItem('device');
					var operationForm = this.findItem('operation');
					var id = 0;
					
					function update(){
						
						var device = EThing.arbo.findOneById(deviceForm.value());
						var operation = operationForm.value();
						var id_ = ++id;
						
						self.removeItem(2);
						
						if(device && operation){
							
							// get the json schema specification for this operation
							device.getApi(operation).done(function(api){
								
								if(api.schema && id_ === id){
									
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
									
									if(typeof options.onApiCall === 'function')
										options.onApiCall.call(self, device, operation, api);
								}
								
							});
							
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
		return Form.Wrapper.prototype.createView.call(this).addClass('f-deviceoperationrequest');
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
	
	
	/* register as a Form plugin */
	
	Form.DeviceRequest = DeviceRequest;
	
	
	
	
}));
