(function (root, factory) {
    if (typeof define === 'function' && define.amd) {
        // AMD. Register as an anonymous module.
        define(['jquery', 'ething', 'form'], factory);
    }
}(this, function ($) {
	
	var UI = window.UI = window.UI || {};
	
	
	var url_re = new RegExp('^((.+:)?\\/\\/)?'+ // protocol
			'((([a-z\\d]([a-z\\d-]*[a-z\\d])*)\\.)+[a-z]{2,}|'+ // domain name
			'((\\d{1,3}\\.){3}\\d{1,3})|'+ // OR ip (v4) address
			'localhost)'+ // or localhost
			'(\\:\\d+)?(\\/[-a-z\\d%_.~+]*)*'+ // port and path
			'(\\?[;&a-z\\d%_.~+=-]*)?'+ // query string
			'(\\#[-a-z\\d_]*)?$','i'); // fragment locator
	
	
	var properties = [
		
		/*
		
		"property":{
			name: "foo", // the name of this property
			label:"name displayed for that property" (default: property's name),
			get:"name of the accessor in the resource object" (default: property's name),
			onlyForType:[], this property is only avalable for the specified types
			notForType:[], this property is not avalable for the specified types
			formatter:function(value){return value;}, value formatter
			default: print the default value for undefined value
			editable:false || Form.Item instance
		}
		
		*/
		
		{
			name: "name",
			editable:function(){
				return new $.Form.Text({
					validators: [$.Form.validator.NotEmpty]
				});
			}
		},
		
		{
			name: "type",
			formatter: function(type){
				return type.replace(/^Device\\/,'');
			}
		},
		
		{
			name: "id"
		},
		
		{
			name: "createdBy",
			label: "created by",
			formatter: function(createdBy){
				if(!createdBy)
					return 'Me';
				else {
					
					if(EThing.arbo.isLoaded()){
						var createdByRess = EThing.arbo.findOneById(createdBy.id);
						return createdByRess ? /*createdBy.type+':'+*/createdByRess.basename() : 'An old '+createdBy.type;
					}
					return 'A '+createdBy.type;
				}
			}
		},
		{
			name: "createdDate",
			label: "created",
			get: "ctime",
			formatter: UI.dateToString
		},
		{
			name: "modifiedDate",
			label: "modified",
			get: "mtime",
			formatter: UI.dateToString
		},
		{
			name: "lastSeenDate",
			onlyForType: ['Device'],
			label: "last seen",
			formatter: function(date){
				return date ? UI.dateToString(date) : 'never';
			}
		},
		/*{
			name: "lastSeenDate",
			onlyForType: ['Device'],
			label: "last seen",
			formatter: function(date){
				return date ? UI.dateDiffToString( Math.floor( (Date.now() - date.getTime()) / 1000 ) ) : 'never';
			}
		},*/
		{
			name: "size",
			formatter: UI.sizeToString,
			default: 0
		},
		{
			name: "mime",
			label: "mime type",
			onlyForType: ['File'],
		},
		{
			name: "length",
			label: "rows",
			onlyForType: ['Table'],
			default: 0
		},
		{
			name: "maxLength",
			label: "max rows",
			onlyForType: ['Table'],
			formatter: function(v){
				return v ? String(v) : "none";
			},
			isOptional: true,
			editable:function(){
				return new $.Form.Number({
					minimum: 1,
					value: 100
				});
			}
		},
		{
			name: "expireAfter",
			label: "expire after",
			description: "This resource will be automatically removed after a specific duration of inactivity.",
			formatter: function(v){
				return v ? UI.dateDiffToString(v) : "never";
			},
			isOptional: true,
			editable: function(){
				return new $.Form.Duration({
					minute: false,
					hour: true,
					day: true,
					value: 86400
				});
			}
		},
		{
			name: "icon",
			onlyForType: ['App'],
			isOptional: true,
			get: function(r){
				return r.iconLink(true);
			},
			editable: function(r){
				return new $.Form.Image({
					imageTransform: function(blob){
						// crop the image into a 128x128px image
						return imageSquareResizeBlob(blob, 128);
					}
				});
			}
		},
		{
			name: "battery",
			onlyForType: ['Device'],
			formatter: function(batValue){
				return (typeof batValue == 'number') ? batValue+"%" : 'no battery';
			}
		},
		{
			name: "url",
			category: 'Server',
			onlyForType: ['Device\\Http'],
			formatter: function(v){
				if(typeof v == 'string'){
					var href = v;
					if(!/^.+:\/\//.test(v))
						href= "http://"+v;
					return '<a href="'+href+'" target="_blank">'+v+'</a>';
				}
			},
			editable:function(){
				return new $.Form.Text({
					validators: [$.Form.validator.NotEmpty, function(value){
						if(!url_re.test(value)) throw 'invalid URL';
						if(/^.+:\/\//.test(value) && !/^https?:\/\//.test(value)) throw 'invalid protocol, only http or https are allowed.';
					}],
					placeholder: "scheme://hostname:port/path"
				});
			}
		},
		{
			name: "auth",
			label: 'authentication',
			category: 'Server',
			onlyForType: ['Device\\Http'],
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
		{
			name: "url",
			onlyForType: ['Device\\RTSP'],
			editable:function(){
				return new $.Form.Text({
					prefix: 'rtsp://',
					validators: [$.Form.validator.NotEmpty, function(value){
						if(!url_re.test('rtsp://'+value)) throw 'invalid URL';
					}],
					placeholder: "hostname:port/path",
					format:{
						'in': function(value){
							return value.replace(/^rtsp:\/\//, '');
						},
						'out': function(value){
							return 'rtsp://'+value;
						}
					}
				});
			},
			description: 'The url of the device.'
		},
		{
			name: "transport",
			onlyForType: ['Device\\RTSP'],
			editable:function(){
				return new $.Form.Select(['tcp','udp','http']);
			},
			description: 'Lower transport protocol.'
		},
		{
			name: "host",
			onlyForType: ['Device\\MQTT'],
			editable:function(){
				return new $.Form.Text({
					validators: [$.Form.validator.NotEmpty],
					placeholder: "hostname"
				});
			},
			description: 'The hostname of the MQTT broker.'
		},
		{
			name: "port",
			onlyForType: ['Device\\MQTT'],
			default: 1883,
			editable:function(){
				return new $.Form.Number({
					validators: [$.Form.validator.Integer],
					placeholder: "port",
					value: 1883,
					minimum: 1,
					maximum: 65535,
				});
			},
			description: 'The port number of the MQTT broker.'
		},
		{
			name: "auth",
			label: 'authentication',
			onlyForType: ['Device\\MQTT'],
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
		{
			name: "topic",
			isOptional: true,
			onlyForType: ['Device\\MQTT'],
			editable:function(){
				return new $.Form.Text({
					validators: [$.Form.validator.NotEmpty],
					placeholder: "topic"
				});
			},
			description: 'The topic to subscribe to.'
		},
		{
			name: "description",
			editable: function(){
				return new $.Form.Textarea({
					placeholder: "describe this resource"
				})
			}
		},
		{
			name: "location",
			onlyForType: ['Device'],
			formatter: function(v){
				var parts = [];
				if(v){
					if( typeof v.latitude != 'undefined' && typeof v.longitude != 'undefined')
						parts.push( v.latitude+"N "+v.longitude+"E" );
					if( typeof v.place != 'undefined' ) parts.push(v.place);
					if( typeof v.floor != 'undefined' ) parts.push('floor:'+v.floor);
					if( typeof v.room != 'undefined' ) parts.push(v.room);
				}
				return parts.length ? parts.join(',') : 'somewhere on earth';
			},
			isOptional: true,
			editable: function(){
				return new $.Form.FormLayout({
					skipOnDisabled: true,
					items:[
						{
							name: 'coordinates',
							item: new $.Form.FormLayout({
								items: [{
									name: 'latitude',
									item: new $.Form.Number({
										validators: [$.Form.validator.NotEmpty],
										placeholder: "latitude"
									})
								},{
									name: 'longitude',
									item: new $.Form.Number({
										validators: [$.Form.validator.NotEmpty],
										placeholder: "longitude"
									})
								}]
							}),
							checkable: true
						},{
							name: 'place',
							item: new $.Form.Text({
								validators: [$.Form.validator.NotEmpty],
								placeholder: "place"
							}),
							checkable: true
						},{
							name: 'floor',
							item: new $.Form.Number({
								validators: [$.Form.validator.NotEmpty],
								placeholder: "floor"
							}),
							checkable: true
						},{
							name: 'room',
							item: new $.Form.Text({
								validators: [$.Form.validator.NotEmpty],
								placeholder: "room"
							}),
							checkable: true
						}
					],
					format: {
						'out': function(value){
							if($.isPlainObject(value) && !$.isEmptyObject(value)){
								var o = $.extend({},value, value.coordinates);
								delete o.coordinates;
								return o;
							}
							return null;
						},
						'in': function(value){
							if($.isPlainObject(value) && !$.isEmptyObject(value)){
								var o = $.extend({},value);
								if( typeof o.latitude != 'undefined' && typeof o.longitude != 'undefined'){
									o.coordinates = {
										latitude: o.latitude,
										longitude: o.longitude
									};
									delete o.latitude;
									delete o.longitude;
								}
								return o;
							} else return {};
						}
					}
				});
			}
		},
		{
			name: "scope",
			label: 'permission',
			description: 'Restrict this resource to the following permissions :',
			onlyForType: ['Device\\Http','App'],
			formatter: function(){
				return null;
			},
			editable:function(resource){
				
				// async
				var depDfr = $.Deferred();
				require(["scopeform"], function(){
					depDfr.resolve(new $.Form.CustomInput({
						input: function(){
							var $input = $('<div>').text('loading...'), self = this;
							$input.empty().scopeForm();
							$input.on('change', function(){
								self.update();
							});
							return $input;
						},
						set: function($e,v){
							$e.scopeForm('value',v)
						},
						get: function($e){
							return $e.scopeForm('value');
						},
						value: ''
					}));
					
				});
				
				return depDfr;
			}
		},
		{
			name: "specification",
			category: 'Server',
			label: 'api specification',
			get: null, // only editable
			onlyForType: ['Device\\Http'],
			isOptional: true,
			description: 'Provide an <a href="http://swagger.io/specification/" target="_blank">OpenAPI Specification</a> describing your device.',
			editable:function(resource){
				
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
					
					resource.getSpecification().then(function(spec){
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
							this.parent().toggle(this, resource instanceof EThing.Device.Http && resource.url());
						}
					});
					
				});
			}
		},
		{
			name: "version",
			formatter: function(v){
				return v || 'unversioned';
			},
			onlyForType: ['App','Device\\RFLink.*Gateway']
		},
		{
			name: "isMetric",
			onlyForType: ['Device\\MySensors.*Gateway'],
			editable: function(){
				return new $.Form.Checkbox({
					value: true
				});
			}
		},
		{
			name: "libVersion",
			onlyForType: ['Device\\MySensors.*Gateway']
		},
		{
			name: "transport",
			onlyForType: ['Device\\MySensorsGateway'],
			editable: function(){
				return new $.Form.Select({
					items: ['ethernet', 'serial']
				});
			}
		},
		{
			name: "address",
			onlyForType: ['Device\\MySensorsGateway', 'Device\\MySensorsEthernetGateway'],
			editable: function(){
				return new $.Form.Text({
					placeholder: '192.168.1.116:5003',
					validators: [$.Form.NotEmpty, function(value){
						if(!/^(([0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3})|([\w-.]+))(:[0-9]{1,5})?$/.test(value))
							throw 'invalid address';
					}]
				});
			}
		},
		{
			name: "inclusion",
			onlyForType: ['Device\\RFLink.*Gateway'],
			editable: function(){
				return new $.Form.Checkbox();
			}
		},
		{
			name: "revision",
			onlyForType: ['Device\\RFLink.*Gateway']
		},
		{
			name: "build",
			onlyForType: ['Device\\RFLink.*Gateway']
		},
		{
			name: "port",
			onlyForType: ['Device\\MySensorsGateway', 'Device\\MySensorsSerialGateway', 'Device\\RFLinkSerialGateway'],
			editable: function(){
				return $.getJSON('../tools/serialPortsList.php').then(function(ports){
					
					return new $.Form.Text({
						placeholder: '/dev/ttyS0',
						validators: [$.Form.validator.NotEmpty],
						comboboxValues: ports.map(function(port){
							return {
								'name': port.device,
								'label': port.device+' <small style="color:grey;">'+port.description+'</small>'
							};
						})
					});
					
				});
				
			}
		},
		{
			name: "baudrate",
			onlyForType: ['Device\\MySensorsGateway', 'Device\\MySensorsSerialGateway', 'Device\\RFLinkSerialGateway'],
			editable: function(resource){
				return new $.Form.Select({
					items: [
						110,
						150,
						300,
						600,
						1200,
						2400,
						4800,
						9600,
						19200,
						38400,
						57600,
						115200
					],
					value: resource === 'Device\\RFLinkSerialGateway' ? 57600 : 115200
				});
			}
		},
		{
			name: "nodeId",
			onlyForType: ['Device\\MySensorsNode','Device\\MySensorsSensor'],
			editable: function(){
				return new $.Form.Number({
					minimum: 1,
					maximum: 254,
					value: 1,
					placeholder: 'nodeId',
					validators: [$.Form.validator.Integer]
				});
			}
		},
		{
			name: "sensorId",
			onlyForType: ['Device\\MySensorsSensor'],
			editable: function(){
				return new $.Form.Number({
					minimum: 0,
					maximum: 254,
					placeholder: 'sensorId',
					validators: [$.Form.validator.Integer]
				});
			}
		},
		{
			name: "sensorType",
			onlyForType: ['Device\\MySensorsSensor'],
			editable: function(){
				return new $.Form.Select({
					items: [
						'S_AIR_QUALITY',
						'S_ARDUINO_NODE',
						'S_ARDUINO_REPEATER_NODE',
						'S_BARO',
						'S_BINARY',
						'S_CAM',
						'S_COLOR_SENSOR',
						'S_COVER',
						'S_CUSTOM',
						'S_DIMMER',
						'S_DISTANCE',
						'S_DOOR',
						'S_DUST',
						'S_GAS',
						'S_GPS',
						'S_HEATER',
						'S_HUM',
						'S_HVAC',
						'S_INFO',
						'S_IR',
						'S_LIGHT',
						'S_LIGHT_LEVEL',
						'S_LOCK',
						'S_MOISTURE',
						'S_MOTION',
						'S_MULTIMETER',
						'S_POWER',
						'S_RAIN',
						'S_RGB_LIGHT',
						'S_RGBW_LIGHT',
						'S_SCENE_CONTROLLER',
						'S_SMOKE',
						'S_SOUND',
						'S_SPRINKLER',
						'S_TEMP',
						'S_UV',
						'S_VIBRATION',
						'S_WATER',
						'S_WATER_LEAK',
						'S_WATER_QUALITY',
						'S_WEIGHT',
						'S_WIND'
					]
				});
			}
		},
		{
			name: "sketchName",
			onlyForType: ['Device\\MySensorsNode']
		},
		{
			name: "sketchVersion",
			onlyForType: ['Device\\MySensorsNode']
		},
		{
			name: "smartSleep",
			onlyForType: ['Device\\MySensorsNode'],
			editable: function(){
				return new $.Form.Checkbox();
			}
		},
		{
			name: "data",
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
		},
		{
			name: "public",
			label: 'share',
			description: 'Make this resource public: anyone who have the link could access it.',
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
		{
			name: "host",
			onlyForType: ['Device\\Denon', 'Device\\Yeelight.*'],
			editable:function(){
				return new $.Form.Text({
					validators: [$.Form.validator.NotEmpty],
					placeholder: "IP address"
				});
			},
			description: 'The IP address of the device.'
		}
	];
	
	
	// set default to properties:
	for(var i=0; i<properties.length; i++)
		properties[i] = $.extend({
			label:properties[i].name,
			get:properties[i].name,
			condition:true,// the condition to tell if this property is enable or not
			onlyForType: null,
			notForType:[],
			formatter: null,
			//default: undefined
			editable:null
		},properties[i]);
	
	
	function getResourceProperties(resource, extendProps, filter){
		var out = [],
			resourceType = (resource instanceof EThing.Resource) ? resource.type() : resource,
			undefined;
		
		for(var i=0; i<properties.length; i++){
			
			var property = $.extend(true, {
				resource: (resource instanceof EThing.Resource) ? resource : null,
				resourceType: resourceType
			}, properties[i], ($.isPlainObject(extendProps) && extendProps.hasOwnProperty(properties[i].name)) ? extendProps[properties[i].name] : null);
			
			var condition = property.condition;
			if(typeof condition == 'function')
				condition = condition.call(property);
			if(!condition)
				continue;
			
			if(Array.isArray(filter) && filter.indexOf(property.name) === -1)
				continue; // show only properties listed in the argument 'properties'.
			
			if((typeof filter == 'function') && !filter.call(property,property,resource))
				continue;
			
			var pass = true;
			
			property.notForType.forEach(function(classname){
				if( (new RegExp('^'+classname.replace('\\','\\\\')+'($|[.\\\\])')).test(resourceType) ){
					pass = false;
					return false;
				}
			});
			
			if(pass && property.onlyForType){
				pass = false;
				property.onlyForType.forEach(function(classname){
					if( (new RegExp('^'+classname.replace('\\','\\\\')+'($|[.\\\\])')).test(resourceType) ){
						pass = true;
						return false;
					}
				});
			}
			
			if(pass){
				
				var value = undefined,
					hasDefaultValue = (typeof property.default != 'undefined');
				
				// get the value
				if(resource instanceof EThing.Resource){
					if(typeof property.get == 'function')
						value = property.get.call(property,resource);
					else if(typeof property.get == 'string'){
						var accessor = EThing.getClass(resourceType).prototype[property.get];
						if(typeof accessor == "undefined")
							continue;
						value = (typeof accessor == 'function') ? accessor.call(resource) : accessor;
					}
				}
				
				if(typeof value == "undefined"){
					if(hasDefaultValue)
						value = property.default;
				}
				
				if(typeof value != "undefined"){
					property.value = value;
					if(typeof property.formatter == 'function')
						property.formattedValue = property.formatter.call(property,value);
					else
						property.formattedValue = String(value);
				}
				
				if(typeof property.label == 'function')
					property.label = property.label.call(property);
				
				out.push(property);
				
			}
		}
		return out;
	}
	
	function getResourceProperty(resource, property){
		return getResourceProperties(resource,null,[property]).shift();
	}
	
	function getResourceFormattedValues(resource, extendProps, filter){
		var pps = getResourceProperties(resource,extendProps,filter),
			out = {};
		
		for(var i=0; i<pps.length; i++){
			var property = pps[i];
			if((typeof property.formattedValue != 'undefined') && property.formattedValue !== null)
				out[property.label] = property.formattedValue;
		}
		
		return out;
	}
	
	
	function getResourceForm(resource, extendProps, filter){
		var pps = getResourceProperties(resource,extendProps,filter),
			dfrs = [];
		
		pps.forEach(function(property){
			
			var formItemDfr = typeof property.editable == 'function' ? property.editable.call(property,resource) : null;
			
			dfrs.push(
				$.when(formItemDfr).then(function(formItem){
					if(formItem instanceof $.Form.Item){
						formItem.name = property.name;
						
						if(typeof property['value'] != 'undefined')
							formItem.value(property.value);
						
						return {
							label: property.label,
							name: property.name,
							checkable: !!property.isOptional,
							checked: typeof property.value != 'undefined' && property.value!==null,
							item: formItem,
							description: property.description
						};
						
					}
				})
			);
			
		}, this);
		
		return $.when.apply($, dfrs).then(function(){
			
			var formItems = dfrs.length===1 ? [arguments[0]] : Array.prototype.slice.call(arguments);
			var out = [];
			formItems.forEach(function(formItem){
				if(formItem) out.push(formItem);
			})
			
			return out;
		});
	}
	
	
	$.extend(true,UI, {
		properties: properties,
		getResourceProperties: getResourceProperties,
		getResourceProperty: getResourceProperty,
		getResourceFormattedValues: getResourceFormattedValues,
		getResourceForm: getResourceForm
	});
	
	return UI;
	
}));