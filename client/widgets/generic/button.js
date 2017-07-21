(function (factory) {
	// AMD.
	define(['jquery','ething','form'], factory);
}(function ($, EThing, Form) {
	
	
	var defaultOptions = {
		title: 'Execute'
	};
	
	
	var Button = function(widget){
		
		var self = this;
		
		var options = $.extend(true,{
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
		}, defaultOptions, widget.options);
		
		var $element = widget.$element;
		
		this.mode = options.mode;
		this.fn = null;
		
		if(this.mode === 'device'){
			
			var resource = EThing.arbo.findOneById(options.resource);
			if(!resource)
				throw new Error('The resource does not exist anymore');
			if(!(resource instanceof EThing.Device))
				throw new Error('The resource is not a device');
			
			this.fn = function(){
				return resource.execute(options.operation, options.parameters);
			};
			
		} else if(this.mode === 'script'){
			
			var script = options.script;
			if(!(typeof script === 'string' && script.trim().length))
				throw new Error('Invalid script value');
			
			this.fn = function(){
				eval(script);
			};
			
		} else if(this.mode === 'event'){
			
			var event = options.event;
			if(!(typeof event === 'string' && event.trim().length))
				throw new Error('Invalid event value');
			
			this.fn = function(){
				return EThing.Rule.trigger(event);
			};
			
		} else {
			throw new Error('Invalid mode !');
		}
		
		
		/*var $error = $('<span class="glyphicon glyphicon-exclamation-sign" aria-hidden="true" ></span>').css({
			'color': '#d9534f',
			'position': 'absolute',
			'right': '10px',
			'top': '10px'
		}).appendTo($element).tooltip({
			title: function(){
				return $(this).data('error') || 'unknown error';
			},
			placement: 'bottom',
			html: true,
			template: '<div class="tooltip" role="tooltip"><div class="tooltip-arrow" style="border-bottom-color: #D9534F;"></div><div class="tooltip-inner" style="background-color: #D9534F;"></div></div>'
		}).hide();
		
		function setError(e){
			$error.data('error',e && e.message ? e.message : e);
			if(e===false)
				$error.hide().tooltip('hide');
			else
				$error.show();
		}*/
		
		var $button = $('<div><div><a>'+options.title+'</a></div></div>');
		
		$button.css({
			'width': '70%',
			'margin': '0 auto',
			'max-width': '200px'
		});
		
		$button.children().css({
			'width': '100%',
			'height': 0,
			'padding-bottom': '100%',
			'border-radius': '50%',
			'border': '6px solid #f5f5f5',
			'overflow': 'hidden',
			'box-shadow': '0 0 3px gray',
			'box-sizing': 'content-box',
			'position': 'relative',
			'left': '-3px',
			'background-color': options.color,
			'color': '#fafafa'
		});
		
		$button.find('a').css({
			'display': 'block',
			'float': 'left',
			'width': '100%',
			'padding-top': '50%',
			'padding-bottom': '50%',
			'line-height': '1em',
			'margin-top': '-0.5em',
			'text-align': 'center',
			'color': 'inherit',
			'font-size': '1.2em',
			'text-decoration': 'none',
			'cursor': 'pointer'
		});
		
		
		
		//var $button = $('<button type="button" class="btn btn-primary btn-lg">'+options.title+'</button>');
		
		$button.click(function(){
			// remove any previous error
			//$error.hide().tooltip('hide');
			
			$button.find('a').html("loading...");
			
			$button.attr('disabled','disabled')
			var dfr = self.fn.call(self);
			$.when(dfr)
				.done(function(){
					$button.children().css({
						'border-color': '#78c735',
						'background-color': '#d7f7bc',
						'color': '#3c763d'
					});
					$button.find('a').html('success');
				})
				.fail(function(e){
					console.log(e);
					$button.children().css({
						'border-color': '#d9534f',
						'background-color': '#f2dede',
						'color': '#a94442'
					});
					$button.find('a').html('error');
					widget.setWarning(e);
					//$error.data('error',e && e.message ? e.message : e).show();
				})
				.always(function(){
					$button.removeAttr('disabled')
					
					// restore color
					setTimeout(function(){
						$button.children().css({
							'border-color': '#f5f5f5',
							'background-color': '#307bbb',
							'color': '#fafafa'
						});
						$button.find('a').text(options.title);
					},2000);
				});
		});
		
		var $wrapper = $('<div>').append($button).appendTo($element);
		
		$element.css({
			'display': 'table'
		});
		$wrapper.css({
			'display': 'table-cell',
			'vertical-align': 'middle',
			'text-align': 'center'
		});
		
	}
	
	
	
	
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
				"resourceselect"
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
									layoutItem.item.setOptions( r instanceof EThing.Device ? r.operations() : []);
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
		
		instanciate: function(widget){
			new Button(widget);
		}
	};
	
}));