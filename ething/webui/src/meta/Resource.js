(function (root, factory) {
    if (typeof define === 'function' && define.amd) {
        // AMD. Register as an anonymous module.
        define(['require','jquery', 'ething', 'ui/utils', 'form'], factory);
    }
}(this, function (require, $, EThing, UI) {
	
	return {
		
		'icon': '<text x="16" y="24" font-size="22" font-weight="bold" font-family="Arial" text-anchor="middle">R</text>',
		
		'properties' : {
			
			'name': {
				editable:function(){
					return new $.Form.Text({
						validators: [$.Form.validator.NotEmpty]
					});
				}
			},
			'type': {
				
			},
			'id': {
				
			},
			"createdBy": {
				label: "created by",
				formatter: function(createdBy){
					if(!createdBy)
						return 'Me';
					else {
						var createdByRess = EThing.arbo.findOneById(createdBy);
						if(createdByRess instanceof EThing.Device)
							return '<a href="#!device?rid='+createdByRess.id()+'">'+createdByRess.basename()+'</a>';
						else if(createdByRess instanceof EThing.Resource)
							return createdByRess.basename();
					}
				}
			},
			"createdDate": {
				name: "createdDate",
				label: "created",
				formatter: UI.dateToString
			},
			"modifiedDate": {
				name: "modifiedDate",
				label: "modified",
				formatter: UI.dateToString
			},
			"description": {
				editable: function(){
					return new $.Form.Textarea({
						placeholder: "describe this resource"
					})
				}
			},
			"public": {
				label: 'share',
				description: 'Make this resource public: anyone who have the link could access it.',
				formatter: function(value){
					return value===false ? 'private' : value;
				},
				editable: function(resource){
					
					if(!(resource instanceof EThing.Resource)) return;
					
					return new $.Form.Select({
						items: {
							'private' : false,
							'public: read only': 'readonly',
							'public: read & write': 'readwrite'
						},
						value: false,
						onload: function(){
							this.change(function(){
								
								var $info = this.$view.find('.share-link');
								if(!$info.length){
									$info = $('<div class="share-link">').html('<h5>shareable link :</h5><p></p>').appendTo(this.$view);
								}
								
								$info.hide();
								
								switch(this.value()){
									case 'readonly':
									case 'readwrite':
										if(resource.getContentUrl){
											var link = resource.getContentUrl();
											$info.show().find('p').text(link);
										}
										break;
								}
								
								
							}).change();
						}
					});
				}
			},
			"data": {
				category: 'data',
				editable: function(resource){
					/*return new $.Form.FormLayout({
						editable: true
					});*/
					
					// async
					var dfr = $.Deferred();
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
						dfr.resolve(new $.Form.CustomInput({
							input: function(){
								var $html = $('<div class="f-resourcedata"><div class="container-fluid"><div class="content"></div><div class="row footer"></div></div></div>'), self = this;
								
								this.map = {};
								this.invalid = {};
								
								var $newDataBtn = $('<button class="btn btn-default" type="submit"><span class="glyphicon glyphicon-plus" aria-hidden="true"></span> add</button>').click(function(){
									var key = $newDataKeyInput.val() || '';
									if(key.length)
										self.add(key);
									$newDataKeyInput.val('');
								});
								var $newDataKeyInput = $('<input type="text" class="form-control" placeholder="key">');
								
								$('<div class="col-sm-offset-4 col-sm-8">').append($('<div class="input-group input-group-sm">').append($newDataKeyInput, $('<span class="input-group-btn">').append($newDataBtn))).appendTo($html.find('.footer'));
								
								this.add = function(key, value){
									var $tr = $('<div class="row">').attr('data-key', key), self = this, $value = $('<div>');
									
									var $remove = $('<button class="btn btn-link btn-xs" type="submit"><span class="glyphicon glyphicon-trash" aria-hidden="true"></span></button>').click(function(){
										$tr.remove();
										self.map[key].removed = true;
										self.map[key].editor = null;
									});
									
									var editor = CodeMirror($value[0], {
										value: JSON.stringify(value, null, '  ') || '',
										tabSize: 2,
										theme: 'json-api-spec',
										mode: 'application/json',
										lint: true,
										gutters: false,
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
									
									$tr.append(
										$('<div class="col-sm-4">').append('<span>'+key+'</span> ', $remove),
										$('<div class="col-sm-8">').append($value)
									)
									
									this.map[key] = {
										editor: editor,
										removed: false
									};
									
									$tr.appendTo(this.$view.find('.content'));
								};
								
								return $html;
							},
							set: function($e,data){
								for(var key in data){
									this.add(key, data[key]);
								}
							},
							get: function($e){
								var v = {};
								for(var key in this.map){
									if(this.map[key].removed)
										v[key] = null;
									else {
										var iv = this.map[key].editor.getValue();
										try{
											v[key] = JSON.parse(iv);
										}
										catch(e){
											v[key] = this.invalid;
										}
									}
								}
								return v;
							},
							validators: [function(value){
								for(var key in value){
									if(value[key] === this.invalid)
										throw 'the key "'+key+'" contains invalid data';
								}
							}]
						}));
					});
					
					return dfr;
				}
			}
		}
		
	}
}))