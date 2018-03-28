(function (root, factory) {
    if (typeof define === 'function' && define.amd) {
        // AMD. Register as an anonymous module.
        define(['ui/core', 'text!./devices.html', 'jquery', 'ething','ui/infopanel', 'ui/meta', 'ui/browser', 'css!./devices', 'ui/formmodal', 'ui/resourceselect', 'css!font-awesome'], factory);
    }
}(this, function (UI, template, $, EThing, Infopanel, Meta) {
	
	
	
	
	var DeviceView = function(opt) {
		
		this._options = $.extend(true,{
			class: 'deviceview'
		},opt);
		
		$.Table.View.call(this);
		
		this._destroyFn = {};
	}
	DeviceView.prototype = Object.create($.Table.View.prototype);

	DeviceView.prototype.init = function($container, table){
		
		this.destroy();
		
		$.Table.View.prototype.init.call(this,$container,table);
		
		this._$grid = $('<div>').appendTo(this.$().addClass('container-fluid')).addClass(this._options.class);
		
	}
	DeviceView.prototype.clear = function(){
		this.destroy();
		
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
		
		// info
		var $info = $('<span class="glyphicon glyphicon-option-horizontal" aria-hidden="true"></span>').addClass('col-info').click(function(e){
			self.table().select(device);
			e.stopPropagation();
			Infopanel.show();
			return false;
		});
		
		var $wrapper = $('<div class="desc">');
		
		
		function update(){
			// construct the item dom element
			
			var name = device.name(),
				lastSeenDate = device.lastSeenDate(),
				battery = device.battery(),
				share = device.public();
			
			
			// icon
			var $icon = $('<div>').html($.Browser.generateSvgResourceIcon(device,true)).addClass('col-icon');
			
			// name
			var $name = $('<div class="col-name">').html(name);
			
			var $share = share ? $('<div class="tag col-share">').html('<i class="fa fa-users col-share" aria-hidden="true"></i>') : null;
			
			// battery
			var batIcon, batText = battery === null ? '' : '<span>'+Math.round(battery)+'%</span>';
			if(battery === null) batIcon = 'plug';
			else if(battery < 12.5) batIcon = 'battery-empty';
			else if(battery < 37.5) batIcon = 'battery-quarter';
			else if(battery < 62.5) batIcon = 'battery-half';
			else if(battery < 87.5) batIcon = 'battery-three-quarters';
			else batIcon = 'battery-full';
			var $battery = battery === null ? null : $('<div class="tag col-battery" '+(battery < 15?'style="color: #d9534f;"': '')+'>').html('<i class="fa fa-'+batIcon+'" aria-hidden="true"></i>'+batText);
			
			// last time the device communicate
			var $time = $('<div class="tag col-date">').html('<span class="glyphicon glyphicon-time" aria-hidden="true"></span><span>'+UI.dateToString(lastSeenDate)+'</span>');		
			
			var $status = null;
			if(device.hasAttr('connected') && !device.attr('connected')){
				$status = $('<div class="tag col-status">').html('Disconnected');
			}
			
			$wrapper.html([
				$icon,
				$('<div class="meta ellipsis">').append(
					$name,
					$share,
					$time,
					$battery,
					$status
				),
				$info
			]);
			
		}
		
		
		
		
		
		var $children = $('<div class="children"></div>');
		
		$item.append(
			$wrapper,
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
			
			if(!this._childrenStack[createdBy]) this._childrenStack[createdBy] = [];
			
			if(Array.isArray(this._childrenStack[createdBy])){
				// the parent is not already loaded, push this child in a temporary array
				this._childrenStack[createdBy].push($item);
			} else {
				this._childrenStack[createdBy].find('.children').first().append($item);
			}
			
		} else {
			this._$grid.append($item);
		}
		
		this._childrenStack[device.id()] = $item;
		
		var attrlist = ['name', 'battery', 'connected', 'public', 'lastSeenDate'];
		
		function onDeviceUpdated(event, updatedAttr){
			for(var i in attrlist){
				if(updatedAttr.indexOf(attrlist[i]) !== -1){
					update();
					return;
				}
			}
		}
		
		device.on('updated', onDeviceUpdated);
		
		this._destroyFn[device.id()] = function(){
			device.off('updated', onDeviceUpdated);
		};
		
		update();
		
		return $item;
	}
	
	/*DeviceView.prototype.setSelectState = function(item, checked, $item){
		
		var $icon = $item.find('.col-icon > svg').toggleClass('col-select', checked);
		$icon.replaceWith($.Browser.generateSvgResourceIcon(checked ? 'Select' : item, true));
		
	}*/
	DeviceView.prototype.destroy = function(){
		
		for(var id in this._destroyFn){
			this._destroyFn[id]();
		}
		
		this._destroyFn = {};
		
	}
	
	return {
		
		buildView: function(){
			
			var $element = UI.Container.set(template);
			
			
			// build the create menu
			function buidMenuItem(index, path) {
				
				var item = path[index];
				var parent = index==0 ? null : path[index-1];
				var isEndpoint = (index==(path.length-1));
				
				var $parent, $item;
				
				function toId(n){
					return path.slice(0,path.indexOf(n)+1).join('.').replace(/[^a-zA-Z0-9]/g, '_');
				}
				
				if(parent){
					$parent = $element.find('ul#menu-create-root li.menu-item-'+toId(parent)+' > ul');
				} else {
					$parent = $element.find('ul#menu-create-root');
				}
				
				$item = $parent.find('li.menu-item-'+toId(item));
				if($item.length == 0){
					$item = $('<li class="menu-item-'+toId(item)+'"><a>'+item+'</a></li>').appendTo($parent);
				}
				
				if(!isEndpoint){
					if(!$item.hasClass('dropdown-submenu')){
						$item.addClass('dropdown-submenu');
						$item.append('<ul class="dropdown-menu dropdown-menu-right">');
					}
				}
				
				return $item;
			}
			
			for(var type in Meta.reg){
				
				if(Meta.reg[type].creatable === false)
					continue;
				
				if(type === 'Device' || !Meta.issubclass(type, 'Device'))
					continue;
				
				var path = Meta.reg[type].path || [];
				var $lastItem;
				
				if(path.length == 0) path = [type];
				
				for(var i=0; i<path.length; i++){
					$lastItem = buidMenuItem(i, path);
				}
				
				(function (type, $lastItem) {
					$lastItem.find('a').click(function(){
						createDevice(type);
					});
				}(type, $lastItem));
			}
			
			
			function createDevice(type){
				var meta = Meta.get([type]);
				var name = meta.name();
				var cl = type;
				
				var form, categories = {};
				
				var filter = function(prop){
					return ['data'].indexOf(prop.name) === -1;
				};
		
				// tidy up by categories
				$.each(meta.properties, function(name, property){
					if(name === 'data') return;
					var category = property.category() || 'General';
					if(!categories.hasOwnProperty(category))
						categories[category] = [];
					categories[category].push(name);
				});
				
				if(Object.keys(categories).length > 1){
					// multiple tabs
					var catForms = [];
					
					Object.keys(categories).forEach(function(cat){
							
						catForms.push(Meta.getResourceForm(cl, categories[cat]).then(function(formItems){
							
							var item;
							
							// special case
							if( (type == 'Http') && /server/i.test(cat) ){
								item = new $.Form.FieldsEnabler({
									label: 'Enable',
									item: new $.Form.FormLayout({items: formItems}),
									state: false,
									disabledValue: {
										url: null
									}
								});
							}
							else
								item = new $.Form.FormLayout({
									items: formItems
								});
							
							return {
								name: cat,
								fields: categories[cat],
								item: item
							};
						}));
						
					});
					
					form= $.when.apply($, catForms).then(function(){
						var catItems = catForms.length==1 ? arguments[0] : Array.prototype.slice.call(arguments);
						
						return new $.Form.TabsLayout({
							format: $.Form.TabsLayout.Format.Merge,
							items: catItems
						});
					});
					
				}
				else {
					form = Meta.getResourceForm(cl, filter).then(function(formItems){
						return new $.Form.FormLayout({
							items: formItems
						});
					});
				}
				
				$.FormModal({
					header: meta.description || null,
					item: form,
					title: '<span class="glyphicon glyphicon-phone" aria-hidden="true"></span> Add a '+name,
					validLabel: '+Add',
					loaded: function($form){
						$form.form('findItem', 'name').focus();
					}
				},function(props){
					return EThing.Device.create(type, props);
				});
				
			}
			
			
			Infopanel.enable();
			
			var $browser = this.$browser = $element.find('#devices-content').browser({
				view: new DeviceView(),
				model: {
					filter: function(r){
						return r instanceof EThing.Device;
					},
					flat: true,
					onUpdate: function(added, removed, updated){
						if(added.length || removed.length) this.table().reload();
					}
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
			
			
			
			
			
		},
		
		deleteView: function(){
			this.$browser.browser('destroy'); // destroy properly the device's widget
		}
	};
}));