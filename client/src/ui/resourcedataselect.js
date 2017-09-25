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
		or
		resourceForm : an external ressourceSelect instance.
		
		onload: function() is executed once the form is loaded.
		
	*/
	
	
	var ResourceDataSelect = function(options){
		
		options = options || {};
		
		var self = this;
		var resourceForm = null;
		var formItems = [];
		
		
		if(options.resourceForm) {
			if(typeof options.resourceForm != 'string') resourceForm = options.resourceForm;
		} else {
			resourceForm = new Form.ResourceSelect({
				filter: function(r){
					return r instanceof EThing.Resource && !(r instanceof EThing.Folder) && (typeof options.filter != 'function' || options.filter.call(self, r));
				},
				validators: [Form.validator.NotEmpty]
			});
			
			formItems.push({
				name: 'resource',
				item: resourceForm
			});
		}
		
		var dataForm = new Form.Select({
			items: [],
			editable: true,
			validators: [$.Form.validator.NotEmpty],
		});
		
		formItems.push({
			name: 'data',
			item: dataForm
		});
		
		
		function update(){
			
			var self = this;
			var resource = EThing.arbo.findOneById(resourceForm.value());
			var resourceId = resource instanceof EThing.Resource ? resource.id() : null;
			
			// update the operation list ! (only if necessary !)
			if(resourceId !== dataForm.assocResource){
				dataForm.clear();
				if(resource instanceof EThing.Resource){
					var data = resource.data(), options = {};
					for(var k in data){
						options[k+' <span class="small ellipsis" style="color: #b5b4b4;max-width: 100px;display: inline-block;vertical-align: middle;">'+data[k]+'</span>'] = k;
					}
					dataForm.setOptions(options);
				}
			}
			
		}
		
		Form.Wrapper.call(this, {
			item : new Form.FormLayout({
				items: formItems,
				onattach: function(){
					
					if(!resourceForm && typeof options.resourceForm == 'string'){
						resourceForm = this.form().findItem(options.resourceForm);
					}
					
					if(!resourceForm) return;
					
					resourceForm.change($.proxy(update, this)).change();
					
					if(typeof options.onload === 'function')
						options.onload.apply(this, arguments);
					
				}
			}),
			value: options.value
		});
		
	};
	ResourceDataSelect.prototype = Object.create(Form.Wrapper.prototype);
	
	ResourceDataSelect.prototype.createView = function(){
		return Form.Wrapper.prototype.createView.call(this).addClass('f-resourcedataselect');
	}
	
	
	/* register as a Form plugin */
	
	Form.ResourceDataSelect = ResourceDataSelect;
	
	
	
	
}));
