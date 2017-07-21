(function (root, factory) {
    if (typeof define === 'function' && define.amd) {
        // AMD. Register as an anonymous module.
        define(['js/ui', 'text!./resource.html', 'jquery', 'ething', 'form', 'css!./resource'], factory);
    }
}(this, function (UI, template, $, EThing) {
	
	
	return function(data){
		
		// get the appId from the query string
		var resource = EThing.arbo.findOneById(data.rid);
		
		if(!resource){
			UI.show404();
			return;
		}
		
		var $template = UI.Container.set(template);
		
		$template.find('.resource-title').text(resource.basename());
		
		
		var form, categories = {};
		
		
		// tidy up by categories
		UI.getResourceProperties(resource).forEach(function(property){
			var category = property.category || 'General';
			if(!categories.hasOwnProperty(category))
				categories[category] = [];
			categories[category].push(property.name);
		});
		
		if(Object.keys(categories).length > 1){
			// multiple tabs
			var catForms = [];
			
			Object.keys(categories).forEach(function(cat){
					
				catForms.push(UI.getResourceForm(resource, null, categories[cat]).then(function(formItems){
					
					var item;
					
					// special case
					if( (resource instanceof EThing.Device) && /server/i.test(cat) ){
						item = new $.Form.FieldsEnabler({
							label: 'Enable',
							item: new $.Form.FormLayout({items: formItems}),
							state: !!resource.url(),
							disabledValue: {
								url: null
							}
						});
					}
					else
						item = new $.Form.FormLayout({items: formItems});
					
					return {
						name: cat,
						fields: categories[cat],
						item: item
					};
				}));
				
			});
			
			form= $.when.apply($, catForms).then(function(){
				var catItems = catForms.length==1 ? arguments[0] : Array.prototype.slice.call(arguments);
				
				return new $.Form.TabsLayout({
					format: $.Form.TabsLayout.Format.Merge,
					items: catItems
				});
			});
			
		}
		else {
			form = UI.getResourceForm(resource).then(function(formItems){
				return new $.Form.FormLayout({items: formItems});
			});
		}
		
		var $form = $template.find('#resource-form').form(form);
		var $error = $template.find('#resource-error');
		
		var $validBtn = $template.find('#resource-valid').click(function(){
			
			$form.form('submit', function(props){
				
				resource
					.set(props)
					.done(function(){
						UI.goBack();
					})
					.fail(function(e){
						$error.text(typeof e.message == 'string' ? e.message : e).show();
						$form.one('changed.form', function(){
							$error.hide();
						});
					});
				
			});
			
		});
		
		$form.on('changed.form', function(){
			$validBtn.prop('disabled', $form.form('hasError'));
		});
		
		$template.find('#resource-cancel').click(function(){
			UI.goBack();
		});
		
		
	};
}));