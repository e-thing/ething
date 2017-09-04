(function (root, factory) {
    if (typeof define === 'function' && define.amd) {
        // AMD. Register as an anonymous module.
        define(['js/ui', 'text!./rules.html', 'jquery', 'ething', 'cronstrue', 'js/ui', 'css!./rules',
			'formmodal',
			'resourceselect',
			'http',
			'devicerequest',
			'table',
			'css!bootstrap-toggle-flat'], factory);
    }
}(this, function (UI, template, $, EThing, cronstrue) {
	
	function escape(unsafe) {
		return unsafe
			 .replace(/&/g, "&amp;")
			 .replace(/</g, "&lt;")
			 .replace(/>/g, "&gt;")
			 .replace(/"/g, "&quot;")
			 .replace(/'/g, "&#039;");
	 };
	
	var hsv2rgb = function(h, s, v) {
	  // adapted from http://schinckel.net/2012/01/10/hsv-to-rgb-in-javascript/
	  var rgb, i, data = [];
	  if (s === 0) {
		rgb = [v,v,v];
	  } else {
		h = h / 60;
		i = Math.floor(h);
		data = [v*(1-s), v*(1-s*(h-i)), v*(1-s*(1-(h-i)))];
		switch(i) {
		  case 0:
			rgb = [v, data[2], data[0]];
			break;
		  case 1:
			rgb = [data[1], v, data[0]];
			break;
		  case 2:
			rgb = [data[0], v, data[2]];
			break;
		  case 3:
			rgb = [data[0], data[1], v];
			break;
		  case 4:
			rgb = [data[2], data[0], v];
			break;
		  default:
			rgb = [v, data[0], data[1]];
			break;
		}
	  }
	  return '#' + rgb.map(function(x){
		return ("0" + Math.round(x*255).toString(16)).slice(-2);
	  }).join('');
	};


	function priorityToColor(val, min, max){
		
		val = min==max ? 50 : (100 * (val-min) / (max-min));
		
		if (val > 100) {
			val = 100;
		}
		else if (val < 0) {
			val = 0;
		}
		
		//var h= Math.floor((100 - val) * 120 / 100);
		var h= Math.floor((100 - val) * 40 / 100)+200;
		var s = 1; //Math.abs(val - 50)/50;
		var v = 1;
		
		var color = hsv2rgb(h, s, v);
		
		return color;
	}
	
	
	
	var ResourceSelection = {
		
		toString: function(resource, type){
			if(typeof type == 'undefined') type = 'resource';
			if(typeof resource == 'undefined' || resource === null)
				return "a "+type;
			else if(Array.isArray(resource)) {
				if(resource.length===1) return ResourceSelection.toString(resource[0], type);
				return "one of the "+type+"s "+resource.map(function(r){
					r = EThing.arbo.findOneById(r);
					if(r)
						return "<mark>"+r.name()+"</mark>";
					else
						return "#"+r+" (does not exist anymore!)";
				}).join(',');
			} else if( EThing.utils.isId(resource) ){
				var r = EThing.arbo.findOneById(resource);
				if(r) {
					return "the "+type+" <mark>"+r.name()+"</mark>";
				} else {
					return "the "+type+" with id '"+resource+"' (does not exist anymore!)";
				}
			}
			else 
				return "a "+type+" that match the expression <code>"+escape(resource)+"</code>";
		},
		
		form: function(options){
			options = $.extend({
				all : true,
				selection : true,
				expression: true,
				emitter: false,
				prefix: '',
				filter: null,
				resourcesName: 'resources'
			}, options);
			
			var items = [];
			
			options.prefix = (typeof options.prefix === 'string' && options.prefix.length) ? options.prefix+' ' : '';
				
			if(options.emitter){
				items.push({
					label: options.prefix+'the resource emitting this signal',
					name: 'emitter',
					item: new $.Form.Constant('#emitter')
				});
			}
			if(options.all){
				items.push({
					label: options.prefix+'any '+options.resourcesName,
					name: 'all',
					item: new $.Form.NullItem()
				});
			}
			if(options.selection){
				items.push({
					label: options.prefix+'specific '+options.resourcesName+'...',
					name: 'selection',
					item: new $.Form.ResourceSelect({
						multiple: true,
						allowCreation: false,
						filter: options.filter,
						validators: [$.Form.validator.NotEmpty] 
					})
				});
			}
			if(options.expression){
				items.push({
					label: options.prefix+options.resourcesName+' that match the following expression...',
					name: 'expression',
					item: new $.Form.Text({
						validators: [$.Form.validator.NotEmpty],
						placeholder: 'size > 0 AND name $= ".txt"'
					})
				});
			}
			
			return new $.Form.SelectPanels({
				items: items,
				value: options.emitter ? '#emitter' : '',
				format: {
					'out': function(value){
						return value.value;
					},
					'in': function(value){
						if(value==='#emitter')
							return {
								type: 'emitter',
								value: value
							};
						if(Array.isArray(value) || EThing.utils.isId(value))
							return {
								type: 'selection',
								value: value
							};
						if(typeof value==='string' && value.length)
							return {
								type: 'expression',
								value: value
							};
						return {
							type: 'all',
							value: value
						};
					}
				}
			});
		}
	}
	
	
	var Rule = {};
	
	Rule.events = [
	
	{
		type: 'Custom', // the event type name
		name: 'Custom event', // the name of the event
		category: 'general',
		toString: function(options){
			var str = "the event <mark>" + options.name + "</mark> is fired";
			if(options.resource)
				str += ' by ' + ResourceSelection.toString(options.resource,'device');
			return str;
		},
		description: 'This event describe a custom event. A custom event is identified by a unique name and may be fired by user request or by another rule which is very usefull for nesting multiple rules.', // an optional description
		form: function(){ // editable or not ? if yes, must be a function returning a Form
			return new $.Form.FormLayout({
				items: [{
					name: 'name',
					description: 'Set the name of this custom event.',
					item: new $.Form.Text({
						placeholder: "myCustomEvent",
						validators: [$.Form.validator.NotEmpty] 
					})
				},{
					name: 'resource',
					description: 'Select on which resource this event must be bind to.',
					item: ResourceSelection.form({
						'filter' : function(r){
							return r instanceof EThing.Device;
						},
						prefix: 'on'
					}),
					class: 'item-expert'
				}],
				disabledValue: undefined
			});
		}
	},
	
	
	{
		type: 'Timer', 
		name: 'at fixed times, dates, or intervals',
		category: 'general',
		toString: function(options){
			try {
				return cronstrue.toString(options.cron);
			} catch(e){
				console.warn(e);
				return "time match the cron expression <code>"+options.cron+"</code>";
			}
		},
		description: 'Emit an event at fixed times, dates, or intervals.',
		form: function(){
			return new $.Form.Cron();
		}
	},
	
	{
		type: 'DeviceUnreachable',
		name: 'Device disconnected',
		category: 'device',
		toString: function(options){
			return ResourceSelection.toString(options.resource,'device')+' becomes unreachable';
		},
		description: null,
		form: function(){
			return new $.Form.FormLayout({
				items: [{
					name: 'resource',
					description: 'Select on which device this event must be bind to.',
					item: ResourceSelection.form({
						'filter' : function(r){
							return (r instanceof EThing.Device.Http) || (r instanceof EThing.Device.RTSP) || (r instanceof EThing.Device.Denon);
						},
						prefix: 'on',
						resourcesName: 'devices'
					})
				}],
				disabledValue: undefined
			});
		}
	},
	
	{
		type: 'LowBatteryDevice',
		name: 'Device low battery level',
		category: 'device',
		toString: function(options){
			return ResourceSelection.toString(options.resource,'device') +' has low batery level';
		},
		description: null,
		form: function(){
			return new $.Form.FormLayout({
				items: [{
					name: 'resource',
					description: 'Select on which device this event must be bind to.',
					item: ResourceSelection.form({
						'filter' : function(r){
							return r instanceof EThing.Device;
						},
						prefix: 'on',
						resourcesName: 'devices'
					})
				}],
				disabledValue: undefined
			});
		}
	},
	
	{
		type: 'FileDataModified',
		name: 'File data modified',
		category: 'file',
		toString: function(options){
			return 'The content of '+ResourceSelection.toString(options.resource,'file') + ' has been modified';
		},
		description: 'This event is fired each time the content of a file has been modified.',
		form: function(){
			return new $.Form.FormLayout({
				items: [{
					name: 'resource',
					description: 'Select on which file this event must be bind to.',
					item: ResourceSelection.form({
						'filter' : function(r){
							return r instanceof EThing.File;
						},
						prefix: 'on',
						resourcesName: 'files'
					})
				}],
				disabledValue: undefined
			});
		}
	},
	{
		type: 'TableDataAdded',
		name: 'Table data added',
		category: 'table',
		toString: function(options){
			return ResourceSelection.toString(options.resource, 'table') + ' has new data';
		},
		description: 'This event is fired each time a new data is added to a table.',
		form: function(){
			return new $.Form.FormLayout({
				items: [{
					name: 'resource',
					description: 'Select on which table this event must be bind to.',
					item: ResourceSelection.form({
						'filter' : function(r){
							return r instanceof EThing.Table;
						},
						prefix: 'on',
						resourcesName: 'tables'
					})
				},{
					name: 'filter',
					description: 'Set an expression to filter more precisely the event. For instance, you may enter an expression to fired this rule only when a value greater than a threshold is inserted to the table.',
					item: new $.Form.Text({
						validators: [$.Form.validator.NotEmpty],
						placeholder: 'value > 0'
					}),
					checkable: true
				}],
				disabledValue: undefined
			});
		}
	},
	{
		type: 'ResourceCreated',
		name: 'Resource created',
		category: 'resource',
		toString: function(options){
			return ResourceSelection.toString(options.resource) + ' has been created';
		},
		description: 'This event is fired each time a resource (File, Table, Device ...) has been created.',
		form: function(){
			return new $.Form.FormLayout({
				items: [{
					name: 'resource',
					description: 'Select on which resource this event must be bind to.',
					item: ResourceSelection.form({
						'selection' : false,
						prefix: 'on'
					})
				}],
				disabledValue: undefined
			});
		}
	},
	{
		type: 'ResourceDeleted',
		name: 'Resource deleted',
		category: 'resource',
		toString: function(options){
			return ResourceSelection.toString(options.resource) + ' has been deleted';
		},
		description: 'This event is fired each time a resource (File, Table, Device ...) has been deleted.',
		form: function(){
			return new $.Form.FormLayout({
				items: [{
					name: 'resource',
					description: 'Select on which resource this event must be bind to.',
					item: ResourceSelection.form({
						prefix: 'on'
					})
				}],
				disabledValue: undefined
			});
		}
	},
	{
		type: 'ResourceMetaUpdated',
		name: 'Resource modified',
		category: 'resource',
		toString: function(options){
			return (options.attributes ? ('the attributes '+options.attributes.map(function(n){
				return '"'+n+'"';
			}).join(',')+' of ') : '') + ResourceSelection.toString(options.resource) + ' has been modified';
		},
		description: 'This event is fired each time a resource (File, Table, Device ...) has been updated.',
		form: function(){
			return new $.Form.FormLayout({
				items: [{
					name: 'resource',
					description: 'Select on which resource this event must be bind to.',
					item: ResourceSelection.form({
						prefix: 'on'
					})
				}, {
					name: 'attributes',
					description: 'Select the attributes you want to watch for change. If this feature is disabled, this event will be triggered regardless of the attribute.',
					item: new $.Form.Select({
						items: ['name','modifiedDate','description','data','public','expireAfter','size','isText','mime','maxLength','length','keys','scope','version','lastSeenDate','battery','location','url','specification','auth','isMetric','address','port','baudrate','nodeId','smartSleep','firmware','nodeId','sketchName','sketchVersion','sensorId','sensorType'],
						multiple: true,
						validators: [$.Form.validator.NotEmpty]
					}),
					checkable: true
				},{
					name: 'filter',
					description: 'Set an expression to filter more precisely the event.',
					item: new $.Form.Text({
						validators: [$.Form.validator.NotEmpty],
						placeholder: 'size > 500'
					}),
					checkable: true
				}],
				disabledValue: undefined
			});
		}
	},
	
	{
		type: 'DeviceDataSet',
		name: 'Device data emitted',
		category: 'device',
		toString: function(options){
			return ResourceSelection.toString(options.resource, 'device') + ' send data';
		},
		description: 'Is fired each time a device send data.',
		form: function(){
			return new $.Form.FormLayout({
				items: [{
					name: 'resource',
					description: 'Select on which device this event must be bind to.',
					item: ResourceSelection.form({
						'filter' : function(r){
							return r instanceof EThing.Device.RFLinkSwitch || r instanceof EThing.Device.MySensorsSensor;
						},
						prefix: 'on',
						resourcesName: 'devices'
					})
				}],
				disabledValue: undefined
			});
		}
	},
	
	];
	
	
	Rule.conditions = [
	
	{
		type: 'ResourceMatch',
		name: 'Resource match an expression', 
		toString: function(options){
			return ResourceSelection.toString(options.resource)+" match <code>"+escape(options.expression)+"</code>";
		},
		description: null,
		form: function(){
			return new $.Form.FormLayout({
				items: [{
					name: 'resource',
					description: 'Select on which resource this condition must be executed.',
					item: ResourceSelection.form({
						emitter: true,
						prefix: 'on'
					})
				},{
					name: 'expression',
					description: 'This condition returns true only if the selected resource(s) match the following expression.',
					item: new $.Form.Text({
						validators: [$.Form.validator.NotEmpty],
						placeholder: 'size > 0 AND name $= ".txt"'
					})
				}]
			});
		}
	},
	
	{
		type: 'Cron',
		name: 'time match a cron expression', 
		toString: function(options){
			try {
				return cronstrue.toString(options.cron);
			} catch(e){
				console.warn(e);
				return "time match the cron expression <code>"+options.cron+"</code>";
			}
		},
		description: null,
		form: function(){
			return new $.Form.Cron();
		}
	},
	
	];
	
	
	Rule.actions = [
	
	{
		type: 'Notify',
		name: 'Notify', 
		toString: function(options){
			return "send a notification with the subject <mark>"+options.subject+"</mark>";
		},
		description: null,
		form: function(){
			return new $.Form.FormLayout({items: [
				{
					name: 'subject',
					item: new $.Form.Text({
						validators: [$.Form.validator.NotEmpty]
					})
				},{
					name: 'content',
					description: "You may use the following identifiers:<br><b>%%</b> : prints a literal % character<br><b>%D</b> : prints date using the format 'Y-m-d H:i:s'<br><b>%R</b> : prints the resource's name that emits the signal<br><b>%I</b> : prints the resource's id that emits the signal<br><b>%d</b> : prints the data attached to the signal (JSON)<br><b>%r</b> : prints the rule's name<br><b>%s</b> : prints the signal's name<br>",
					item: new $.Form.Textarea({
						validators: [$.Form.validator.NotEmpty]
					})
				}, {
					name: 'attachments',
					description: 'Select files or tables to attach to this notification',
					item: ResourceSelection.form({
						'filter' : function(r){
							return r instanceof EThing.Table || r instanceof EThing.File;
						},
						all : false,
						selection : true,
						expression: true,
						emitter: false,
						resourcesName: 'files or tables'
					}),
					checkable: true
				}
			]});
		}
	},
	
	{
		type: 'ResourceClear',
		name: 'clear resource',
		toString: function(options){
			return "clear "+ResourceSelection.toString(options.resource);
		},
		description: null,
		form: function(){
			return new $.Form.FormLayout({
				items: [{
					name: 'resource',
					description: 'Select which resource must be cleared.',
					item: ResourceSelection.form({
						emitter: true,
						filter: function(r){
							return r instanceof EThing.Table || r instanceof EThing.File;
						}
					})
				}]
			});
		}
	},
	
	{
		type: 'ResourceRemove',
		name: 'remove resource',
		toString: function(options){
			return "remove "+ResourceSelection.toString(options.resource);
		},
		description: null,
		form: function(){
			return new $.Form.FormLayout({
				items: [{
					name: 'resource',
					description: 'Select which resource must be removed.',
					item: ResourceSelection.form({
						emitter: true
					})
				}]
			});
		}
	},
	
	{
		type: 'TableStatistics',
		name: 'make statistics',
		toString: function(options){
			return "make statistics of the data '"+options.field+"' in "+ ResourceSelection.toString(options.resource, 'table');
		},
		description: null,
		form: function(){
			return new $.Form.FormLayout({
				items: [{
					name: 'resource',
					item: new $.Form.ResourceSelect({
						name: 'resource',
						multiple: false,
						allowCreation: false,
						filter: function(r){
							return r instanceof EThing.Table;
						},
						validators: [$.Form.validator.NotEmpty] 
					})
				},{
					name: 'field',
					item: new $.Form.Select({
						name: 'field',
						items: [],
						validators: [$.Form.validator.NotEmpty] 
					})
				},{
					name: 'dataset',
					item: new $.Form.CustomInput({
						input: function(){
							var self = this;
							var $input = $(
							'<div class="TableStatistics-dataset">'+
								'<div class="radio">'+
								  '<label>'+
									'<input type="radio" name="dataset" value="ALL">'+
									'all data'+
								  '</label>'+
								'</div>'+
								'<div class="radio">'+
								  '<label>'+
									'<input type="radio" name="dataset" value="DATERANGE">'+
									'data newer than'+
									'<select class="form-control inline">'+
										'<option value="3600">1 hour</option>'+
										'<option value="7200">2 hours</option>'+
										'<option value="21600">6 hours</option>'+
										'<option value="43200">12 hours</option>'+
										'<option value="86400" selected>1 day</option>'+
										'<option value="172800">2 days</option>'+
										'<option value="604800">1 week</option>'+
										'<option value="12009600">2 weeks</option>'+
										'<option value="2678400">1 month</option>'+
										'<option value="5270400">2 months</option>'+
										'<option value="15811200">6 months</option>'+
										'<option value="31557600">1 year</option>'+
									'</select>'+
								  '</label>'+
								'</div>'+
								'<div class="radio">'+
								  '<label>'+
									'<input type="radio" name="dataset" value="ROW">'+
									'last <input class="form-control inline" type="number" value="100" min="0" style="width: 60px;"> row(s)'+
								  '</label>'+
								'</div>'+
							'</div>'
							);
							
							var $radios = this.$radios = $input.find('.radio input[name="dataset"]').change(function(){
								var $this = $(this), val = $this.val();
								$radios.not(this).closest('.radio').removeClass('selected').find('.inline').prop('disabled',true);
								$this.closest('.radio').addClass('selected').find('.inline').prop('disabled',false);
							});
							
							$input.change(function(){
								self.update();
							});
							
							$radios.filter('[value="ALL"]').prop('checked', true).change();
							
							return $input;
						},
						get: function($input){
							var $radio = this.$radios.filter(':checked'), mode = $radio.val();
							if(mode=='DATERANGE') {
								var v = $radio.closest('.radio').find('select').val();
								if(!v) throw 'no range selected';
								return parseInt(v);
							}
							if(mode=='ROW') {
								var v = $radio.closest('.radio').find('input[type="number"]').val();
								if(v<=0) throw 'the rows number must be greater than 0';
								return - parseInt(v);
							}
							return 0; // mode == 'ALL'
						},
						set: function($input, value){
							value = parseInt(value);
							var mode = 'ALL';
							if(value>0){
								mode = 'DATERANGE';
								this.$radios.filter('[value="DATERANGE"]').closest('.radio').find('select').val(value);
							}
							else if(value<0){
								mode = 'ROW';
								this.$radios.filter('[value="ROW"]').closest('.radio').find('input[type="number"]').val(-value);
							}
							if(mode)
								this.$radios.filter('[value="'+mode+'"]').prop('checked', true).change();
						},
						validators: [function(value){
							if(typeof value != 'number' || isNaN(value)) throw 'not a number';
						}],
						value: 0
					})
				},{
					label: 'destination table',
					name: 'destination',
					item: new $.Form.ResourceSelect({
						multiple: false,
						filter: function(r){
							return r instanceof EThing.Table;
						},
						allowCreation: ['Table'],
						validators: [$.Form.validator.NotEmpty]
					}),
					
				}],
				onload: function(){
					var fieldItem = this.findItem('field');
					this.findItem('resource').change(function(){
						var table = EThing.arbo.findOneById(this.value());
						fieldItem.setOptions( table ? table.keys() : [] );
					}).change();
				}
			});
		}
	},
	
	{
		type: 'EventTrigger',
		name: 'Trigger event', 
		toString: function(options){
			return "trigger the custom event '"+options.name+"'";
		},
		description: null,
		form: function(){
			return new $.Form.FormLayout({items: [
				{
					name: 'name',
					item: new $.Form.Text({
						validators: [$.Form.validator.NotEmpty],
						placeholder: "myCustomEvent"
					})
				}
			]});
		}
	},
	
	{
		type: 'HttpRequest',
		name: 'Send a HTTP request',
		toString: function(options){
			return "send a HTTP request to <mark>"+options.url+"</mark>";
		},
		description: null,
		form: function(){
			
			return new $.Form.FormLayout({
				items: [{
					name: 'request',
					label: false,
					item: new $.Form.HttpRequest()
				},
				{
					name: 'output',
					description: 'Save the result of this request in a file with the following filename :',
					item: new $.Form.Text({
						validators: [$.Form.validator.NotEmpty],
						value: 'output.txt'
					}),
					checkable: true
				}],
				format: {
					'out': function(value){
						return $.extend({}, value.request, { output: value.output });
					},
					'in': function(value){
						var o = {
							output: value.output
						};
						delete value.output;
						o.request = value;
						return o;
					}
				}
			});
		}
	},
	
	{
		type: 'DeviceRequest',
		name: 'Execute a device operation',
		toString: function(options){
			var str = "execute the operation <mark>"+options.operation+"</mark> on "+ResourceSelection.toString(options.device, 'device');
			if(options.output){
				str += " and store the response in a "+options.output.type;
			}
			return str;
		},
		description: null,
		form: function(){
			
			var f = new $.Form.FormLayout({
				items: [{
					name: 'request',
					label: false,
					item: new $.Form.DeviceRequest({
						onApiCall: function(device, operation, api){
							console.log(api.response);
							f.setVisible('output', !!api.response);
							// only json accepted for table output
							f.getLayoutItemByName('output').item.setEnable('table', /json/.test(api.response));
						},
						onchange: function(device, operation){
							if(f) f.setVisible('output', false);
						}
					})
				},{
					name: 'output',
					description: 'Save the result of this request in a file or a table.',
					item: new $.Form.SelectPanels({
						label: false,
						format: $.Form.SelectPanels.format.Merge,
						items: [{
							name: 'file',
							label: 'put the response in a file',
							item: new $.Form.FormLayout({
								items:[{
									name: 'name',
									description: "You may use the following identifiers:<br><b>%%</b> : prints a literal % character<br><b>%D</b> : prints date using the format 'Y-m-d H:i:s'<br><b>%R</b> : prints the resource's name that emits the signal<br><b>%I</b> : prints the resource's id that emits the signal<br><b>%c</b> : prints an incremental integer<br><b>%r</b> : prints the rule's name<br><b>%s</b> : prints the signal's name<br>",
									item: new $.Form.Text({
										validators: [$.Form.validator.NotEmpty]
									})
								},{
									name: 'expireAfter',
									label: 'expire after',
									description: 'The file will be automatically removed after the specified amount of time.',
									item: new $.Form.Duration({
										minute: false,
										hour: true,
										day: true,
										value: 86400
									}),
									checkable: true
								}]
							})
						},{
							name: 'table',
							label: 'append the response in a table <i style="font-size: smaller;">(only json)</i>',
							item: new $.Form.FormLayout({
								items:[{
									name: 'name',
									item: new $.Form.Text({
										validators: [$.Form.validator.NotEmpty]
									})
								}]
							})
						}]
					}),
					checkable: true,
					class: 'item-expert'
				}],
				format: {
					'out': function(value){
						return $.extend({}, value.request, { output: value.output });
					},
					'in': function(value){
						var o = {
							output: value.output
						};
						delete value.output;
						o.request = value;
						return o;
					}
				}
			});
			
			return f;
		}
	},
	
	{
		type: 'Log',
		name: 'log',
		toString: function(options){
			return "log the message <mark>"+options.message+"</mark>";
		},
		description: null,
		form: function(){
			
			return new $.Form.FormLayout({
				items: [{
					name: 'message',
					item: new $.Form.Text({
						validators: [$.Form.validator.NotEmpty]
					})
				}]
			});
		}
	},
	
	{
		type: 'Sleep',
		name: 'sleep for a specified number of seconds',
		toString: function(options){
			return "sleep for "+options.duration+" seconde(s)";
		},
		description: 'Sleep for a specified number of seconds. Insert this before an action to delay it.',
		form: function(){
			
			return new $.Form.FormLayout({
				items: [{
					name: 'duration',
					item: new $.Form.Number({
						minimum: 1,
						value: 10,
						validators: [$.Form.validator.Integer]
					})
				}]
			});
		}
	},
	
	{
		type: 'MqttPublish',
		name: 'MQTT publish',
		toString: function(options){
			return "publish to "+options.host+":"+options.port;
		},
		description: 'Publish a message to a MQTT broker.',
		form: function(){
			
			return new $.Form.FormLayout({
				items: [{
					name: 'host',
					item: new $.Form.Text({
						validators: [$.Form.validator.NotEmpty],
						placeholder: "hostname"
					})
				},{
					name: 'port',
					item: new $.Form.Number({
						validators: [$.Form.validator.Integer],
						placeholder: "port",
						value: 1883,
						minimum: 1,
						maximum: 65535,
					})
				},{
					name: "auth",
					label: 'authentication',
					checkable: true,
					item: new $.Form.FormLayout({
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
					})
				},{
					name: 'topic',
					item: new $.Form.Text({
						validators: [$.Form.validator.NotEmpty],
						placeholder: "topic"
					})
				},{
					name: 'payload',
					item: new $.Form.Textarea({
						validators: [$.Form.validator.NotEmpty],
						placeholder: "payload"
					})
				}],
				format:{
					'in': function(v){
						if(v.user && v.password){
							v.auth = {
								'user': v.user,
								'password': v.password
							};
							delete v.user;
							delete v.password;
						}
						return v;
					},
					'out': function(v){
						if(v.hasOwnProperty('auth')){
							if($.isPlainObject(v.auth)){
								v.user = v.auth.user;
								v.password = v.auth.password;
							}
							delete v['auth'];
						}
						return v;
					}
				}
			});
		}
	},
	
	{
		type: 'ScriptExecution',
		name: 'Execute a script',
		toString: function(options){
			var r = EThing.arbo.findOneById(options.script);
			if(r) {
				return "the script <mark>"+r.name()+"</mark> is executed";
			} else {
				return "the script with id '"+options.script+"' (does not exist anymore!) is executed";
			}
		},
		description: 'Execute a script.',
		form: function(){
			
			return new $.Form.FormLayout({
				items: [{
					name: 'script',
					description: 'Select which script must be executed.',
					item: new $.Form.ResourceSelect({
						multiple: false,
						allowCreation: false,
						filter: function(r){
							return r instanceof EThing.File && r.isScript();
						},
						validators: [$.Form.validator.NotEmpty] 
					})
				},{
					name: 'arguments',
					checkable: true,
					description: 'You may provide command line arguments.',
					item: new $.Form.Text({
						validators: [$.Form.validator.NotEmpty],
						placeholder: 'arguments'
					})
				}]
			});
		}
	}
	
	];
	
	
	['events', 'conditions', 'actions'].forEach(function(part){
		Rule[part].find = function(item){
			var f = undefined, type = typeof item == 'string' ? item : item.type;
			this.forEach(function(meta){
				if(type === meta.type){
					f = meta;
					return false;
				}
			});
			if(!f){
				f = {
					type: type
				};
			}
			if(!f.name) f.name = f.type;
			if(!f.toString) f.toString = function(){
				return this.name;
			};
			return f;
		};
	});
	
	
	var filterKey = function(obj, keysToKeep){
		obj = $.extend(true,{},obj);
		for(var i in obj){
			if(keysToKeep.indexOf(i)===-1)
				delete obj[i];
		}
		return obj;
	}
	
	
	var editRule = function(rule, callback){
		
		if(typeof rule == 'function'){
			callback = rule
			rule = undefined;
		}
		
		var $html = $(
		'<div class="rule-editor">'+
		
		'<div class="options">'+
		  
		'</div>'+
		
		'<div class="subpart subpart-primary event">'+
		  '<h4>Event</h4>'+
		  '<p>When to execute this rule ?</p>'+
		  '<p>'+
			'<p class="empty-notification">empty</p>'+
			'<table class="list"></table>'+
			'<button type="button" class="btn btn-default" data-role="add"><span class="glyphicon glyphicon-plus" aria-hidden="true"></span> Add a new event</button>'+
		   '</p>'+
		'</div>'+
		
		'<div class="subpart subpart-primary condition">'+
		  '<h4>Condition <small>(optional)</small></h4>'+
		  '<p>Is there any condition to execute this rule ?</p>'+
		  '<p>'+
			'<p class="empty-notification">empty</p>'+
			'<table class="list"></table>'+
			'<button type="button" class="btn btn-default" data-role="add"><span class="glyphicon glyphicon-plus" aria-hidden="true"></span> Add a new condition</button>'+
		   '</p>'+
		'</div>'+
		
		'<div class="subpart subpart-primary action">'+
		  '<h4>Action</h4>'+
		  '<p>Action to execute when the rule match ?</p>'+
		  '<p>'+
			'<p class="empty-notification">empty</p>'+
			'<table class="list"></table>'+
			'<button type="button" class="btn btn-default" data-role="add"><span class="glyphicon glyphicon-plus" aria-hidden="true"></span> Add a new action</button>'+
		   '</p>'+
		'</div>'+
		
		'<div class="alert alert-warning" role="alert"></div>'+
		'</div>'
		);
		
		function capitalizeFirstLetter(string) {
			return string.charAt(0).toUpperCase() + string.slice(1);
		}
		
		$html.find('.options').form(new $.Form.FormLayout({
			items: [{
				name: 'name',
				item: new $.Form.Text({
					validators: [$.Form.validator.NotEmpty],
					placeholder: "name of the rule",
					focus: true
				})
			},{
				name: 'priority',
				item: new $.Form.Number({
					validators: [$.Form.validator.Integer],
					placeholder: "priority",
					value: 0
				})
			},{
				name: 'repeat',
				description: 'If repeat is set to false, the actions of this rule will be executed only the first time the conditions match.',
				item: new $.Form.Checkbox({
					label: 'repeat',
					value: true
				})
			}]}), rule ? {
				'name': rule.name(),
				'priority': rule.priority(),
				'repeat': rule.repeat()
			} : undefined);
		
		// items : events, conditions, actions
		var editItem = function(type, item, callback){
			
			if(typeof item == 'function'){
				callback = item
				item = undefined;
			}
			
			var formItems = [];
			Rule[type+'s'].forEach(function(meta){
				
				formItems.push({
					category: capitalizeFirstLetter(meta.category || ''),
					name: meta.type,
					label: meta.name,
					description: meta.description ? '<div style="color: grey;">'+meta.description+'</div>' : null,
					item: typeof meta.form == 'function' ? (meta.form(meta) || null) : null
				});
			});
			
			var $advbtn;
			
			$.FormModal({
				item: new $.Form.SelectPanels({
					items: formItems,
					format: {
						'out': function(value){
							value.options = value.value;
							delete value.value;
							return value;
						},
						'in': function(value){
							value.value = value.options;
							delete value.options;
							return value;
						}
					}
				}),
				value: item,
				title: item ? 'Rule: '+type+'\'s editing' : 'Rule: add a new '+type,
				validLabel: item ? '+Apply' : '+Add'
			},callback);
			
		};
		
		var updateItemBtns = function($parent){
			var $items = $parent.children('.item');
			
			if($items.length<2){
				$items.find('.toolbar button[data-role="up"], .toolbar button[data-role="down"]').hide();
			} else {
				$items.find('.toolbar button[data-role="up"], .toolbar button[data-role="down"]').removeAttr('disabled').show();
				$items.first().find('.toolbar button[data-role="up"]').attr('disabled','disabled');
				$items.last().find('.toolbar button[data-role="down"]').attr('disabled','disabled');
			}
		}
		
		var addItem = function(type, item, $updateItem){
			
			if(!item || $.isEmptyObject(item)) return;
			
			var meta = Rule[type+'s'].find(item);
			if(!meta) return;
			
			var $item = $(
				'<tr class="item '+type+'">'+
					'<td>'+
						'<div class="description"></div>'+
						'<div class="error"></div>'+
					'</td>'+
					'<td>'+
						'<div class="toolbar btn-group btn-group-sm">'+
							'<button type="button" class="btn btn-default" data-role="edit"><span class="glyphicon glyphicon-cog" aria-hidden="true"></span></button>'+
							'<button type="button" class="btn btn-default" data-role="up"><span class="glyphicon glyphicon-arrow-up" aria-hidden="true"></span></button>'+
							'<button type="button" class="btn btn-default" data-role="down"><span class="glyphicon glyphicon-arrow-down" aria-hidden="true"></span></button>'+
							'<button type="button" class="btn btn-default" data-role="remove"><span class="glyphicon glyphicon-trash" aria-hidden="true"></span></button>'+
						'</div>'+
					'</td>'+
				'</tr>'
			);
			
			$item.data('data',item);
			
			var error = item.error;
			var isInvalid = item.isInvalid || false;
			
			if(isInvalid && !error) error = 'invalid '+type;
			
			$item.toggleClass('invalid', !!isInvalid);
			$item.toggleClass('hasError', !!error);
			$item.find('.error').html(error || '').toggle(!!error);
			
			$item.find('.description').html(meta.toString(item.options));
			
			$item.find('.toolbar button[data-role="edit"]').click(function(){
				editItem(type, item, function(props){
					addItem(type, props, $item);
				});
			});
			$item.find('.toolbar button[data-role="remove"]').click(function(){
				var $p = $item.parent();
				$item.remove();
				$html.find('.subpart.'+type+' .empty-notification').toggle($list.children('.item').length>0);
				updateItemBtns($p);
			});
			$item.find('.toolbar button[data-role="up"]').click(function(){
				var $prev = $item.prev();
				if($prev.length){
					$item.insertBefore($prev);
					updateItemBtns($item.parent());
				}
			});
			$item.find('.toolbar button[data-role="down"]').click(function(){
				var $next = $item.next();
				if($next.length){
					$item.insertAfter($next);
					updateItemBtns($item.parent());
				}
			});
			
			if($updateItem){
				$updateItem.replaceWith($item);
			} else {
				var $list = $html.find('.subpart.'+type+' .list');
				
				$list.append($item);
				
				$html.find('.subpart.'+type+' .empty-notification').toggle($list.children('.item').length>0);
			}
			updateItemBtns($item.parent());
		};
		
		
		
		// events
		$html.find('.subpart.event button[data-role="add"]').click(function(){
			editItem('event', function(props){
				addItem('event',props);
			});
		});
		if(rule){
			rule.events().forEach(function(event){
				addItem('event',event);
			});
		}
		
		// conditions
		$html.find('.subpart.condition button[data-role="add"]').click(function(){
			editItem('condition', function(props){
				addItem('condition',props);
			});
		});
		if(rule){
			rule.conditions().forEach(function(condition){
				addItem('condition',condition);
			});
		}
		
		// actions
		$html.find('.subpart.action button[data-role="add"]').click(function(){
			editItem('action', function(props){
				addItem('action',props);
			});
		});
		if(rule){
			rule.actions().forEach(function(action){
				addItem('action',action);
			});
		}
		
		
		// error
		var $error = $html.children('.alert').hide();
		
		
		
		$html.modal({
			title: 'Rule',
			buttons:{
				'+Apply' : function(){
					
					$error.hide();
					
					var rule = {};
					
					$html.find('.options').form('submit', function(options){
						
						$.extend(rule, options);
						
						// grab the conditions
						rule.events = [];
						$html.find('.item.event').each(function(){
							rule.events.push( filterKey($(this).data('data'), ['type','options']) );
						});
						
						// grab the conditions
						rule.conditions = [];
						$html.find('.item.condition').each(function(){
							rule.conditions.push( filterKey($(this).data('data'), ['type','options']) );
						});
						
						// grab the actions
						rule.actions = [];
						$html.find('.item.action').each(function(){
							rule.actions.push( filterKey($(this).data('data'), ['type','options']) );
						});
						
						if(typeof callback == 'function'){
							
							
							$.when( callback(rule) ).done(function(){
								// ok
								$html.modal('hide');
							})
							.fail(function(err){
								console.error(err);
								$error.text( err.message || err || 'unknown error' ).show();
							});
						}
						else
							$html.modal('hide');
					});
					
					return false;
					
				},
				'Cancel': null
			}
		});
		
	}
	
	
	
	
	/*
	Cron form
	*/
	
	// form builder
	$.Form.Cron = function(options){
		options =options || {};
		
		
		$.Form.Wrapper.call(this, {
			item : new $.Form.FormLayout({
				items: [
				{
					label: false,
					name: 'expression',
					item: new $.Form.Text({
						prefix: 'cron',
						validators: [$.Form.validator.NotEmpty, function(v){
							if(typeof v != 'string' || v.split(/\s+/).length != 5)
								throw 'not a valid cron expression !';
						}],
						placeholder: 'Cron expression : min hour day month weekday',
						comboboxValues: {
							'<span style="color:grey;">ex:</span> at 11 AM daily': '0 11 * * *',
							'<span style="color:grey;">ex:</span> every minutes' : '* * * * *',
							'<span style="color:grey;">ex:</span> twice a day' : '0 5,17 * * *',
							'<span style="color:grey;">ex:</span> every Sunday at 5 PM' : '0 17 * * sun',
							'<span style="color:grey;">ex:</span> every 10 minutes' : '*/10 * * * *'
						}
					})
				},{
					name: 'info',
					label: false,
					item: new $.Form.Label(),
					dependencies: {
						'expression': function(layoutItem, dependentLayoutItem){
							var cronvalue = dependentLayoutItem.item.value();
							var crontstr = null;
							try {
								if(cronvalue) crontstr = cronstrue.toString(cronvalue);
							} catch(e){}
							layoutItem.item.value(crontstr||'');
							return  true;
						}
					}
				}],
				format: {
					'in': function(value){
						return {
							expression: value.cron
						};
					},
					'out': function(value){
						return {
							cron: value.expression
						};
					}
				}
			}),
			value: options.value
		});
		
	};
	$.Form.Cron.prototype = Object.create($.Form.Wrapper.prototype);
	
	$.Form.Cron.prototype.createView = function(){
		return $.Form.Wrapper.prototype.createView.call(this).addClass('f-cron');
	}
	
	
	
	
	var RuleModel = function(options){

		this._options = $.extend(true,{
			filter: null // function(rule) -> return boolean , if it returns false, the rule is ignored
		},options);
		
		$.Table.Model.call(this,this._options);
		
		this._sort = null; // by default, no sort is made
		this._filter = this._options.filter;
	}
	RuleModel.prototype = Object.create($.Table.Model.prototype);

	RuleModel.prototype.init = function(tableInstance){}

	// return the keys/columns
	RuleModel.prototype.keys = function(){
		return ['event','conditions','actions'];
	}
	// return the items, may be a deferred object
	// offset and length are used for pagination
	RuleModel.prototype.data = function(parent, offset, length){
		// parent is null if root
		var deferred = $.Deferred(),
			self = this;
		
		EThing.listRules().done(function(rules){
			
			if(self._filter)
				rules = $.grep(rules,self._filter)
			
			if(self._sort)
				rules.sort(self._sort);
			
			// find the extrem priority
			var minPriority = null, maxPriority = null;
			rules.forEach(function(r){
				if(minPriority===null || r.priority() < minPriority)
					minPriority = r.priority();
				if(maxPriority===null || r.priority() > maxPriority)
					maxPriority = r.priority();
			});
			self.minPriority = minPriority;
			self.maxPriority = maxPriority;
			
			// pagination
			if(typeof offset == 'number')
				rules = rules.slice(offset,length ? (offset+length) : undefined);
			
			deferred.resolve(rules);
			
		}).fail(function(){
			deferred.reject();
		});
		
		return deferred.promise();
	}
	// return a unique index identifying an items according to the data given in argument
	RuleModel.prototype.index = function(rule){
		return (rule instanceof EThing.Rule) ? rule.id() : rule;
	}
	RuleModel.prototype.filter = function(filter){
		if(typeof filter == 'undefined')
			return this._filter;
		else
			this._filter = filter;
	}
	RuleModel.prototype.sort = function(field, ascending){
		
		if(field=="executedDate"){ // date
			this._sort = function(a,b){
				a = a[field]();
				b = b[field]();
				return (
					isFinite(a) && isFinite(b) ?
					((ascending ? 1 : -1) * ((a>b)-(a<b))):
					NaN
				);
			};
			return;
		}
		
		this._sort = function(a,b){
			a = a[field]();
			b = b[field]();
			return (ascending ? 1 : -1) * (typeof a == 'number' ? a-b : a.localeCompare(b));
		};
	}


	var RuleView = function(opt) {
		
		opt = $.extend(true,{
			fields: {
				'state': {
					label: "",
					get: function(rule,index,$tr){
						
						// determine the state of this rule : valid, error or warning
						var state = 'valid';
						
						if(rule.isInvalid()){
							state = 'error';
						} else {
							[].concat(rule.events(), rule.actions(), rule.conditions()).forEach(function(item){
								if(item.isInvalid || item.error){
									state = 'warning';
								}
							});
						}
						
						$tr.addClass('rule-'+state);
						$tr.data('state', state);
						
						
						// make it clickable
						$tr.click(function(){
							
							var $next = $tr.next();
							if($next.is('.details')){
								$next.find('td > div').slideUp(200, function(){
									$next.remove();
								});
								return;
							}
							
							// show more details
							
							var $extraTr = $('<tr class="details"><td colspan="6"><div></div></td></tr>').hide(),
								$cntr = $extraTr.find('div').hide();
							
							function makeItem(type,attr){
								var $item = $(
										'<div class="item">'+
											'<div class="description"></div>'+
											'<div class="error"></div>'+
										'</div>'
									),
									meta = Rule[type+'s'].find(attr);
								
								$item.addClass(type);
								
								var error = attr.error;
								var isInvalid = attr.isInvalid || false;
								
								if(isInvalid && !error) error = 'invalid '+type;
								
								$item.toggleClass('invalid', !!isInvalid);
								$item.toggleClass('hasError', !!error);
								$item.find('.error').html(error || '').toggle(!!error);
								
								$item.find('.description').html(meta.toString(attr.options));
								
								$cntr.append($item);
							}
							
							if(rule.events().length){
								$cntr.append('<h4>events</h4>');
								rule.events().forEach(function(event){
									makeItem('event',event);
								});
							}
							if(rule.conditions().length){
								$cntr.append('<h4>conditions</h4>');
								rule.conditions().forEach(function(condition){
									makeItem('condition',condition);
								});
							}
							if(rule.actions().length){
								$cntr.append('<h4>actions</h4>');
								rule.actions().forEach(function(action){
									makeItem('action',action);
								});
							}
							$cntr.append('<h4>details</h4>');
							$cntr.append(
								'<div class="rule-details">'+
								  '<strong>name</strong> : '+rule.name()+'<br>'+
								  '<strong>repeat</strong> : '+rule.repeat().toString()+'<br>'+
								  '<strong>priority</strong> : '+rule.priority()+'<br>'+
								  '<strong>invalid</strong> : '+rule.isInvalid().toString()+'<br>'+
								  '<strong>created date</strong> : '+UI.dateToString(rule.createdDate())+'<br>'+
								  '<strong>last executed date</strong> : '+(rule.executedDate() ? UI.dateToString(rule.executedDate()) : 'never')+'<br>'+
								  '<strong>executed count</strong> : '+rule.executedCount()+'<br>'+
								'</div>'
							);
							
							$extraTr.insertAfter($tr).show();
							$cntr.slideDown(400);
						});
						
						return state == 'valid' ? '' : '<span class="glyphicon glyphicon-alert" aria-hidden="true"></span>';
					},
					class: "col-state",
					sortable: false
				},
				'enabled': {
					get: function(r){
						
						var $switch = $('<div class="checkbox checkbox-slider--b-flat"><label><input type="checkbox"><span></span></label></div>');
						$switch.click(function(e){
							e.stopPropagation();
						}).find('input').prop('checked', r.enabled()).change(function(){
							var checked = $(this).prop('checked');
							r.set({
								enabled: checked
							});
						});
						return $switch;
					},
					class: "col-enabled",
					sortable: false
				},
				'name': {
					get: function(r){
						return r.name() || '<small>unnamed</small>';
					},
					class: "col-name",
					sortable: true
				},
				'priority': {
					get: function(r){
						var priorityColor = priorityToColor(r.priority(), this.table().model().minPriority, this.table().model().maxPriority);
						return '<span class="badge" style="background-color: '+priorityColor+';">'+r.priority()+'<span>';
					},
					class: "col-priority",
					sortable: true
				},
				'executedDate': {
					label: 'executed',
					get: function(rule){
						return rule.executedDate() ? UI.dateToString(rule.executedDate()) : '<small>never</small>';
					},
					class: "col-executed",
					sortable: true
				},
				'toolbar': {
					label: "",
					get: function(r, index, $tr){
						
						var $tb = $(
							'<div class="btn-group">'+
								'<button type="button" class="btn btn-default" data-role="run"><span class="glyphicon glyphicon-play" aria-hidden="true"></span></button>'+
								'<button type="button" class="btn btn-default" data-role="edit"><span class="glyphicon glyphicon-cog" aria-hidden="true"></span></button>'+
								'<button type="button" class="btn btn-default" data-role="remove"><span class="glyphicon glyphicon-trash" aria-hidden="true"></span></button>'+
							'</div>'
						);
						
						var customSignal = null;
						r.events().forEach(function(event){
							if(event.type === 'Custom' && !event.options.resource ){
								customSignal = event.options.name;
								return false;
							}
						});
						
						$tb.find('[data-role="run"]').prop('disabled', !customSignal).click(function(evt){
							evt.stopPropagation();
							EThing.Rule.trigger(customSignal);
						});
						
						
						$tb.find('[data-role="edit"]').click(function(evt){
							editRule(r, function(rule){
								return r.set(rule).done(function(){
									$('.rule-table').table('reload');
								});
							});
							evt.stopPropagation();
						});
						
						$tb.find('[data-role="remove"]').click(function(evt){
							if(confirm('Do you really want to remove this rule ?')){
								r.remove(function(){
									$('.rule-table').table('reload');
								});
							}
							evt.stopPropagation();
						});
						
						return $tb;
					},
					class: "col-tb",
					sortable: false
				}/*,
				'pc': {
					label: "",
					get: function(r){
						return $('<div>').css({
							//backgroundColor: priorityToColor(r.priority(), this.table().model().minPriority, this.table().model().maxPriority),
							'border-right': '5px solid '+priorityToColor(r.priority(), this.table().model().minPriority, this.table().model().maxPriority)
						});
					},
					class: "col-pc",
					sortable: false
				}*/
			},
			showOnlySpecifiedField: true,
			class: 'table'
		},opt);
		
		$.Table.TableView.call(this,opt);
	}
	RuleView.prototype = Object.create($.Table.TableView.prototype);
	
	
	return function(){
		
		var $template = UI.Container.set(template);
		
		$template.find('#rule-add-btn').click(function(){
					
			editRule(function(rule){
				return EThing.Rule.create(rule).done(function(){
					$('.rule-table').table('reload');
				});
			});
			
			
		});
		
		$template.find('#rule-emit-btn').click(function(){
			
			var signal = $('#rule-emit-input').val().trim();
			
			if(signal.length){
				var $self = $(this).prepend('<span class="glyphicon glyphicon-refresh glyphicon-animate"></span> ');
				EThing.Rule.trigger(signal, function(){
					$self.find('.glyphicon-refresh').remove();
				});
			}
			
		});
	
		
		$template.find('.rule-table').table({
			
			model: new RuleModel(),
			view: new RuleView(),
			row: {
				class: 'item'
			},
			openable:{
				enable: false
			}
			
		});
		
	};
}));