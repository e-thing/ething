(function (root, factory) {
    if (typeof define === 'function' && define.amd) {
        // AMD. Register as an anonymous module.
        define(['require', 'jquery', 'ething', 'form'], factory);
    }
}(this, function (require, $, EThing) {
	
	return {
		
		'bases': ['Device'],
		
		'icon': '<text x="16" y="20" font-size="10" font-family="Bookman Old Style" text-anchor="middle">HTTP</text>',
		
		'name': 'HTTP device',
		
		'description' : 'A HTTP device is a device that use the HTTP protocol. An API KEY will be automatically generated for this device to access your data. Enable the server feature to interact with your device.',
		
		'path' : ['HTTP'],
		
		'properties' : {
			"url": {
				category: 'Server',
				formatter: function(v){
					if(typeof v == 'string'){
						var href = v;
						if(!/^.+:\/\//.test(v))
							href= "http://"+v;
						return '<a href="'+href+'" target="_blank">'+v+'</a>';
					}
				},
				editable:function(){
					
					var url_re = new RegExp('^((.+:)?\\/\\/)?'+ // protocol
						'((([a-z\\d]([a-z\\d-]*[a-z\\d])*)\\.)+[a-z]{2,}|'+ // domain name
						'((\\d{1,3}\\.){3}\\d{1,3})|'+ // OR ip (v4) address
						'localhost)'+ // or localhost
						'(\\:\\d+)?(\\/[-a-z\\d%_.~+]*)*'+ // port and path
						'(\\?[;&a-z\\d%_.~+=-]*)?'+ // query string
						'(\\#[-a-z\\d_]*)?$','i'); // fragment locator
					
					return new $.Form.Text({
						validators: [$.Form.validator.NotEmpty, function(value){
							if(!url_re.test(value)) throw 'invalid URL';
							if(/^.+:\/\//.test(value) && !/^https?:\/\//.test(value)) throw 'invalid protocol, only http or https are allowed.';
						}],
						placeholder: "scheme://hostname:port/path"
					});
				}
			},
			"auth": {
				label: 'authentication',
				category: 'Server',
				formatter: function(v){
					if(v){
						return v.user+':***';
					}
				},
				isOptional: true,
				editable: function(){
					return new $.Form.FormLayout({
						items:[
							{
								name: 'type',
								item: new $.Form.Select(['basic','digest','query'])
							},{
								name: 'user',
								item: new $.Form.Text({
									validators: [$.Form.validator.NotEmpty],
									placeholder: 'user'
								})
							},{
								name: 'password',
								item: new $.Form.Text({
									password: true,
									validators: [$.Form.validator.NotEmpty],
									placeholder: 'password'
								})
							}
						]
					});
				}
			},
			"specification": {
				category: 'Server',
				label: 'api specification',
				get: null, // only editable
				onlyForType: ['Http'],
				isOptional: true,
				description: 'Provide an <a href="http://swagger.io/specification/" target="_blank">OpenAPI Specification</a> describing your device. The specification describes the available requests that your device accepts.',
				editable:function(){
					
					var resource = this.resource;
					
					// async
					var cmDfr = $.Deferred();
					// load codemirror first!
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
						"codemirror/addon/lint/lint.min",
						"css!codemirror/addon/lint/lint.min",
						"https://cdn.rawgit.com/zaach/jsonlint/79b553fb65c192add9066da64043458981b3972b/lib/jsonlint.js",
						"codemirror/addon/lint/json-lint.min",
						"codemirror/addon/scroll/simplescrollbars",
						"css!codemirror/addon/scroll/simplescrollbars",
						"codemirror/addon/display/autorefresh"
					], function(CodeMirror){
						cmDfr.resolve(CodeMirror);
					});
					
					var defaultSpec = {
						"swagger": "2.0",
						"info": {
							"version": "unversioned",
							"title": "untitled"
						},
						"paths": {
							"/example": {
								"get": {
									"description": "An example of a GET request that returns plain text.",
									"produces": [
										"text/plain"
									],
									"responses": {
										"200": {
											"description": "200 response",
											"schema": {
												"type": "string"
											}
										},
										"400": {
											"description": "error"
										}
									}
								}
							}
						}
					};
					
					var value=null;
					
					if(resource instanceof EThing.Device){
						value = $.Deferred();
						
						EThing.Device.Http.getSpecification(resource).then(function(spec){
							value.resolve(spec);
						}, function(){
							value.resolve(defaultSpec);
						});
					}
					
					return $.when(
						$.when(value || defaultSpec).then(function(data){
							return JSON.stringify(data, null, '  ');
						}),
						cmDfr
					).then(function(spec, CodeMirror){
						
						return new $.Form.CustomInput({
							input: function(){
								var $input = $('<div>'), self = this;
								
								this.editor = CodeMirror($input[0], {
									lineNumbers: true,
									value: spec,
									tabSize: 2,
									theme: 'json-api-spec',
									mode: 'application/json',
									lint: true,
									gutters: ["CodeMirror-lint-markers", "CodeMirror-linenumbers", "CodeMirror-foldgutter"],
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
							},
							get: function($e){
								var json = this.editor.getValue(), spec;
								if(!json || json.trim()==='') json = '{}';
								try{
									spec = JSON.parse(json);
								}
								catch(e){
									spec = null;
								}
								return spec;
							},
							validators: [function(value){
								if(value===null) throw 'invalid JSON';
							}, function(value){
								if(value.hasOwnProperty('host'))
									throw 'the host property must not be set';
								if(value.hasOwnProperty('schemes'))
									throw 'the schemes property must not be set';
							}],
							onattach: function(){
								this.parent().toggle(this, resource instanceof EThing.Device && resource.attr('url'));
							}
						});
						
					});
				}
			}
		}
	}
}))