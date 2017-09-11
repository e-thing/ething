(function (factory) {
	// AMD.
	define(['jquery','ething','form'], factory);
}(function ($, EThing, Form) {
	
	
	var defaultOptions = {
		title: 'Execute'
	};
	
	
	return {
		description: "Execute a request by clicking a button.",
		
		// must return a function which returns an options object
		factory: function(container, preset){
			
			var form = null;
			
			require([
				"codemirror",
				"css!codemirror",
				"codemirror/mode/javascript/javascript",
				"codemirror/addon/edit/matchbrackets",
				"codemirror/addon/edit/closebrackets",
				"codemirror/addon/fold/foldcode",
				"codemirror/addon/fold/foldgutter",
				"css!codemirror/addon/fold/foldgutter",
				"codemirror/addon/fold/brace-fold",
				"codemirror/addon/scroll/simplescrollbars",
				"css!codemirror/addon/scroll/simplescrollbars",
				"codemirror/addon/display/autorefresh",
				"ui/resourceselect"
			], function(CodeMirror){
				
				form = new $.Form(container,
					new $.Form.FormLayout({
						merge: true,
						items:[{
							name: 'title',
							item: new $.Form.Text({
								validators: [$.Form.validator.NotEmpty]
							})
						},{
							name: 'color',
							item: new $.Form.Color({
								value: '#307bbb'
							})
						},{
							name: 'mode',
							item: new $.Form.Select({
								items: {
									'execute a device\'s request': 'device',
									'execute a script': 'script',
									'emit a event': 'event'
								}
							})
						},{
							name: 'resource',
							label: 'source',
							item: new $.Form.ResourceSelect({
								filter: function(r){
									return r instanceof EThing.Device;
								},
								validators: [$.Form.validator.NotEmpty]
							}),
							dependencies: {
								'mode': function(layoutItem, dependentLayoutItem){
									return dependentLayoutItem.item.value() === 'device';
								}
							}
						},{
							name: 'operation',
							item: new $.Form.Select(),
							dependencies: {
								'resource': function(layoutItem){
									var r = EThing.arbo.findOneById(this.getLayoutItemByName('resource').item.value());
									layoutItem.item.setOptions( r instanceof EThing.Device ? r.operations() : []);
									return (r instanceof EThing.Device) && this.getLayoutItemByName('mode').item.value() === 'device';
								},
								'mode': function(layoutItem){
									var r = EThing.arbo.findOneById(this.getLayoutItemByName('resource').item.value());
									return (r instanceof EThing.Device) && this.getLayoutItemByName('mode').item.value() === 'device';
								}
							}
						},{
							name: 'script',
							item: new $.Form.CustomInput({
								input: function(){
									var $input = $('<div>'), self = this;
									
									this.editor = CodeMirror($input[0], {
										lineNumbers: true,
										tabSize: 2,
										mode: 'application/javascript',
										gutters: ["CodeMirror-linenumbers", "CodeMirror-foldgutter"],
										matchBrackets: true,
										autoCloseBrackets: true,
										foldGutter: true,
										extraKeys: {
											"Ctrl-Q": function(cm){
												cm.foldCode(cm.getCursor());
											}
										},
										scrollbarStyle: 'simple',
										autoRefresh: true
									});
									
									this.editor.setSize(null,'400px');
									
									this.editor.on('blur', function(){
										self.update();
									});
									
									return $input;
								},
								set: function($e,v){
									// content is set on input function
									this.editor.setValue(v);
								},
								get: function($e){
									return this.editor.getValue();
								},
								validators: [function(value){
									// valid javascript ?
									// todo
								}],
								value: "// javascript\n\n"
							}),
							dependencies: {
								'mode': function(layoutItem, dependentLayoutItem){
									return dependentLayoutItem.item.value() === 'script';
								}
							}
						},{
							name: 'event',
							label: 'event name',
							item: new $.Form.Text({
								validators: [$.Form.validator.NotEmpty]
							}),
							dependencies: {
								'mode': function(layoutItem, dependentLayoutItem){
									return dependentLayoutItem.item.value() === 'event';
								}
							}
						}],
						onload: function(){
							
							var self = this;
							var resourceForm = this.getLayoutItemByName('resource').item;
							var operationForm = this.getLayoutItemByName('operation').item;
							var id = 0;
							
							function update(){
								
								var resource = EThing.arbo.findOneById(resourceForm.value());
								var operation = operationForm.value();
								var id_ = ++id;
								
								self.removeItem('parameters');
								
								if(resource instanceof EThing.Device && operation){
									
									// get the json schema specification for this operation
									resource.getApi(operation).done(function(api){
										
										if(api.schema && id_ === id){
											
											var layoutitem = self.addItem({
												name: 'parameters',
												item: Form.fromJsonSchema(api.schema),
												dependencies: {
													'mode': function(layoutItem){
														return this.getLayoutItemByName('mode').item.value() === 'device';
													}
												}
											});
											
											if(preset && preset.operation === operation){
												layoutitem.item.value(preset.parameters);
											}
										}
										
									});
									
								}
								
							}
							
							operationForm.change(update);
							resourceForm.change(update).change();
							
						}
					}),
					$.extend(true,{}, defaultOptions, preset)
				);
				
				
			});
			
			
			
			
			return function(){
				return form.submit();
			}
		},
		
		require: ['widget/Buttons'],
		
		instanciate: function(options, Buttons){
			
			options = $.extend(true,{
				mode: 'device', // device, script or event
				color: '#307bbb',
				// device
				resource: null, // either a device or a file
				operation: null, // operation id if the resource is a Device
				parameters: null, // optional parameters if the resource is a Device
				// script
				script: '',
				// event,
				event: null
			}, defaultOptions, options);
			
			var mode = options.mode;
			var fn = null;
			var title = null;
			
			if(mode === 'device'){
				
				var resource = EThing.arbo.findOneById(options.resource);
				if(!resource)
					throw new Error('The resource does not exist anymore');
				if(!(resource instanceof EThing.Device))
					throw new Error('The resource is not a device');
				
				title = resource.basename();
				fn = function(){
					return resource.execute(options.operation, options.parameters);
				};
				
			} else if(mode === 'script'){
				
				var script = options.script;
				if(!(typeof script === 'string' && script.trim().length))
					throw new Error('Invalid script value');
				
				fn = function(){
					eval(script);
				};
				
			} else if(mode === 'event'){
				
				var event = options.event;
				if(!(typeof event === 'string' && event.trim().length))
					throw new Error('Invalid event value');
				
				fn = function(){
					return EThing.Rule.trigger(event);
				};
				
			} else {
				throw new Error('Invalid mode !');
			}
			
			var button = Buttons({
				buttons : [{
					label: options.title,
					onClick: fn,
					bgColor: options.color
				}],
				title: title
			});
			
			return button;
		}
	};
	
}));