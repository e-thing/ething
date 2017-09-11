(function (root, factory) {
    if (typeof define === 'function' && define.amd) {
        // AMD. Register as an anonymous module.
        define(['jquery','form','ething','./resourceselect','bootstrap-select'], factory);
    } else {
        // Browser globals
        root.DeviceOperationSelect = factory(root.jQuery,root.Form,root.EThing);
    }
}(this, function ($, Form, EThing) {
	
	
	/*
	
	example :
	
	$('#mydiv').deviceOperationSelect({
	  value: {
		device: "NbsS7uz",
		operation: "post_/echo/data2"
	  }
	}, function(){
		// is executed when this widget is fully loaded. 
	});
	
	*/
	
	var DeviceOperationSelect = function(element,opt){
		var self = this;
		
		this.$element = $(element);
		this.options = $.extend(true,{
			filter: null, // filter function(resource) -> true|false|"disabled"
			operationFilter: null, // function(operationId) -> boolean
			value: null,
			customOperation: false // enable 
		}, opt);
		
		this.$element.addClass('device-operation-select');
		
		this.$deviceSelect = $('<div>');
		
		this.$selectOp = $('<select disabled>');
		
		this.$element.html( $('<div class="form-inline">').append(this.$deviceSelect, ' ', this.$selectOp) );
		
		this.$deviceSelect.resourceSelect({
			filter: function(r){
				var m;
				if(r instanceof EThing.Device){
					if(typeof self.options.filter != "function" || (m = self.options.filter(r))){
						return (r.url() || self.options.customOperation) && m!='disabled' ? true : 'disabled';
					}
				}
			},
			multiple: false,
			allowCreation: false,
			title: 'Select a device'
		});
		
		this.$deviceSelect.resourceSelect('change', function(){
			self.update();
			self.change();
		});
		
		this.$selectOp.selectpicker({
			title: 'Select an operation',
			showTick: true,
			header: 'Select an operation'
		});
		
		this.$selectOp.on('changed.bs.select', function(e,clickedIndex, select){
			self.change();
		});
		
		if(this.options.value) this.value(this.options.value);
		
		
	}
	
	DeviceOperationSelect.prototype.change = function(handler){
		if(typeof handler == 'function'){
			var self = this;
			this.$element.on('changed.dos', function(){
				handler.call(self);
			});
		} else {
			var e = $.Event( 'changed.dos', { instance: this, data: handler } );
			this.$element.trigger(e);
		}
		return this;
	}
	
	DeviceOperationSelect.prototype.update = function(){
		var device = this.$deviceSelect.resourceSelect('value');
		
		// update the operation list
		var currentDevice = this.$selectOp.data('device');
		if(currentDevice === device) return;
		
		this.$selectOp.data('device', device);
		
		
		// update the field list
		this.$selectOp.empty();
		if(device instanceof EThing.Resource){
			
			if(this.options.customOperation){
				this.$selectOp.append('<option value="__custom__">custom</option>');
			}
			
			device.operations().forEach(function(operationId){
				if(!this.options.operationFilter || this.options.operationFilter.call(this, operationId))
					this.$selectOp.append('<option>'+operationId+'</option>');
			},this);
			
			// select the first item
			this.$selectOp.find('option').first().attr('selected','selected');
			
			this.$selectOp.removeAttr('disabled');
		}
		else
			this.$selectOp.attr('disabled', 'disabled');
		
		this.$selectOp.selectpicker('refresh');
		
	}
	
	/*
	 value = {
		device: ID{string} | EThing.Device ,
		operation: {string} // not available when custom selected
	 }
	*/
	DeviceOperationSelect.prototype.value = function(value){
		if(typeof value == 'undefined'){
			var device = this.$deviceSelect.resourceSelect('value'),
				operation = this.$selectOp.val();
			
			if(device && operation){
				if(operation == '__custom__')
					return {
						device: device
					};
				else
					return {
						device: device,
						operation: operation
					};
			}
			else
				return null;
		}
		else {
			if($.isPlainObject(value) && value.device){
				
				var operation = value.operation;
				if(!operation && this.options.customOperation){
					operation = '__custom__';
				}
				if(operation){
					this.$deviceSelect.resourceSelect('value',value.device);
					this.update();
					this.$selectOp.selectpicker('val', typeof operation == 'string' ? operation : operation.operation.operationId);
				}
			}
		}
	}
	
	
	
	function serialize(value){
		if($.isPlainObject(value) && value.hasOwnProperty('device')){
			var out = {
				device: value.device instanceof EThing.Resource ? value.device.id() : value.device
			};
			if(value.hasOwnProperty('operation')){
				out.operation = typeof value.operation == 'string' ? value.operation : value.operation.operation.operationId;
			}
			return out;
		}
		else if(value===null) return null;
		throw 'invalid data';
	}
	
	
	/* register as a Form plugin */
	
	Form.DeviceOperationSelect = function(options){
		
		Form.CustomInput.call(this,$.extend({
			input: function(){
				var $input = $('<div class="f-deviceoperationselect">').deviceOperationSelect(options), self = this;
				
				$input.deviceOperationSelect('change', function(){
					self.update();
				});
				
				return $input;
			},
			get: function($input){
				return serialize($input.deviceOperationSelect('value'));
			},
			set: function($input,v){
				$input.deviceOperationSelect('value', v);
			},
			value: null
		}, options));
		
	}
	Form.DeviceOperationSelect.prototype = Object.create(Form.CustomInput.prototype);
	
	Form.DeviceOperationSelect.prototype.setValue = function(value){
		try {
			value = serialize(value);
		} catch(e){ return false; }
		return Form.CustomInput.prototype.setValue.call(this,value);
	}
	
	Form.DeviceOperationSelect.prototype.getDevice = function(){
		var v = this.$input.deviceOperationSelect('value');
		return v ? v.device : null;
	}
	Form.DeviceOperationSelect.prototype.getOperation = function(){
		var v = this.$input.deviceOperationSelect('value');
		return v ? v.operation : null;
	}
	
	
	
	
	
	/* register as a plugin in jQuery */
	$.DeviceOperationSelect = DeviceOperationSelect;
	
	$.fn.deviceOperationSelect = function(){
		var args = [].slice.call(arguments);
		
		if (this[0]) { // this[0] is the renderTo div
			
			var instance = $(this[0]).data('deviceOperationSelect');
			
			if(instance){
				if(args.length){
					if(typeof args[0] == 'string'){
						// access the attribute or method
						var prop = instance[args.shift()];
						if(typeof prop == 'function'){
							var r = prop.apply(instance,args);
							return (r === instance) ? this : r; // make it chainable
						}
						else {
							if(args.length==0){
								// getter
								return prop;
							}
							else if(args.length==1){
								// setter
								prop = args[0];
								return this;
							}
						}
					}
				}
				else
					return instance;// When called without parameters return the instance
			}
			
			// if we are are, it means that there is no instance or that the user wants to create a new one !
			// /!\ NOTE : be sure to not emit any event in the constructor, or delay them using the setTimeout function !
			instance = new DeviceOperationSelect(this[0],args[0],args[1],args[2],args[3],args[4],args[5],args[6]);
			$(this[0]).data('deviceOperationSelect',instance);
			
			return this;
		}
	};
	
	
	return DeviceOperationSelect;
	
}));
