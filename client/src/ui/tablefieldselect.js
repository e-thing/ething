(function (root, factory) {
    if (typeof define === 'function' && define.amd) {
        // AMD. Register as an anonymous module.
        define(['jquery','form','ething','./resourceselect','bootstrap-select','bootstrap-typeahead'], factory);
    } else {
        // Browser globals
        root.TableFieldSelect = factory(root.jQuery,root.Form,root.EThing);
    }
}(this, function ($, Form, EThing) {
	
	
	
	
	var TableFieldSelect = function(element,opt){
		var self = this;
		
		this.$element = $(element);
		this.options = $.extend(true,{
			filter: null, // filter function(resource) -> true|false|"disabled"
			value: null,
			allowCustom: false // allow the user to set a custom field
		}, opt);
		
		
		this.$element.addClass('table-field-select');
		
		
		this.$tableSelect = $('<div>');
		
		this.$selectField = $('<select disabled>');
		
		this.$element.html( $('<div class="form-inline">').append(this.$tableSelect, ' ', this.$selectField) );
		
		
		this.$tableSelect.resourceSelect({
			filter: function(r){
				return (r instanceof EThing.Table) ? (r.keys().length ? true : 'disabled') : false;
			},
			multiple: false,
			allowCreation: false,
			title: 'Select a table'
		});
		
		this.$tableSelect.resourceSelect('change', function(){
			self.update();
			self.change();
		});
		
		if(this.options.allowCustom){
			
			var $input = $('<input type="text" class="form-control" placeholder="field">');
			this.$selectField.replaceWith($input);
			this.$selectField = $input;
			
			this.$selectField.change(function(){
				self.change();
			});
			
			this.update();
			
			
		} else {
		
			this.$selectField.selectpicker({
				title: 'Select a field',
				showTick: true,
				header: 'Select a field'
			});
			
			this.$selectField.on('changed.bs.select', function(e,clickedIndex, select){
				self.change();
			});
			
		}
		
		if(this.options.value) this.value(this.options.value);
		
		
	}
	
	TableFieldSelect.prototype.change = function(handler){
		if(typeof handler == 'function'){
			var self = this;
			this.$element.on('changed.tfs', function(){
				handler.call(self);
			});
		} else {
			var e = $.Event( 'changed.tfs', { instance: this, data: handler } );
			this.$element.trigger(e);
		}
		return this;
	}
	
	TableFieldSelect.prototype.update = function(){
		
		var table = this.$tableSelect.resourceSelect('value');
		
		// update the operation list
		var currentTable = this.$selectField.data('table');
		if(currentTable === table) return;
		
		this.$selectField.data('table', table);
		
		if(this.options.allowCustom){
			this.$selectField.typeahead('destroy');
			if(table instanceof EThing.Resource){
				this.$selectField.removeAttr('disabled');
				this.$selectField.typeahead({
					source: table.keys(),
					showHintOnFocus: "all",
					items: 'all'
				});
			}
			else this.$selectField.attr('disabled', 'disabled')
		} else {
		
			// update the field list
			this.$selectField.empty();
			if(table instanceof EThing.Resource){
				table.keys().forEach(function(key){
					this.$selectField.append('<option>'+key+'</option>');
				},this);
				
				// select the first item
				this.$selectField.find('option').first().attr('selected','selected');
				
				this.$selectField.removeAttr('disabled');
			}
			else
				this.$selectField.attr('disabled', 'disabled');
			
			this.$selectField.selectpicker('refresh');
			
		}
		
	}
	
	/*
	 value = {
		table: ID{string} | EThing.Table ,
		field: {string}
	 }
	*/
	TableFieldSelect.prototype.value = function(value){
		if(typeof value == 'undefined'){
			var table = this.$tableSelect.resourceSelect('value'),
				field = this.$selectField.val();
				
			return (table && field) ? {
				table: table,
				field: field
			} : null;
		}
		else {
			if($.isPlainObject(value) && value.table && value.field){
				this.$tableSelect.resourceSelect('value',value.table);
				this.update();
				this.$selectField.selectpicker('val', value.field);
			}
		}
	}
	
	
	function serialize(value){
		if($.isPlainObject(value) && typeof value.field == 'string'){
			if(typeof value.table == 'string') return value;
			else if(value.table instanceof EThing.Table) return {
				table: value.table.id(),
				field: value.field
			};
		}
		else if(value===null) return null;
		throw 'invalid data';
	}
	
	
	/* register as a Form plugin */
	
	
	$.Form.TableFieldSelect = function(options){
		
		$.Form.CustomInput.call(this,$.extend({
			input: function(){
				var $input = $('<div class="f-tablefieldselect">').tableFieldSelect(options), self = this;
				
				$input.tableFieldSelect('change', function(){
					self.update();
				});
				
				return $input;
			},
			get: function($input){
				return serialize($input.tableFieldSelect('value'));
			},
			set: function($input,v){
				$input.tableFieldSelect('value', v);
			},
			value: null,
		}, options));
		
	}
	$.Form.TableFieldSelect.prototype = Object.create($.Form.CustomInput.prototype);
	
	$.Form.TableFieldSelect.prototype.setValue = function(value){
		try {
			value = serialize(value);
		} catch(e){ return false; }
		return $.Form.CustomInput.prototype.setValue.call(this,value);
	}
	
	$.Form.TableFieldSelect.prototype.getTable = function(){
		var v = this.$input.tableFieldSelect('value');
		return v ? v.table : null;
	}
	$.Form.TableFieldSelect.prototype.getField = function(){
		var v = this.$input.tableFieldSelect('value');
		return v ? v.field : null;
	}
	
	
	
	
	/* register as a plugin in jQuery */
	$.TableFieldSelect = TableFieldSelect;
	
	$.fn.tableFieldSelect = function(){
		var args = [].slice.call(arguments);
		
		if (this[0]) { // this[0] is the renderTo div
			
			var instance = $(this[0]).data('tableFieldSelect');
			
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
			instance = new TableFieldSelect(this[0],args[0],args[1],args[2],args[3],args[4],args[5],args[6]);
			$(this[0]).data('tableFieldSelect',instance);
			
			return this;
		}
	};
	
	
	return TableFieldSelect;

	
	
}));
