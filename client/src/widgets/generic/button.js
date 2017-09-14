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
				"ui/resourceselect",
				"ui/devicerequest"
			], function(CodeMirror){
				
				form = new $.Form(container,
					new $.Form.FormLayout({
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
							item: new $.Form.SelectPanels({
								items: [{
									name: 'device',
									label: 'execute a device\'s request',
									item: new $.Form.DeviceRequest()
								},{
									name: 'script',
									label: 'execute a script',
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
									})
								},{
									name: 'event',
									label: 'emit an event',
									item: new $.Form.FormLayout({
										items: [{
											name: 'event',
											label: 'event name',
											item: new $.Form.Text({
												validators: [$.Form.validator.NotEmpty]
											})
										}]
									})
								}]
							})
						}]
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
				color: '#307bbb',
				mode: {
					type: 'device', // device, script or event
					value: {
						// device
						device: null, // either a device or a file
						operation: null, // operation id if the resource is a Device
						parameters: null, // optional parameters if the resource is a Device
						// event,
						event: null
					}
				}
			}, defaultOptions, options);
			
			var mode = options.mode.type;
			var fn = null;
			var title = null;
			
			if(mode === 'device'){
				
				var resource = EThing.arbo.findOneById(options.mode.value.device);
				if(!resource)
					throw new Error('The resource does not exist anymore');
				if(!(resource instanceof EThing.Device))
					throw new Error('The resource is not a device');
				
				title = resource.basename();
				fn = function(){
					return resource.execute(options.mode.value.operation, options.mode.value.parameters);
				};
				
			} else if(mode === 'script'){
				
				var script = options.mode.value;
				if(!(typeof script === 'string' && script.trim().length))
					throw new Error('Invalid script value');
				
				fn = function(){
					eval(script);
				};
				
			} else if(mode === 'event'){
				
				var event = options.mode.value.event;
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