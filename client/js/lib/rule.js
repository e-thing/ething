(function(){
	
	
	var events = [
		
		{
			name: 'TableDataAdded', // an unique name, must correspond to the event name
			label: "after data is added in this table", // name displayed to the user
			description: null, // an optional description
			compatible: function(rule){ // compatibility check {function(Rule)->bool}
				return (rule.parent instanceof EThing.Table);
			},
			editable: false, // editable or not ? if yes, must be a function returning a Form {null|function()->Form}
			callback: null, // to be executed once this event is selected function(Rule)->{Deferred|false}. If it returns false, the selection is cancelled.
			defaultRepeatValue: true
		},
		{
			name: 'FileDataModified',
			label: "after the content of this file is modified",
			description: null,
			compatible: function(rule){
				return (rule.parent instanceof EThing.File);
			},
			defaultRepeatValue: true
		},
		{
			name: 'LowBatteryDevice', 
			label: "if the battery level of this device is under 10%", 
			description: null, 
			compatible: function(rule){
				return (rule.parent instanceof EThing.Device);
			},
			defaultRepeatValue: false
		},
		{
			name: 'TickTimer',
			label: "at a specific moment",
			description: null,
			callback: function(rule){
				var event = this,
					condition = new Condition(find('Cron',conditions),event.parent);
				
				return $.Deferred(function(deferred){
					edit(condition,function(){
						rule.addCondition(condition);
						deferred.resolve();
					});
				}).promise();
			},
			defaultRepeatValue: true
		},
		{
			name: 'DeviceUnreachable', 
			label: "when this device is unreachable", 
			description: null, 
			compatible: function(rule){
				return (rule.parent instanceof EThing.Device);
			},
			defaultRepeatValue: false
		}
		
	];
	
	
	var conditions = [
		{
			name: 'Cron',
			label: function(options){
				if(!options || !options.cron)
					return "where the current time matches a cron expression";
				return "where the current time matches the cron expression '"+options.cron+"'";
			},
			description: null,
			editable: function(){
				return new $.Form.FormLayout([
					{
						name: 'minute',
						item: {
							input: {
								'every minute': "*",
								'every 5 minutes': "*/5",
								'every 15 minutes': "*/15",
								'every 30 minutes': "30",
							}
						}
					},{
						name: 'hour',
						item: {
							input: function(){
								var $input = $('<select>');
								$input.append('<option value="*">every hour</option>');
								$input.append('<option value="*/2">every 2 hours</option>');
								$input.append('<option value="*/4">every 4 hours</option>');
								$input.append('<option value="*/6">every 6 hours</option>');
								$input.append('<option value="0">0 = 12AM (midnight)</option>');
								for(var i=1;i<12;i++)
									$input.append('<option value="'+i+'">'+i+' = '+i+'AM</option>');
								$input.append('<option value="12">12 = 12PM (noon)</option>');
								for(var i=1;i<12;i++)
									$input.append('<option value="'+(i+12)+'">'+(i+12)+' = '+i+'PM</option>');
								return $input;
							}
						}
					},{
						name: 'day',
						item: {
							input: function(){
								var $input = $('<select>');
								$input.append('<option value="*">every day</option>');
								for(var i=1;i<=31;i++)
									$input.append('<option value="'+i+'">'+i+'</option>');
								return $input;
							}
						}
					},{
						name: 'month',
						item: {
							input: function(){
								var $input = $('<select>');
								$input.append('<option value="*">every month</option>');
								var months = ["January","February","March","April","May","June","July","August","September","October","November","December"];
								for(var i=0; i<months.length; i++)
									$input.append('<option value="'+(i+1)+'">'+months[i]+'</option>');
								return $input;
							}
						}
					},{
						name: 'year',
						item: {
							input: function(){
								var $input = $('<select>');
								$input.append('<option value="*">every year</option>');
								var currentYear = new Date().getFullYear();
								for(var i=0;i<10;i++)
									$input.append('<option value="'+(currentYear+i)+'">'+(currentYear+i)+'</option>');
								return $input;
							}
						}
					},{
						name: 'weekday',
						item: {
							input: function(){
								var $input = $('<select>');
								$input.append('<option value="*">every weekday</option>');
								var weekday = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"];
								for(var i=0; i<weekday.length; i++)
									$input.append('<option value="'+i+'">'+weekday[i]+'</option>');
								return $input;
							}
						}
					}
				]);
			},
			validateForm: function(json){
				var o = $.extend({
					minute: '*',
					hour: '*',
					day: '*',
					month: '*',
					year: '*',
					weekday: '*'
				},json);
				return {
					cron: o.minute+" "+o.hour+" "+o.day+" "+o.month+" "+o.year+" "+o.weekday
				};
			}
		},
		{
			name: 'TableValueThreshold',
			label: function(options){
				if(!options)
					return "where the value of a specific field is compared to a threshold";
				
				var opStr = '?';
				switch(options.operator){
					case '>':
						opStr = 'greater than';
						break;
					case '<':
						opStr = 'less than';
						break;
					case '>=':
						opStr = 'greater or equal';
						break;
					case '<=':
						opStr = 'less or equal';
						break;
					case '==':
						opStr = 'equal';
						break;
					case '!=':
						opStr = 'not equal';
						break;
				}
				return 'where the value of the field "'+options.field+'" is '+opStr+' '+options.threshold;
			},
			compatible: function(rule){
				return rule.event.name==='TableDataAdded';
			},
			editable: function(){
				var parent = this.parent;
				return new $.Form.FormLayout([
					{
						name: 'field',
						item:{
							input: function(){
								var $input = $('<select>');
								parent.keys().forEach(function(key,index){
									$input.append('<option>'+key+'</option>');
								});
								return $input;
							}
						}
					},
					{
						name: 'operator',
						item:{
							input: function(){
								var $input = $('<select>');
								$input.append('<option>&gt;</option>');
								$input.append('<option>&lt;</option>');
								$input.append('<option>&gt;=</option>');
								$input.append('<option>&lt;=</option>');
								$input.append('<option>==</option>');
								$input.append('<option>!=</option>');
								return $input;
							}
						}
					},
					{
						name: 'threshold',
						item:{
							input: 'number',
							value: 0
						}
					}
				]);
			}
		},
		{
			name: 'TableLength',
			label: function(options){
				if(!options)
					return "where the number of rows is compared to a threshold";
				
				var opStr = '?';
				switch(options.operator){
					case '>':
						opStr = 'greater than';
						break;
					case '<':
						opStr = 'less than';
						break;
					case '>=':
						opStr = 'greater or equal';
						break;
					case '<=':
						opStr = 'less or equal';
						break;
					case '==':
						opStr = 'equal';
						break;
					case '!=':
						opStr = 'not equal';
						break;
				}
				return 'where the number of rows is '+opStr+' '+options.threshold;
			},
			compatible: function(rule){
				return (rule.parent instanceof EThing.Table);
			},
			editable: function(){
				return new $.Form.FormLayout([
					{
						name: 'operator',
						item:{
							input: function(){
								var $input = $('<select>');
								$input.append('<option>&gt;</option>');
								$input.append('<option>&lt;</option>');
								$input.append('<option>&gt;=</option>');
								$input.append('<option>&lt;=</option>');
								$input.append('<option>==</option>');
								$input.append('<option>!=</option>');
								return $input;
							}
						}
					},{
						name: 'threshold',
						item:{
							input: 'number',
							value: 1000,
							attr:{
								min: 0
							}
						}
					}
				]);
			}
		},
		{
			name: 'FileLineNumber',
			label: function(options){
				if(!options)
					return "where the number of lines is compared to a threshold";
				
				var opStr = '?';
				switch(options.operator){
					case '>':
						opStr = 'greater than';
						break;
					case '<':
						opStr = 'less than';
						break;
					case '>=':
						opStr = 'greater or equal';
						break;
					case '<=':
						opStr = 'less or equal';
						break;
					case '==':
						opStr = 'equal';
						break;
					case '!=':
						opStr = 'not equal';
						break;
				}
				return 'where the number of lines is '+opStr+' '+options.threshold;
			},
			compatible: function(rule){
				return (rule.parent instanceof EThing.File);
			},
			editable: function(){
				return new $.Form.FormLayout([
					{
						name: 'operator',
						item:{
							input: function(){
								var $input = $('<select>');
								$input.append('<option>&gt;</option>');
								$input.append('<option>&lt;</option>');
								$input.append('<option>&gt;=</option>');
								$input.append('<option>&lt;=</option>');
								$input.append('<option>==</option>');
								$input.append('<option>!=</option>');
								return $input;
							}
						}
					},{
						name: 'threshold',
						item:{
							input: 'number',
							value: 100,
							attr:{
								min: 0
							}
						}
					}
				]);
			}
		},
		{
			name: 'FileSize',
			label: function(options){
				if(!options)
					return "where the size of this file is compared to a threshold";
				
				var opStr = '?';
				switch(options.operator){
					case '>':
						opStr = 'greater than';
						break;
					case '<':
						opStr = 'less than';
						break;
					case '>=':
						opStr = 'greater or equal';
						break;
					case '<=':
						opStr = 'less or equal';
						break;
					case '==':
						opStr = 'equal';
						break;
					case '!=':
						opStr = 'not equal';
						break;
				}
				return 'where the size of this file is '+opStr+' '+options.threshold;
			},
			compatible: function(rule){
				return (rule.parent instanceof EThing.File);
			},
			editable: function(){
				return new $.Form.FormLayout([
					{
						name: 'operator',
						item:{
							input: function(){
								var $input = $('<select>');
								$input.append('<option>&gt;</option>');
								$input.append('<option>&lt;</option>');
								$input.append('<option>&gt;=</option>');
								$input.append('<option>&lt;=</option>');
								$input.append('<option>==</option>');
								$input.append('<option>!=</option>');
								return $input;
							}
						}
					},{
						name: 'threshold',
						item:{
							input: 'number',
							value: 1000,
							attr:{
								min: 0
							}
						}
					}
				]);
			}
		},
		{
			name: 'DeviceInactive',
			label: function(options){
				return "where the device is inactive for more than "+(options ? (options.duration+" seconds") : "a certain amount of time");
			},
			compatible: function(rule){
				return (rule.parent instanceof EThing.Device);
			},
			editable: function(){
				return new $.Form.FormLayout([
					{
						name: 'duration',
						item:{
							input: {
								'15 minutes': 300,
								'30 minutes': 600,
								'1 hour' : 3600,
								'2 hours' : 7200,
								'6 hours' : 21600,
								'12 hours' : 43200,
								'1 day' : 86400,
								'2 days' : 172800,
								'1 week' : 604800
							},
							value: 3600
						}
					}
				]);
			}
		},
		{
			name: 'DeviceBatteryLevel',
			label: function(options){
				if(!options)
					return "where the battery level of this device is compared to a threshold";
				
				var opStr = '?';
				switch(options.operator){
					case '>':
						opStr = 'greater than';
						break;
					case '<':
						opStr = 'less than';
						break;
					case '>=':
						opStr = 'greater or equal';
						break;
					case '<=':
						opStr = 'less or equal';
						break;
					case '==':
						opStr = 'equal';
						break;
					case '!=':
						opStr = 'not equal';
						break;
				}
				return 'where the battery level of this device is '+opStr+' '+options.threshold;
			},
			compatible: function(rule){
				return (rule.parent instanceof EThing.Device);
			},
			editable: function(){
				return new $.Form.FormLayout([
					{
						name: 'operator',
						item:{
							input: function(){
								var $input = $('<select>');
								$input.append('<option>&gt;</option>');
								$input.append('<option>&lt;</option>');
								$input.append('<option>&gt;=</option>');
								$input.append('<option>&lt;=</option>');
								$input.append('<option>==</option>');
								$input.append('<option>!=</option>');
								return $input;
							}
						}
					},{
						name: 'threshold',
						item:{
							input: 'number',
							value: 10,
							attr:{
								min: 0,
								max: 100
							}
						}
					}
				]);
			}
		}
		
	];
	
	
	var actions = [
		
		{
			name: 'Notify',
			label: function(options){
				var mess = "send a notification";
				if(options){
					if(options.subject)
						mess += ' with subject "'+options.subject+'"';
					if(options.content)
						mess += ' and custom content';
				}
				return mess;
			},
			editable: function(){
				return new $.Form.FormLayout([
					{
						name: 'subject',
						item: 'text',
						checkable: true,
						check: false
					},{
						name: 'content',
						item: 'textarea',
						checkable: true,
						check: false
					}
				]);
			}
		},
		{
			name: 'ResourceClear',
			label: "clear the resource",
			compatible: function(rule){
				return (rule.parent instanceof EThing.Table) || (rule.parent instanceof EThing.File);
			},
			editable: false
		},
		{
			name: 'ResourceRemove',
			label: "remove the resource",
			editable: false
		}
		
	];
	
	
	
	var find = function(name,coll){
		if(typeof coll == 'undefined')
			coll = [].concat(rules,conditions,actions);
		for(var i=0; i<coll.length; i++)
			if(coll[i].name === name)
				return coll[i];
	}
	
	
	var counter = 0;
	
	function construct(self, props, parent){
		self.parent = parent;
		self.props = $.extend(true,{
			name: 'unknown',
			label: 'unknown',
			editable: false,
			compatible: true
		},props);
		self.options = null;
		
		for(var i in props)
			self[i] = props[i];
		
		self.label = function(){
			return (typeof self.props.label == 'function') ? self.props.label.call(self,(self.options && !$.isEmptyObject(self.options)) ? self.options : null) : self.props.label;
		}
		
		self.isEditable = function(){
			return !!props.editable;
		}
		
		self.setOptions = function(options){
			self.options = $.extend(true,{},options);
		}
		
		self.validate = function(){
			return $.extend(true,{
				type: self.name
			}, self.options);
		}
	}
	
	
	function Event(props,parent){
		construct(this,props,parent);
	}
	
	Event.fromJSON = function(json,parent){
		var json_;
		if(typeof json == 'string')
			json_ = {
				type : json
			};
		else
			json_ = $.extend(true,{},json); // make a deep copy
		var typeName = json_.type;
		delete json_.type;
		var props = find(typeName,events);
		var instance = new Event(props,parent);
		instance.setOptions(json_);
		return instance;
	}
	
	function Condition(props,parent){
		construct(this,props,parent);
		
		this._id = this.name + '#' + (++counter);
	}
	
	Condition.fromJSON = function(json,parent){
		var json_;
		if(typeof json == 'string')
			json_ = {
				type : json
			};
		else
			json_ = $.extend(true,{},json); // make a deep copy
		var typeName = json_.type;
		delete json_.type;
		var props = find(typeName,conditions);
		var instance = new Condition(props,parent);
		instance.setOptions(json_);
		return instance;
	}
	
	Condition.prototype.id = function(){
		return this._id;
	}
	
	function Action(props,parent){
		construct(this,props,parent);
	}
	
	Action.fromJSON = function(json,parent){
		var json_;
		if(typeof json == 'string')
			json_ = {
				type : json
			};
		else
			json_ = $.extend(true,{},json); // make a deep copy
		var typeName = json_.type;
		delete json_.type;
		var props = find(typeName,actions);
		var instance = new Action(props,parent);
		instance.setOptions(json_);
		return instance;
	}
	
	function Rule(parent){
		this.parent = parent;
		this.event = null;
		this.conditions = [];
		this.actions = [];
		this.repeat = false;
	}
	/*
		{
			"event":"table.valueAdded",
			"conditions":[{
				"type":"table.valueThreshold",
				"field":"pressure",
				"operator":"over",
				"threshold":"45"
			}],
			"actions":[{
				"type":"notify"
			}]
		}';
	*/
	Rule.fromJSON = function(json, parent){
		
		var rule = new Rule(parent);
		
		rule.event = Event.fromJSON(json.event,parent);
		
		json.conditions.forEach(function(condition){
			rule.addCondition(Condition.fromJSON(condition,parent));
		});
		
		json.actions.map(function(action){
			rule.addAction(Action.fromJSON(action,parent));
		});
		
		if(json.hasOwnProperty('repeat'))
			rule.repeat = !!json.repeat;
		
		return rule;
	}
	Rule.prototype.isValid = function(){
		return this.event && this.actions.length;
	}
	Rule.prototype.description = function(multiline){
		var str = 'Apply this rule ';
		str += this.event.label();
		str += multiline ? '<br>' : ' ';
		if(this.conditions.length){
			str += this.conditions.map(function(c){
				return c.label();
			}).join((multiline ? '<br>' : ' ')+'and ');
			str += multiline ? '<br>' : ' ';
		}
		str += this.actions.map(function(c){
			return c.label();
		}).join((multiline ? '<br>' : ' ')+'and ');
		return str;
	}
	Rule.prototype.addCondition = function(condition){
		if((condition instanceof Condition) && this.conditions.indexOf(condition) === -1)
			this.conditions.push(condition);
	}
	Rule.prototype.removeCondition = function(condition){
		var index = this.conditions.indexOf(condition);
		if(index !== -1)
			this.conditions.splice(index, 1);
	}
	Rule.prototype.addAction = function(action){
		if((action instanceof Action) && this.actions.indexOf(action) === -1)
			this.actions.push(action);
	}
	Rule.prototype.removeAction = function(action){
		var index = this.actions.indexOf(action);
		if(index !== -1)
			this.actions.splice(index, 1);
	}
	Rule.prototype.toJSON = function(){
		var json = {
			event:this.event.name,
			conditions:[],
			actions:[],
			repeat: !!this.repeat
		};
		
		this.conditions.forEach(function(condition){
			json.conditions.push(condition.validate());
		});
		this.actions.forEach(function(action){
			json.actions.push(action.validate());
		});
		
		return json;
	}
	
	
	var listCompatible = function(collection, rule){
		return collection.filter(function(el){
			return (typeof el.compatible == 'undefined') || ((typeof el.compatible == 'function') ? el.compatible.call(el,rule) : el.compatible);
		});
	}
	
	var edit = function(what,callback){
		
		var classname = what.constructor.name,
			editable = (typeof what.editable == 'function') ? what.editable.call(what) : what.editable;
		
		$('<div>')
			.form(editable)
			.modal({
				title: 'Edit a '+classname,
				buttons:{
					'+Apply': function(){
						var $this = $(this);
						$this.form().validate().done(function(options){
							if(typeof what.validateForm == 'function')
								options = what.validateForm(options);
							
							if(!options)
								return false; // an error occurs so do not close the modal dialog
							
							what.setOptions(options);
							
							$this.modal('hide',callback);
						});
						
						return false;
					},
					'Cancel': null
				}
			})
		
	}
	
	// parent can either be a preset (another Rule to edit) or a parent (creating a new Rule)
	var RuleWizard = function(arg){
		
		var hasPreset = false;
		
		if(arg instanceof Rule){
			// deep copy the rule
			this.rule = Rule.fromJSON(arg.toJSON(),arg.parent);
			this.parent = this.rule.parent;
			hasPreset = true;
		}
		else if(arg instanceof EThing.Resource){
			this.parent = arg;
			this.rule = new Rule(this.parent);
		}
		else
			throw 'invalid argument';
		
		
		
		var self = this;
		
		
		// construct the dom
		var $html = $(
			'<div class="ruleWizard">'+
				'<div name="part1">'+
					'<div class="subpart subpart-primary" name="part.event">'+
					  '<h4>Event</h4>'+
					  '<p>When to execute this rule :</p>'+
					  '<p>'+
						'<div name="list.event"></div>'+
						'<button type="button" class="btn btn-primary btn-xs" name="select.event"><span class="glyphicon glyphicon-ok" aria-hidden="true"></span> Select</button>'+
						'<button type="button" class="btn btn-primary btn-xs" name="change.event" style="display: none;"><span class="glyphicon glyphicon-refresh" aria-hidden="true"></span> Change</button>'+
					   '</p>'+
					'</div>'+
				'</div>'+
				'<div name="part2" style="display:none;">'+
					'<div class="subpart subpart-primary" name="part.condition">'+
					  '<h4>Condition</h4>'+
					  '<p>Is there any condition to execute this rule :</p>'+
					  '<p>'+
						'<ul name="list.condition"></ul>'+
						'<button type="button" class="btn btn-primary btn-xs" name="add.condition"><span class="glyphicon glyphicon-plus" aria-hidden="true"></span> Add a new condition</button>'+
					   '</p>'+
					'</div>'+
					'<div class="subpart subpart-primary" name="part.action">'+
					  '<h4>Action</h4>'+
					  '<p>Select which action to execute :</p>'+
					  '<p>'+
						'<div name="list.action"></div>'+
					   '</p>'+
					'</div>'+
					'<div class="subpart subpart-primary" name="part.options">'+
					  '<h4>Options</h4>'+
					  '<p class="checkbox">'+
						'<label><input type="checkbox" name="repeat.rule"> repeat this rule</label>'+
					   '</p>'+
					  '<p class="alert alert-info" role="alert">'+
						'If the repeat mode is set, this rule will be executed every times the conditions match.'+
						'Else this rule will be executed only one time on the first conditions match. Then this rule will be disabled until the conditions are not met again.'+
						'This is useful if you want to send a notification only the first time this rule match and not every time.'+
					  '</p>'+
					  
					'</div>'+
				'</div>'+
				'<div class="alert alert-success" role="alert" style="display:none;"></div>'+
			'</div>'
		);
		
		
		
		var $events = $html.find('[name="list.event"]');
		listCompatible(events,self.rule).forEach(function(props,index){
			
			var event = this.rule.event && this.rule.event.name == props.name ? this.rule.event : null,
				selected = (!!event) || (!hasPreset && index==0);
			
			if(!event)
				event = new Event(props,self.parent);
			
			var $label = $('<label>'),
				$checkbox = $('<input type="radio" name="event" value="'+event.name+'" '+(selected?'checked':'')+'>').data('event',event);
			
			$label.append(
				$checkbox,
				event.label()+' '
			);
			
			if(event.isEditable()){
				$label.append(
					$('<button type="button" class="btn btn-default btn-xs"><span class="glyphicon glyphicon-edit" aria-hidden="true"></span> edit</button>').click(function(){
						edit(event);
					})
				)
			}
			
			$events.append(
				$('<div class="radio">')
					.append($label)
			)
				
		},self);
		
		var addEvent = function(event){
			self.rule.event = event;
			
			// disable the event selection
			$html.find('div[name="part.event"] input').prop('disabled',true);
			$html.find('button[name="select.event"]').hide();
			$html.find('button[name="change.event"]').show();
			
			// update the condition list
			$html.find('[name="list.condition"]').empty();
			self.rule.conditions.forEach(addCondition);
			
			// update the actions list
			var $actions = $html.find('[name="list.action"]').empty();
			listCompatible(actions,self.rule).forEach(function(props){
				
				var action = null;
				
				for(var i=0; i<self.rule.actions.length; i++)
					if(self.rule.actions[i].name == props.name){
						action = self.rule.actions[i];
						break;
					}
				
				var selected = !!action;
				
				if(!action)
					action = new Action(props,self.parent);
				
				var $label = $('<label>'),
					$checkbox = $('<input type="checkbox" name="action" value="'+action.name+'" '+(selected?'checked':'')+'>').change(function(){
						if($(this).is(':checked'))
							self.rule.addAction(action);
						else 
							self.rule.removeAction(action);
					});
				
				$label.append(
					$checkbox,
					action.label()+' '
				);
				
				if(action.isEditable()){
					$label.append(
						$('<button type="button" class="btn btn-default btn-xs"><span class="glyphicon glyphicon-edit" aria-hidden="true"></span> edit</button>').click(function(){
							edit(action);
						})
					)
				}
				
				$actions.append(
					$('<div class="checkbox">')
						.append($label)
				)

			});
			
			$html.find('input[name="repeat.rule"]').prop('checked',!!event.defaultRepeatValue);
			
			// enable the conditions and the actions
			$html.find('div[name="part2"]').show();
		}
		
		
		$html.find('button[name="select.event"]').click(function(){
			var event = $('input[name="event"]:checked', $html).data('event');
			if(!event)
				return;
			
			if(typeof event.callback == 'function'){
				var res = event.callback.call(event,self.rule);
				if(res!==false)
					$.when(res).done(function(){
						addEvent(event);
					});
			}
			else
				addEvent(event);
			
		});
		
		$html.find('button[name="change.event"]').click(function(){
			self.rule = new Rule(self.parent);
			
			$html.find('div[name="part.event"] input').prop('disabled',false);
			$html.find('button[name="select.event"]').show();
			$html.find('button[name="change.event"]').hide();
		});
		
		
		var addCondition = function(condition){
			
			self.rule.addCondition(condition);
			
			// update the dom
			var $condition = $('<li name="'+condition.id()+'">');
			$condition
				.html('<div name="label">'+condition.label()+'</div>')
				.append(
					$('<div class="btn-group">').append(
						$('<button type="button" class="btn btn-default btn-xs"><span class="glyphicon glyphicon-edit" aria-hidden="true"></span> edit</button>').click(function(){
							edit(condition, function(){
								// update the label
								$condition.find('[name="label"]').html(condition.label());
							});
						}),
						$('<button type="button" class="btn btn-default btn-xs"><span class="glyphicon glyphicon-trash" aria-hidden="true"></span> remove</button>').click(function(){
							removeCondition(condition);
						})
					)
				);
			$html.find('ul[name="list.condition"]').append($condition);
			
		}
		
		var removeCondition = function(condition){
			
			self.rule.removeCondition(condition);
				
			// update the dom
			$('li[name="'+condition.id()+'"]', $html).remove();
		}
		
		
		$html.find('button[name="add.condition"]').click(function(){
			
			var $conditionList = $('<div>');
			
			listCompatible(conditions,self.rule).forEach(function(props){
				var condition = new Condition(props,self.parent);
				
				var $label = $('<label>'),
					$checkbox = $('<input type="radio" name="condition" value="'+condition.name+'">').data('condition',condition);
				
				$label.append(
					$checkbox,
					condition.label()
				);
				
				$conditionList.append(
					$('<div class="radio">')
						.append($label)
				)
			},self);
			
			$conditionList.modal({
				title: 'Add a new condition',
				buttons: {
					'+Add': function(){
						var condition = $('input[name="condition"]:checked', $conditionList).data('condition'),
							$this = $(this);
						if(condition){
							if(condition.isEditable()){
								edit(condition, function(){
									addCondition(this);
									$this.modal('hide');
								});
								return false;
							}
							else
								addCondition(condition);
						}
						else
							return false; // empty selection
					},
					'Cancel': null
				}
			});
			
		});
		
		
		
		
		if(hasPreset){
			addEvent(this.rule.event);
			$html.find('input[name="repeat.rule"]').prop('checked',!!this.rule.repeat);
		}
		
		
		this._$ = $html;
		
	}
	
	RuleWizard.prototype.$ = function(){
		return this._$;
	}
	
	RuleWizard.prototype.validate = function(){
		
		this.rule.repeat = !!($('input[name="repeat.rule"]',this.$()).prop('checked'));
		
		if(!this.rule.isValid()){
			$('div[role="alert"]',this.$()).html('This rule is incomplete !').show();
			return null;
		}
		
		return this.rule;
	}
	
	
	
	
	
	
	
	
	
	
	/*******************
	*
	*
	*	jquery plugin
	*
	*
	********************/
	
	
	
	var ruleWizardPlugin = function(element, options) {

        var defaults = {
            parent: null,
			value: []
        }

        var plugin = this;

        plugin.settings = {}

        var $element = $(element),
             element = element,
			 isDisabled = false;

        plugin.init = function() {
            plugin.settings = $.extend({}, defaults, options);
            
			var parent = plugin.settings.parent;
			
			if(parent && (typeof parent.rules == 'function'))
				plugin.settings.value = parent.rules() || [];
			
			$element.empty();
			
			var nullRule = new Rule(parent);
			isDisabled = listCompatible(events,nullRule).length == 0 || listCompatible(actions,nullRule).length == 0;
			if(isDisabled){
				// if there is no available event or action, there is no point to try to build a rule !
				$element.html('<p class="text-muted">No rules are available for this resource</p>');
				return;
			}
			$('<button type="button" class="btn btn-default"><span class="glyphicon glyphicon-plus" aria-hidden="true"></span> Add a new rule</button>').click(function(){
				var wiz = new RuleWizard(parent);
				
				wiz.$().modal({
					title: 'Add a new rule for the '+parent.type()+' "'+parent.name()+'"',
					buttons:{
						'+Apply': function(){
							var rule = wiz.validate();
							if(!rule)
								return false;
							plugin.settings.value.push(rule.toJSON());
							buildDom();
						},
						'Cancel': null
					}
				})
				
			})
			.appendTo($element);
			
			buildDom();
			
        }

        plugin.value = function(value) {
            // No value passed, act as a getter.
			if ( value === undefined ) {
				return plugin.settings.value;
	
			// Value passed, act as a setter.
			} else if(!isDisabled) {
								
				if(!$.isArray(value))
					value = [value];
				
				plugin.settings.value = value || [];
				
				// update the dom
				buildDom();
			}
        }
		
		
		var buildDom = function(){
			var $html;
			
			if(plugin.settings.value.length){
				$html = $('<table class="table">');
				
				var $tbody = $('<tbody>').appendTo($html);
				
				plugin.settings.value.forEach(function(json, index){
					var parent = plugin.settings.parent,
						rule = Rule.fromJSON(json,parent);
					
					var $tr = $('<tr>'),
						$edit = $('<button class="btn btn-default" type="submit"><span class="glyphicon glyphicon-edit" aria-hidden="true"></span></button>').click(function(){
							var wiz = new RuleWizard(rule);
							
							wiz.$().modal({
								title: 'Edit rule #'+(index+1)+' for the '+parent.type()+' "'+parent.name()+'"',
								buttons:{
									'+Apply': function(){
										var rule = wiz.validate();
										if(!rule)
											return false;
										plugin.settings.value.splice(index,1,rule.toJSON());
										buildDom();
									},
									'Cancel': null
								}
							})
							
						}),
						$remove = $('<button class="btn btn-default" type="submit"><span class="glyphicon glyphicon-trash" aria-hidden="true"></span></button>').click(function(){
							plugin.settings.value.splice(index,1);
							buildDom();
						});
					
					[
						'<strong>'+(index+1)+'</strong>',
						rule.description(true),
						$('<div class="btn-group">').append($edit,$remove)
					].forEach(function(el){
						$('<td>').html(el).appendTo($tr);
					});
					
					$tr.appendTo($tbody);
				});
			}
			else
				$html = $('<p class="text-muted">No rules are installed</p>');
			
			$element.children().not('button').remove();
			$element.prepend($html);
			
		}

        plugin.init();

    }
	
	
	
	/* register as a plugin in jQuery */
	if (window.jQuery)
		window.jQuery.addPlugin('RuleWizard',ruleWizardPlugin);
	
	
	
	
	
	return Rule;
	
})();