(function (root, factory) {
    if (typeof define === 'function' && define.amd) {
        // AMD. Register as an anonymous module.
        define(['jquery','form','ething','./resourceselect','./devicerequest'], factory);
    } else {
        // Browser globals
        factory(root.jQuery,root.Form,root.EThing);
    }
}(this, function ($, Form, EThing) {
	
	/*
	
	options:
		
		filter : function(resource) -> boolean 
		
		
	
	*/
	
	
	var DataSource = function(options){
		
		options = options || {};
		
		var self = this;
		
		var items = [];
		
		if(options.tableColumn){
			var item = {
				name: 'table.column',
				label: 'get data from a table',
				item: new Form.FormLayout({
					items: [{
						name: 'resource',
						label: 'table',
						item: new Form.ResourceSelect({
							filter: function(r){
								return r instanceof EThing.Table && (typeof options.tableColumn.filter != 'function' || options.tableColumn.filter.call(self, r));
							},
							validators: [Form.validator.NotEmpty]
						})
					},{
						name: 'column',
						item: new Form.Select({
							validators: [$.Form.validator.NotEmpty],
						}),
						dependencies: {
							'resource': function(layoutItem){
								var r = EThing.arbo.findOneById(this.getLayoutItemByName('resource').item.value());
								layoutItem.item.setOptions(r instanceof EThing.Table ? r.keys() : []);
								return r instanceof EThing.Table;
							}
						}
					}]
				})
			};
			
			items.push(item);
		}
		
		if(options.deviceRequest){
			var item = {
				name: 'device.request',
				label: 'get data returned by a device',
				item: new Form.DeviceRequest($.isPlainObject(options.deviceRequest) ? options.deviceRequest : {})
			};
			
			items.push(item);
		}
		
		if(options.resourceData){
			var item = {
				name: 'resource.data',
				label: 'get internal data from a resource',
				item: new Form.FormLayout({
					items: [{
						name: 'resource',
						item: new Form.ResourceSelect({
							filter: function(r){
								return !(r instanceof EThing.Folder) && !$.isEmptyObject(r.data()) && (typeof options.resourceData.filter != 'function' || options.resourceData.filter.call(self, r));
							},
							validators: [Form.validator.NotEmpty]
						})
					},{
						name: 'data',
						item: new Form.Select({
							validators: [$.Form.validator.NotEmpty],
						}),
						dependencies: {
							'resource': function(layoutItem){
								var r = EThing.arbo.findOneById(this.getLayoutItemByName('resource').item.value());
								var options = {};
								if(r instanceof EThing.Resource){
									var data = r.data();
									for(var k in data){
										options[k+' <span class="small ellipsis" style="color: #b5b4b4;max-width: 100px;display: inline-block;vertical-align: middle;">'+data[k]+'</span>'] = k;
									}
								}
								layoutItem.item.setOptions(options);
							}
						}
					}]
				})
			};
			
			items.push(item);
		}
		
		if(options.fileContent){
			var item = {
				name: 'file.content',
				label: 'get content from a file',
				item: new Form.FormLayout({
					items: [{
						name: 'resource',
						item: new Form.ResourceSelect({
							filter: function(r){
								return r instanceof EThing.File && (typeof options.fileContent.filter != 'function' || options.fileContent.filter.call(self, r));
							},
							validators: [Form.validator.NotEmpty]
						})
					}]
				})
			};
			
			items.push(item);
		}
		
		
		Form.Wrapper.call(this, {
			item : new Form.SelectPanels({
				items: items,
				format: Form.SelectPanels.format.Merge
			}),
			value: options.value
		});
		
	};
	DataSource.prototype = Object.create(Form.Wrapper.prototype);
	
	DataSource.prototype.createView = function(){
		return Form.Wrapper.prototype.createView.call(this).addClass('f-datasource');
	}
	
	
	/* register as a Form plugin */
	
	Form.DataSource = DataSource;
	
	
	
	
}));
