(function (root, factory) {
    if (typeof define === 'function' && define.amd) {
        // AMD. Register as an anonymous module.
        define(['ui/core', 'text!./devices.html', 'jquery', 'ething','ui/infopanel', 'ui/browser', 'css!./devices', 'ui/formmodal', 'ui/resourceselect', 'css!font-awesome'], factory);
    }
}(this, function (UI, template, $, EThing, Infopanel) {
	
	
	
	
	var DeviceView = function(opt) {
		
		this._options = $.extend(true,{
			class: 'deviceview'
		},opt);
		
		$.Table.View.call(this);
	}
	DeviceView.prototype = Object.create($.Table.View.prototype);

	DeviceView.prototype.init = function($container, table){
		
		$.Table.View.prototype.init.call(this,$container,table);
		
		this._$grid = $('<div>').appendTo(this.$().addClass('container-fluid')).addClass(this._options.class);
		
	}
	DeviceView.prototype.clear = function(){
		this._$grid.find('.item[data-role="item"]').each(function(){
			var widget = $(this).data('widget');
			if(widget && typeof widget.destroy === 'function')
				widget.destroy();
		});
		
		this._$grid.empty();
		
		this._childrenStack = null;
	}
	
	DeviceView.prototype.createItem = function(device){
		var self = this;
		
		var $item = $('<div>');
		
		// construct the item dom element
		
		var name = UI.getResourceProperty(device,'name'),
			lastSeenDate = UI.getResourceProperty(device,'lastSeenDate'),
			battery = UI.getResourceProperty(device,'battery'),
			share = UI.getResourceProperty(device,'public');
		
		
		// icon
		var $icon = $('<div>').html($.Browser.generateSvgResourceIcon(device,true)).addClass('col-icon');
		
		// name
		var $name = $('<div class="col-name">').html(name.formattedValue);
		
		var $share = share.value ? $('<div class="tag col-share">').html('<i class="fa fa-users col-share" aria-hidden="true"></i>') : null;
		
		// battery
		var batIcon, batText = battery.value === null ? '' : '<span>'+Math.round(battery.value)+'%</span>';
		if(battery.value === null) batIcon = 'plug';
		else if(battery.value < 12.5) batIcon = 'battery-empty';
		else if(battery.value < 37.5) batIcon = 'battery-quarter';
		else if(battery.value < 62.5) batIcon = 'battery-half';
		else if(battery.value < 87.5) batIcon = 'battery-three-quarters';
		else batIcon = 'battery-full';
		var $battery = battery.value === null ? null : $('<div class="tag col-battery" '+(battery.value < 15?'style="color: #d9534f;"': '')+'>').html('<i class="fa fa-'+batIcon+'" aria-hidden="true"></i>'+batText);
		
		// last time the device communicate
		var $time = $('<div class="tag col-date">').html('<span class="glyphicon glyphicon-time" aria-hidden="true"></span><span>'+lastSeenDate.formattedValue+'</span>');		
		
		var $status = null;
		if(device.isConnected && !device.isConnected()){
			$status = $('<div class="tag col-status">').html('Disconnected');
		}
		if(device.isReachable && !device.isReachable() && !(device instanceof EThing.Device.Http && !device.url())){
			$status = $('<div class="tag col-status">').html('Unreachable');
		}
		
		// info
		var $info = $('<span class="glyphicon glyphicon-option-horizontal" aria-hidden="true"></span>').addClass('col-info').click(function(e){
			self.table().select(device);
			e.stopPropagation();
			Infopanel.show();
			return false;
		});
		
		var $children = $('<div class="children"></div>');
		
		$item.append(
			$('<div class="desc">').append(
				$icon,
				$('<div class="meta ellipsis">').append(
					$name,
					$share,
					$time,
					$battery,
					$status
				),
				$info
			),
			$children
		);
		
		if(!this._childrenStack) this._childrenStack = {};
		
		if(this._childrenStack && this._childrenStack[device.id()]){
			
			this._childrenStack[device.id()].forEach(function($child){
				$children.append($child);
			});
			
			delete this._childrenStack[device.id()];
		}
		
		var createdBy = device.createdBy();
		if(createdBy){
			
			if(!this._childrenStack[createdBy.id]) this._childrenStack[createdBy.id] = [];
			
			if(Array.isArray(this._childrenStack[createdBy.id])){
				// the parent is not already loaded, push this child in a temporary array
				this._childrenStack[createdBy.id].push($item);
			} else {
				this._childrenStack[createdBy.id].find('.children').first().append($item);
			}
			
		} else {
			this._$grid.append($item);
		}
		
		this._childrenStack[device.id()] = $item;
		
		return $item;
	}
	
	/*DeviceView.prototype.setSelectState = function(item, checked, $item){
		
		var $icon = $item.find('.col-icon > svg').toggleClass('col-select', checked);
		$icon.replaceWith($.Browser.generateSvgResourceIcon(checked ? 'Select' : item, true));
		
	}*/
	
	
	return {
		
		buildView: function(){
			
			var $element = UI.Container.set(template);
			
			Infopanel.enable();
			
			var $browser = this.$browser = $element.find('#devices-content').browser({
				view: new DeviceView(),
				model: {
					filter: function(r){
						return r instanceof EThing.Device;
					},
					flat: true
				},
				selectable:{
					enable: true,
					limit: 0,
					trigger: UI.isTouchDevice ? {
						event: 'click',
						selector: '.col-icon'
					} : 'click',
					cumul: UI.isTouchDevice
				},
				openable:{
					enable: true,
					open: function(r){
						UI.go('device',{
							rid: r.id()
						});
					}
				},
				message:{
					empty: function(){
						var $html = $(
								'<div class="text-center">'+
									'<p>'+
										'No device installed :-('+
									'</p>'+
								'</div>'
							);
						
						return $html;
					}
				}
			}).on('selection.change',function(){
				
				var selection = $(this).browser('selection');
				Infopanel.setResource(selection);
				
				$element.find('#devices-header button[data-action="remove"]').remove();
				if(selection.length){
					var $removeBtn = $('<button type="button" class="btn btn-link visible-xs-inline-block" data-action="remove"><span class="glyphicon glyphicon-trash" aria-hidden="true"></span> remove</button>').click(function(){
						UI.runAction('remove', selection);
					}).prependTo('#devices-header-btns');
				}
			});
			
			
			$element.find('#btn-create-Http').click(function(){
				var form = $.when( 
					UI.getResourceForm('Device\\Http', null, ['name','scope','location','description']),
					UI.getResourceForm('Device\\Http', null, ['url','auth','specification'])
				).then(function(globFormEntries, httpFormEntries){
					
					httpFormEntries.forEach(function(entry){
						if(entry.name === 'specification'){
							entry.description += " The specification describes the available requests that your device accepts.";
						}
					});
					
					
					return new $.Form.TabsLayout({
						format: $.Form.TabsLayout.Format.Merge,
						items: [{
							name: 'general',
							fields: ['name','scope','location','description'],
							item: new $.Form.FormLayout({
								items: globFormEntries
							})
						}, {
							name: 'server',
							fields: ['url','auth','specification'],
							item: new $.Form.FieldsEnabler({
								label: 'Enable',
								item: new $.Form.FormLayout({
									items: httpFormEntries
								}),
								description: 'Enable this feature if this device is accessible through HTTP request (acting like a server).',
								state: false,
								disabledValue: {
									url: null
								}
							})
						}]
					});
					
				});
				
				$.FormModal({
					header: 'A HTTP device is a device that use the HTTP protocol. An API KEY will be automatically generated for this device to access your data. Enable the server feature to interact with your device.',
					item: form,
					title: '<span class="glyphicon glyphicon-phone" aria-hidden="true"></span> Create a new Http Device',
					validLabel: '+Add',
					loaded: function($form){
						$form.form('findItem', 'name').focus();
					}
				},function(props){
					return EThing.Device.Http.create(props);
				});
			});
			
			$element.find('#btn-create-RTSP').click(function(){
				var form = UI.getResourceForm('Device\\RTSP', null, ['name','location','description','url','transport']).then(function(formEntries){
				
					return new $.Form.FormLayout({
						items: formEntries
					});
				});
				
				$.FormModal({
					item: form,
					title: '<span class="glyphicon glyphicon-phone" aria-hidden="true"></span> Add an IP camera',
					validLabel: '+Add',
					loaded: function($form){
						$form.form('findItem', 'name').focus();
					}
				},function(props){
					return EThing.Device.RTSP.create(props);
				});
			});
			
			$element.find('#btn-create-Denon').click(function(){
				var form = UI.getResourceForm('Device\\Denon', null, ['name','location','description','host']).then(function(formEntries){
				
					return new $.Form.FormLayout({
						items: formEntries
					});
				});
				
				$.FormModal({
					item: form,
					title: '<span class="glyphicon glyphicon-phone" aria-hidden="true"></span> Add a Denon/Marantz device',
					validLabel: '+Add',
					loaded: function($form){
						$form.form('findItem', 'name').focus();
					}
				},function(props){
					return EThing.Device.Denon.create(props);
				});
			});
			
			$element.find('#btn-create-MQTT').click(function(){
				
				var form = $.when( 
					UI.getResourceForm('Device\\MQTT', null, ['name','location','description','host','port','auth']),
					UI.getResourceForm('Device\\MQTT', null, ['subscription'])
				).then(function(formEntries, subscriptionFormEntries){
					
					return new $.Form.TabsLayout({
						format: $.Form.TabsLayout.Format.Merge,
						items: [{
							name: 'general',
							fields: ['name','location','description','host','port'],
							item: new $.Form.FormLayout({
								items: formEntries
							})
						}, {
							name: 'subscription',
							fields: ['topic','contentType'],
							item: new $.Form.FormLayout({
								items: subscriptionFormEntries
							})
						}]
					});
				});
				
				$.FormModal({
					item: form,
					title: '<span class="glyphicon glyphicon-phone" aria-hidden="true"></span> Add a MQTT client',
					validLabel: '+Add',
					loaded: function($form){
						$form.form('findItem', 'name').focus();
					}
				},function(props){
					return EThing.Device.MQTT.create(props);
				});
			});
			
			$element.find('#btn-create-SSH').click(function(){
				var form = UI.getResourceForm('Device\\SSH', null, ['name','location','description','host','port','auth']).then(function(formEntries){
					return new $.Form.FormLayout({
						items: formEntries
					});
				});
				
				$.FormModal({
					item: form,
					title: '<span class="glyphicon glyphicon-phone" aria-hidden="true"></span> Add a new SSH device',
					validLabel: '+Add',
					loaded: function($form){
						$form.form('findItem', 'name').focus();
					}
				},function(props){
					return EThing.Device.SSH.create(props);
				});
			});
			
			$element.find('#btn-create-BleaEthernetGateway').click(function(){
				var form = UI.getResourceForm('Device\\BleaEthernetGateway', null, ['name','location','description','host','port']).then(function(formEntries){
					return new $.Form.FormLayout({
						items: formEntries
					});
				});
				
				$.FormModal({
					item: form,
					title: '<span class="glyphicon glyphicon-phone" aria-hidden="true"></span> Add a new Blea gateway',
					validLabel: '+Add',
					loaded: function($form){
						$form.form('findItem', 'name').focus();
					}
				},function(props){
					return EThing.Device.SSH.create(props);
				});
			});
			
			$element.find('#btn-create-YeelightBulbRGBW').click(function(){
				var form = UI.getResourceForm('Device\\YeelightBulbRGBW', null, ['name','location','description','host']).then(function(formEntries){
					return new $.Form.FormLayout({
						items: formEntries
					});
				});
				
				$.FormModal({
					item: form,
					title: '<span class="glyphicon glyphicon-phone" aria-hidden="true"></span> Add a new Yeelight LED bulb (color) device',
					validLabel: '+Add',
					loaded: function($form){
						$form.form('findItem', 'name').focus();
					}
				},function(props){
					return EThing.Device.YeelightBulbRGBW.create(props);
				});
			});
			
			$element.find('#btn-create-RFLinkSerialGateway').click(function(){
				var form = UI.getResourceForm('Device\\RFLinkSerialGateway', null, ['name','location','description','port','baudrate']).then(function(formEntries){
				
					return new $.Form.FormLayout({
						items: formEntries
					});
				});
				
				$.FormModal({
					header: 'See <a href="//rflink.nl" target="_blank">RFLink website</a>',
					item: form,
					title: '<span class="glyphicon glyphicon-phone" aria-hidden="true"></span> Add a new Serial RFLink gateway client',
					validLabel: '+Add',
					loaded: function($form){
						$form.form('findItem', 'name').focus();
					}
				},function(props){
					return EThing.Device.RFLinkSerialGateway.create(props);
				});
			});
			
			$element.find('#btn-create-RFLinkNode').click(function(){
				var form = UI.getResourceForm('Device\\RFLinkNode', null, ['name','location','description','subType','protocol','nodeId','switchId']).then(function(formEntries){
					
					formEntries.unshift({
						name: 'gateway',
						item: new $.Form.ResourceSelect({
							filter: function(r){
								return r instanceof EThing.Device.RFLinkGateway;
							},
							validators: [$.Form.validator.NotEmpty]
						})
					});
					
					return new $.Form.FormLayout({
						items: formEntries,
						onattach: function(){
							var self = this;
							
							this.findItem('subType').change(function(){
								
								switch(this.value()){
									case 'switch':
									case 'door':
									case 'motion':
										self.setVisible('switchId',true);
										break;
									default:
										self.setVisible('switchId',false);
										break;
								}
								
							}).change();
						}
					});
				});
				
				$.FormModal({
					header: 'See <a href="//rflink.nl" target="_blank">RFLink website</a>',
					item: form,
					title: '<span class="glyphicon glyphicon-phone" aria-hidden="true"></span> Add a new RFLink node',
					validLabel: '+Add',
					loaded: function($form){
						$form.form('findItem', 'name').focus();
					}
				},function(props){
					return EThing.Device.RFLinkNode.create(props);
				});
			});
			
			$element.find('#btn-create-MySensorsGateway').click(function(){
				var form = UI.getResourceForm('Device\\MySensorsGateway', null, ['name','location','description','isMetric','transport','address','port','baudrate']).then(function(formEntries){
				
					
					return new $.Form.FormLayout({
						items: formEntries,
						onattach: function(){
							var self = this;
							
							this.findItem('transport').change(function(){
								
								switch(this.value()){
									case 'ethernet':
										self.setVisible('address',true);
										self.setVisible('port',false);
										self.setVisible('baudrate',false);
										break;
									case 'serial':
										self.setVisible('address',false);
										self.setVisible('port',true);
										self.setVisible('baudrate',true);
										break;
								}
								
							}).change();
						}
					});
				});
				
				$.FormModal({
					header: 'See <a href="//www.mysensors.org" target="_blank">MySensors website</a>',
					item: form,
					title: '<span class="glyphicon glyphicon-phone" aria-hidden="true"></span> Create a new MySensors Gateway',
					validLabel: '+Add',
					loaded: function($form){
						$form.form('findItem', 'name').focus();
					}
				},function(props){
					
					var transport = props.transport;
					delete props.transport;
					switch(transport){
						case 'ethernet':
							return EThing.Device.MySensorsEthernetGateway.create(props);
						case 'serial':
							return EThing.Device.MySensorsSerialGateway.create(props);
					}
				});
			});
			
			$element.find('#btn-create-MySensorsNode').click(function(){
				var form = UI.getResourceForm('Device\\MySensorsNode', null, ['name','location','description','nodeId','smartSleep']).then(function(formEntries){
				
					formEntries.unshift({
						name: 'gateway',
						item: new $.Form.ResourceSelect({
							filter: function(r){
								return r instanceof EThing.Device.MySensorsGateway;
							},
							validators: [$.Form.validator.NotEmpty]
						})
					});
					
					return (new $.Form.FormLayout({
						items: formEntries
					}));
				});
				
				$.FormModal({
					header: 'MySensors Nodes are created automatically. Use this form only if you want to add it manually.',
					item: form,
					title: '<span class="glyphicon glyphicon-phone" aria-hidden="true"></span> Create a new MySensors Node',
					validLabel: '+Add',
					loaded: function($form){
						$form.form('findItem', 'name').focus();
					}
				},function(props){
					return EThing.Device.MySensorsNode.create(props);
				});
			});
			
			$element.find('#btn-create-MySensorsSensor').click(function(){
				var form = $.Deferred();
				
				require(['ui/resourceselect'], function(){
					UI.getResourceForm('Device\\MySensorsSensor', null, ['name','location','description','sensorId','sensorType']).done(function(formEntries){
					
						formEntries.unshift({
							name: 'node',
							item: new $.Form.ResourceSelect({
								filter: function(r){
									return r instanceof EThing.Device.MySensorsNode;
								},
								validators: [$.Form.validator.NotEmpty]
							})
						});
						
						form.resolve(new $.Form.FormLayout({
							items: formEntries
						}));
					});
					
				});
				
				$.FormModal({
					header: 'MySensors Nodes are created automatically. Use this form only if you want to add it manually.',
					item: form,
					title: '<span class="glyphicon glyphicon-phone" aria-hidden="true"></span> Create a new MySensors Sensor',
					validLabel: '+Add',
					loaded: function($form){
						$form.form('findItem', 'name').focus();
					}
				},function(props){
					return EThing.Device.MySensorsSensor.create(props);
				});
			});
		},
		
		deleteView: function(){
			this.$browser.browser('destroy'); // destroy properly the device's widget
		}
	};
}));