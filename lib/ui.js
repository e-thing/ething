 
/* @file: src\ui\utils.js */ 
(function () {
	
	if (window.jQuery) {
		
		window.jQuery.addPlugin = function(name,constructor){
			
			window.jQuery[name] = constructor;
			
			// the name of the plug in is by convention a small letter.
			var pluginName = name.charAt(0).toLowerCase() + name.slice(1);
			
			window.jQuery.fn[pluginName] = function(){
				var args = [].slice.call(arguments);
				
				if (this[0]) { // this[0] is the renderTo div
					
					var instance = $(this[0]).data(pluginName);
					
					if(instance){
						if(args.length){
							if(typeof args[0] == 'string'){
								// access the attribute or method
								var prop = instance[args.shift()];
								if(typeof prop == 'function'){
									var r = prop.apply(instance,args);
									return ((r === instance) || (typeof r == 'undefined')) ? this : r; // make it chainable
								}
								else {
									if(args.length==0){
										// getter
										return prop;
									}
									else if(args.length==1){
										// setter
										prop = args[0];
										return this;
									}
								}
							}
						}
						else
							return instance;// When called without parameters return the instance
					}
					
					// if we are are, it means that there is no instance or that the user wants to create a new one !
					instance = new constructor(this[0],args[0],args[1],args[2],args[3],args[4],args[5],args[6]);
					$(this[0]).data(pluginName,instance);
					
					return this;
				}
			}
		}
		
		
		
		function AbstractPlugin(element, options){
			
			this.$element = $(element);
			
			if(typeof options != 'undefined')
				this.options = $.extend(true,{},options);
			
			var self = this;
			['on','off','one','trigger'].forEach(function(method){
				self[method] = function(){
					var args = Array.prototype.slice.call(arguments);
					self.$element[method].apply(self.$element,args);
				}
			});
			
		}
		
		
		
		window.jQuery.AbstractPlugin = AbstractPlugin;
		
		
		
		
		function Dependency(require, onload){
			
			if(!(this instanceof Dependency))
				return new Dependency(require, onload);
			
			var this_ = this;
			
			var dfr = $.Deferred(), initied = false;
			
			dfr.promise(this);
			
			this.done(onload);
			
			this.require = function(doneCb){
				if(!initied){
					initied = true;
					EThing.utils.require(require)
						.done(function(){
							dfr.resolveWith(this);
						})
						.fail(function(){
							dfr.rejectWith(this);
						});
				}
				this_.done(doneCb);
				return this_;
			};
		};
		
		window.jQuery.Dependency = Dependency;
		
		
	}
	
})(this);
 
/* @file: src\ui\form.js */ 
(function(){
	
	
	var dependency = $.Dependency([
		'//gitcdn.github.io/bootstrap-toggle/2.2.2/css/bootstrap-toggle.min.css',
		'//gitcdn.github.io/bootstrap-toggle/2.2.2/js/bootstrap-toggle.min.js',
		'//cdnjs.cloudflare.com/ajax/libs/bootstrap-select/1.10.0/css/bootstrap-select.min.css',
		'//cdnjs.cloudflare.com/ajax/libs/bootstrap-select/1.10.0/js/bootstrap-select.min.js'
	]);
	
	// some helpers to handle select with the Selectpicker plugin
	function hideSelectPicker($e){
		$e.hide();
		if($e.data('selectpicker'))
			$e.selectpicker('hide');
		return $e;
	}
	function showSelectPicker($e){
		$e.show();
		if($e.data('selectpicker'))
			$e.selectpicker('show');
		return $e;
	}
	function refreshSelectPicker($e){
		if($e.data('selectpicker'))
			$e.selectpicker('refresh');
		return $e;
	}
	function valSelectPicker($e, val){
		if(typeof val == 'undefined')
			return $e.val();
		$e.val(val);
		if($e.data('selectpicker'))
			$e.selectpicker('render');
		return $e;
	}
	function selectPicker($e, opt){
		var isHidden = $e.is(':hidden');
		$e.selectpicker(opt);
		if(isHidden)
			$e.selectpicker('hide');
		return $e;
	}
	
	
	
	function inherits(extended, parent){
		extended.prototype = Object.create(parent.prototype);
	};
	
	
	
	
	function recursive(item,fn){
		if(typeof fn == 'string'){
			if(typeof item[fn] == 'function')
				item[fn]();
		}
		else
			fn.call(item);
		if(item.children_)
			for(var i=0; i<item.children_.length; i++)
				recursive(item.children_[i],fn);
	}
	
	
	function instanciateItem(item){
		if(typeof item == 'string'){
			return new Form.StandardItem({
				input: item
			});
		}
		else if($.isPlainObject(item)){
			if(typeof item.input != 'undefined')
				return new Form.StandardItem(item);
			else
				return new Form.FormLayout({
					items: item
				});
		}
		else if(Array.isArray(item))
			return new Form.ArrayLayout({
				items: item
			});
		else if(item instanceof Form.Item)
			return item;
		else
			throw 'invalide input data ['+(typeof item)+']'; // invalide input data
	}
	
	function sanitizeLayoutOptions(options){
		if(options instanceof Form.Item)
			return {
				items: [options]
			};
		else if(Array.isArray(options) || !$.isPlainObject(options) || typeof options.items == 'undefined')
			return {
				items: options
			};
		return options
	}
	
	
	
	// form builder
	function Form(element,opt){
		
		if(!$.isPlainObject(opt) || typeof opt.item == 'undefined')
			opt = {
				item: opt
			};
		
		opt.item = instanciateItem(opt.item);
		
		$.AbstractPlugin.call(this,element,opt);
		
		var self = this;
		
		this.$element.addClass('f-form');
		
		
		var item = opt.item;
		
		for(var fname in item){
			if(typeof item[fname] == 'function' && typeof this[fname] == 'undefined'){
				(function(this_,fn,item){
					this_[fn] = function(){
						var args = Array.prototype.slice.call(arguments, 0);
						return item[fn].apply(item,args);
					}
				})(this,fname,item);
			}
		}
		
		
		// draw it
		this.$error = $('<div class="alert alert-danger" role="alert">');
		this.$element.append(
			item.$element,
			this.$error.hide()
		);
		
		recursive(item,function(){
			this.form_ = self;
		});
		
		
		setTimeout(function(){
			
			recursive(item,function(){
				if(this.onload_){
					for(var i=0; i<this.onload_.length; i++)
						this.onload_[i].call(this);
				}
			});
			
			self.$element.trigger('loaded.f');
		},1);
		
	};
	
	Form.prototype.setError = function(message){
		if(typeof message == 'undefined' || message === null || message === false)
			this.$error.hide();
		else
			this.$error.html(message || 'error').show();
	};
	
	
	
	
	/*
	 item base class
	*/
	Form.Item = function(opt){
		this.options = $.extend(true,{
			name: null // used by the finding feature
		},opt);
		
		this.$element = this.$element || $('<div>');
	}
	Form.Item.prototype.name = function(){
		return this.options.name;
	};
	Form.Item.prototype.setError = function(message){
		if(typeof message == 'undefined' || message === null || message === false)
			message = null;
		
		var change = ( this.hasError() == (message===null) );
		this.error = message;
		
		this.$element.toggleClass('f-has-error',this.hasError());
		
		if(change)
			this.trigger('error-state-changed.f', [this,message]); // only trigger on change
	};
	Form.Item.prototype.hasError = function(){
		return !(typeof this.error == 'undefined' || this.error === null);
	};
	Form.Item.prototype.setValue = function(value){};
	// must return a jQuery deferred object containing the value on success or an error message on fail !
	Form.Item.prototype.validate = function(){};
	Form.Item.prototype.parent = function(){
		return this.parent_;
	};
	// return the root form object
	Form.Item.prototype.form = function(){
		return this.form_;
	};
	Form.Item.prototype.setParent = function(parent){
		if(!parent){
			// unlink
			if(this.parent_)
				this.parent_.removeChild(this);
			delete this.parent_;
		}
		else {
			if(this.parent_)
				this.parent_.removeChild(this);
			this.parent_ = parent;
			if(!parent.children_)
				parent.children_ = [];
			parent.children_.push(this);
		}
	};
	Form.Item.prototype.removeChild = function(item){
		// unlink
		delete item.parent_;
		if(this.children_){
			for(var i=0; i<this.children_.length; i++){
				if(this.children_[i]===item){
					this.children_.splice(i, 1);
					i--;
				}
			}
		}
	};
	Form.Item.prototype.addChild = function(item){
		item.setParent(this);
	};
	Form.Item.prototype.addChild = function(item){
		item.setParent(this);
	};
	['on','off','one','trigger'].forEach(function(method){
		Form.Item.prototype[method] = function(){
			var args = Array.prototype.slice.call(arguments);
			this.$element[method].apply(this.$element,args);
		}
	});
	Form.Item.prototype.findItem = function(name){
		if(this.name() === name)
			return this;
		if(this.children_)
			for(var i=0; i<this.children_.length; i++){
				var f = this.children_[i].findItem(name);
				if(typeof f != 'undefined')
					return f;
			}
	};
	Form.Item.prototype.onload = function(handler){
		if(typeof handler == 'function'){
			var isLoaded = !!this.form_;
			if(isLoaded) // if already loaded, just execute it right now
				handler.call(this);
			else { // else, store it to execute it later
				if(!this.onload_) this.onload_ = [];
				this.onload_.push(handler);
			}
		}
	}
	
	
	/*
	 layout base class
	*/
	Form.Layout = function(opt){
		var self = this;
		
		Form.Item.call(this,$.extend(true,{
			items: [],
			itemsOptions: []
		},opt));
		
		this.items_ = [];
		this.itemsOptions_ = [];
		
		this.errorHandle_ = function(evt,item,message){
			evt.stopPropagation();
			
			var error = false;
			self.items().forEach(function(item){
				if(item.hasError()){
					error = item.error;
					return false; // break;
				}
			});
			self.setError(error);
		};
		
		
		for(var i=0; i<this.options.items.length; i++){
			this.addItem(this.options.items[i], this.options.itemsOptions[i]);
		}
		
	}
	inherits(Form.Layout,Form.Item);
	
	Form.Layout.prototype.items = function(){
		return this.items_;
	};
	Form.Layout.prototype.addItem = function(item, itemOptions){
		
		if(typeof itemOptions == 'undefined')
			itemOptions = null;
		
		item = instanciateItem(item);
		this.items_.push(item);
		this.itemsOptions_.push(itemOptions);
		
		item.setParent(this);
		
		// update this error state each time a child error state changed
		item.on('error-state-changed.f',this.errorHandle_);
		
		return item;
	};
	Form.Layout.prototype.removeItem = function(item){
		for (var i = 0; i < this.items().length; i++) {
			if (this.items_[i] === item) {
				this.items_.splice(i, 1);
				this.itemsOptions_.splice(i, 1);
				i--;
			}
		}
		
		this.removeChild(item);
		
		// update this error state each time a child error state changed
		item.off('error-state-changed.f',this.errorHandle_);
	};
	Form.Layout.prototype.clear = function(){
		var length = this.length();
		while(length--){
			this.removeItem(this.items()[length]);
		}
	};
	Form.Layout.prototype.length = function(){
		return this.items().length || 0;
	};
	Form.Layout.prototype.getItemIndex = function(item){
		var items = this.items();
		for (var i = 0; i < items.length; i++) {
			if (items[i] === item) {
				return i;
			}
		}
		return -1;
	};
	Form.Layout.prototype.getItemOptions = function(item){
		if(typeof item == 'number')
			return this.itemsOptions_[item];
		
		var index = this.getItemIndex(item);
		if(index != -1)
			return this.itemsOptions_[index];
	};
	Form.Layout.prototype.getItemByIndex = function(index){
		if(typeof index == 'number')
			return this.items()[index];
	};
	Form.Layout.prototype.isEmpty = function(){
		return this.length() == 0;
	};
	Form.Layout.prototype.setValue = function(v){
		if(Array.isArray(v)){
			var items = this.items();
			for(var i=0; i<v.length && i<items.length; i++)
				items[i].setValue(v[i]);
		}
	};
	// if it fails, it will return the first error
	Form.Layout.prototype.validate = function(){
		// validate all the items
		var prop = [], dfr = $.Deferred(), promises = [], self = this;
		
		this.items().forEach(function(item, index){
			promises.push(
				$.when(item.validate()).done(function(value){
					prop[index] = value;
				})
			);
		});
		
		$.when.apply($, promises).done(function() {
			dfr.resolveWith(self,[prop]);
		}).fail(function(e) {
			dfr.rejectWith(self,[e]);
		});
		
		return dfr.promise();
	};
	
	
	
	
	/**
	* ArrayLayout
	*
	* return an array as a value
	*
	* options:
	*  items : [<Form.Item>]
	*  instanciator : function() -> <Form.Item>
	*  editable: <boolean>
	*
	*/
	Form.ArrayLayout = function(opt){
		
		this.$element = $('<div>').addClass('f-arraylayout');
		
		if($.isPlainObject(opt) && !opt.items)
			opt.items = [];
		
		var options = $.extend(true,{
			items:[],
			editable: true,
			instanciator: null
		},sanitizeLayoutOptions(opt));
		
		this.$content = $('<div>').appendTo(this.$element);
		
		if(options.editable && options.instanciator){
			var self = this,
				$add = $('<button type="button" class="btn btn-default"><span class="glyphicon glyphicon-plus" aria-hidden="true"></span> add</button>');
			
			$add.click(function(){
				self.addItem();
			});
			
			this.$element.append(
				$add
			);
		}
		
		Form.Layout.call(this, options);
	}
	inherits(Form.ArrayLayout,Form.Layout);
	
	Form.ArrayLayout.prototype.addItem = function(item){
		if(typeof item == 'undefined'){
			if(typeof this.options.instanciator == 'function')
				item = this.options.instanciator.call(this);
			else
				console.error('no instanciator function set !');
			if(!item)
				return;
		}
		
		item = Form.Layout.prototype.addItem.call(this,item);
		
		var self = this, editable = this.options.editable;
		
		var $wrapper = $('<div class="f-array-item">'),
			$delete = $('<button type="button" class="btn btn-default"><span class="glyphicon glyphicon-remove" aria-hidden="true"></span></button>').click(function(){
				self.removeItem(item);
				$wrapper.remove();
			});
		
		this.$content.append(
			$wrapper.append(
				item.$element,
				editable ? $delete : null
			)
		);
	};
	Form.ArrayLayout.prototype.removeItem = function(item){
		// get item index
		var index = this.getItemIndex(item);
		if(index!==-1){
			this.$content.children().eq(index).remove();
			Form.Layout.prototype.removeItem.call(this,item);
		}
	};
	Form.ArrayLayout.prototype.setValue = function(v){
		this.clear();
		if(Array.isArray(v)){
			for(var i=0; i<v.length; i++){
				var item = this.addItem();
				item.setValue(v[i]);
			}
		}
	};
	
	
	
	/**
	* FormLayout
	*
	* return an object as a value
	*
	* options:
	*  items : [{label: <string>, name: <string>, item: <Form.Item>}]
	*  inline : <boolean>
	*  disabledValue : <anything>
	*  skipOnDisabled : <boolean>
	*
	*/
	Form.FormLayout = function(opt){
		var meta = [];
		
		var options = $.extend(true,{
			inline: false,
			disabledValue: null,
			skipOnDisabled: false,
			emptyMessage: 'empty !',
			items: []
		},sanitizeLayoutOptions(opt));
		
		// reformat options.items to be compatible with the Layout Class
		if($.isPlainObject(options.items)){
			for(var label in options.items){
				meta.push({
					label: label,
					item: options.items[label]
				})
			}
		}
		else if(Array.isArray(options.items)){
			// must be an array of object { name: * , item: * }
			meta = [].concat(options.items);
		}
		
		var items = [];
		for(var i=0; i<meta.length; i++){
			items.push(meta[i].item);
			delete meta[i].item; // not fully constructed
		}
		
		options.items = items;
		options.itemsOptions = meta;
		
		this.$element = $('<div>').addClass('f-formlayout');
		
		if(options.inline)
			this.$element.addClass('form-inline');
		
		this.$element.append($('<div data-role="empty-msg">').html(options.emptyMessage));
		
		Form.Layout.call(this,options);
		
	}
	inherits(Form.FormLayout,Form.Layout);
	
	Form.FormLayout.defaults = {
		label: null,
		name: null,
		description: null,  // {String | Function} description of the field
		checkable: false, // set this field checkable, if not check, the return value will be null
		checked: false, // set the initial state of a checkable field
		skip: false, // if set, will be ignored in the validation object
		hidden: false, // if this field is hidden or not
		toggle: function(item,state){
			[item.$element, this.getItemOptions(item).$description].forEach(function($e){
				if(!$e) return;
				state ? $e.slideDown(200,function(){
					$(this).show();
				}) : $e.slideUp(200,function(){
					$(this).hide();
				}) // default behaviour is to hide/show the input
			})
		}
	}
	Form.FormLayout.prototype.getItemByName = function(name){
		var items = this.items();
		for(var i=0; i<items.length; i++){
			var options = this.getItemOptions(i);
			if(options.name === name)
				return items[i];
		}
	}
	Form.FormLayout.prototype.toggle = function(nameOrIndex,state){
		var item = (typeof nameOrIndex == 'number') ? this.item()[nameOrIndex] : this.getItemByName(nameOrIndex);
		if(item){
			var itemOptions = this.getItemOptions(item);
			state = !!state;
			if(itemOptions && itemOptions.checkable && (typeof itemOptions.disabled == 'undefined' || itemOptions.disabled == state)){
				itemOptions.disabled = !state;
				itemOptions.toggle.call(this,item,state);
				itemOptions.$checkbox.prop('checked',state).change();
			}
		}
	};
	Form.FormLayout.prototype.setVisible = function(nameOrIndex,visible){
		var item = (typeof nameOrIndex == 'number') ? this.item()[nameOrIndex] : this.getItemByName(nameOrIndex);
		if(item){
			var itemOptions = this.getItemOptions(item);
			visible = !!visible;
			if(itemOptions && (typeof itemOptions.hidden == 'undefined' || itemOptions.hidden == visible)){
				itemOptions.hidden = !visible;
				itemOptions.$wrapper.toggle(visible);
			}
		}
	};
	Form.FormLayout.prototype.addItem = function(item, options){
		
		if(!this.length()){
			this.$element.children('[data-role="empty-msg"]').remove(); // remove the empty message if any !
		}
		
		options = $.extend(true,{},Form.FormLayout.defaults,options);
		
		if(!options.name) // the name attribute is mandatory
			options.name = options.label;
			
		// set the name of the item if none was given
		if($.isPlainObject(item) && typeof item.name == 'undefined')
			item.name = options.name;
		
		item = Form.Layout.prototype.addItem.call(this,item, options);
		
		var label = options.label === false ? false : (options.label || options.name),
			$wrapper = $('<div class="form-group">'),
			$checkbox = null,
			self = this;
		
		if(options.checkable){
			
			$checkbox = $('<input type="checkbox">').change(function() {
				var state = $(this).prop('checked');
				self.toggle(options.name,state);
			}).css({
				'vertical-align': 'top'
			});
			
			options.$checkbox = $checkbox;
			
			$checkbox.prop('checked',options.checked);
		}
		
		// description
		var description = options.description;
		if(typeof description == 'function')
			description = description.call(this);
		options.$description = description && description!='' ? $('<p class="f-description">').html(description) : null;
		
		
		var $item = item.$element;
		if(this.options.inline)
			$item.css('display','inline-block');
		
		options.$wrapper = $wrapper.append(
			label ? $('<label>').html(label) : null,
			$checkbox,
			options.$description,
			$item
		);
		
		if(options.hidden)
			$wrapper.hide();
		
		// beautiful bootstrap switch
		dependency.require(function(){
			if($checkbox){
				$checkbox.bootstrapToggle({
					size: 'mini'
				});
			}
		});
		
		this.$element.append( $wrapper, ' ' );
		
		if($checkbox)
			this.onload(function(){
				$checkbox.change();
			});
	};
	
	Form.FormLayout.prototype.removeItem = function(item){
		// get item index
		var index = this.getItemIndex(item);
		if(index!==-1){
			this.$element.children().eq(index).remove();
			Form.Layout.prototype.removeItem.call(this,item);
			
			if(!this.length()){
				this.$element.append($('<div data-role="empty-msg">').html(this.options.emptyMessage));
			}
		}
	};
	Form.FormLayout.prototype.setValue = function(v){
		var items = this.items();
		
		if($.isPlainObject(v)){
			var keys = Object.keys(v);
			for(var i=0; i<keys.length; i++){
				var key = keys[i],
					item = this.getItemByName(key);
				if(item){
					item.setValue(v[key]);
					this.toggle(key,true); // enable the item
				}
			}
		}
		
	};
	Form.FormLayout.prototype.validate = function(){
		// validate all the items
		var prop = {}, dfr = $.Deferred(), promises = [], self = this;
		
		this.items().forEach(function(item, index){
			var optionsItem = this.getItemOptions(item);
			if(optionsItem.skip || (optionsItem.disabled && this.options.skipOnDisabled))
				return;
			
			promises.push(
				$.when(optionsItem.disabled ? this.options.disabledValue : item.validate()).done(function(value){
					prop[optionsItem.name] = value;
				})
			);
		}, this);
		
		$.when.apply($, promises).done(function() {
			dfr.resolveWith(self,[prop]);
		}).fail(function(e) {
			dfr.rejectWith(self,[e]);
		});
		
		return dfr.promise();
	};
	
	
	
	
	
	/*
	* TabsLayout
	* 
	* options:
	*  items : [{name: <string>, item: <Form.Item>}]
	*  merge: <boolean> whether or not merge the value of each tab (tabs item must all return either an array or an object)
	*/
	Form.TabsLayout = function(opt){
		
		var options = sanitizeLayoutOptions(opt);
		
		var items = [];
		if(Array.isArray(options.items))
			items = options.items;
		else if($.isPlainObject(options.items))
			for(var i in options.items){
				items.push({
					name: i,
					item: options.items[i]
				});
			}
		
		options.items = [];
		options.itemsOptions = [];
		
		for(var i=0; i<items.length; i++){
			var name = items[i].name,
				item = items[i].item;
			
			options.items.push(item);
			options.itemsOptions.push({
				name: name
			});
			
		}
		
		
		this.$element = $('<div>').addClass('f-tabslayout');
		
		this.$navTabs = $('<ul class="nav nav-tabs" role="tablist">');
		this.$tabPanes = $('<div class="tab-content">');
		
		this.$element.append(
			this.$navTabs,
			this.$tabPanes
		);
		
		Form.Layout.call(this,options);
		
		this.on('error-state-changed.f',function(evt,item){
			var $navli = item.$navTabs.children('li');
			item.items().forEach(function(item,index){
				$navli.eq(index).toggleClass('f-has-error',item.hasError());
			});
		});
	}
	inherits(Form.TabsLayout,Form.Layout);
	
	Form.TabsLayout.prototype.getItemByTabName = function(name){
		var items = this.items();
		for(var i=0; i<items.length; i++){
			var options = this.getItemOptions(i);
			if(options.name === name)
				return items[i];
		}
	}
	
	Form.TabsLayout.prototype.addItem = function(item,options){
		
		options = $.extend(true,{
			name: 'tab'+this.length()
		},options);
		
		item = Form.Layout.prototype.addItem.call(this,item,options);
		
		var id = String(Math.round(Math.random()*1000000)), t=this.$navTabs.children().length;
		
		this.$navTabs.append('<li role="presentation" class="'+(t==0?'active':'')+'"><a href="#'+id+'" role="tab" data-toggle="tab">'+options.name+'</a></li>');
		$('<div role="tabpanel" class="tab-pane '+(t==0?'active':'')+'" id="'+id+'">').appendTo(this.$tabPanes).append(item.$element);
		
		return item;
	};
	Form.TabsLayout.prototype.setValue = function(v){		
		var merge = !!this.options.merge;
		
		if(merge){
			this.items().forEach(function(item){
				item.setValue(v);
			});
		}
		else {
			for(var key in v){
				var item = getItemByTabName(key);
				if(item)
					item.setValue(v[key]);
			}
		}
	};
	Form.TabsLayout.prototype.validate = function(){
		return Form.Layout.prototype.validate.call(this).then(
			function(arrvalues){
				var prop = {}, merge = !!this.options.merge;
				
				arrvalues.forEach(function(value, index){
					if(merge)
						prop = $.extend(true,prop,value);
					else{
						var optionsItem = this.getItemOptions(index);
						prop[optionsItem.name] = value;
					}
				}, this);
				
				return prop;
			}
		);
	};
	
	
	
	
	/*
	 Standard Item class
	*/
	Form.StandardItem = function(opt,name){
		
		if(!$.isPlainObject(opt))
			opt = {
				input: opt
			};
		
		var options = $.extend(true,{
			input: 'text', // the input field, could be :
			//    - an html string "<...>" , so the input will be created on the fly from the html string
			//    - a input type such as 'text|number|url ...', the generated html will be <input type="...">
			//    - a function returning a DOM element or a jQuery object
			get: function($e, validation){ // input getter
				if($e.is('input[type="checkbox"]'))
					return !!$e.prop('checked');
				if($e.data('form'))
					return $e.form(validation ? 'validate' : 'getValue');
				if($e.is('input[type="number"]')){
					var v = $e.val();
					return (typeof v == 'string' && (v===''||!/^(\-|\+)?([0-9]+(\.[0-9]+)?|Infinity)$/.test(v))) ? null : Number($e.val());
				}
				return $e.val();
			},
			set: function($e,value){ // input setter
				if($e.is('input[type="checkbox"]')){
					$e.prop('checked',!!value).change();
					return;
				}
				$e.data('form') ? $e.form('setValue',value) : $e.val(value);
			},
			attr: null, // attribute to be added to the input
			'class': null, // class to be added to the input
			value: null, // set the initial value of the field
			description: null, // {String | Function} description of the field
			onload: null, // is executed once the form is fully loaded
			on: null, // attach some handlers to events
			validator: null // some validator to validate the input
		},opt);
		
		
		Form.Item.call(this,options);
		
		this.$element.addClass("f-standarditem");
		
		
		
		this.$error = $('<div class="alert alert-danger" role="alert">');
		
		var input = $.isFunction(options.input) ? options.input.call(this) : options.input,
			$input = null,
			self = this;
		
		
		if(input.jquery){ // a jquery object
			$input = input;
		}
		else if(typeof input == 'string'){
			$input = /^</.test(input) ? $(input) : (input==='textarea' ? $('<textarea>') : $('<input type="'+input+'">'));
		}
		else if($.isArray(input)){
			$input = $('<select>');
			input.forEach(function(optstr){
				$input.append('<option value="'+optstr+'">'+optstr+'</option>');
			});
		}
		else if($.isPlainObject(input)){
			$input = $('<select>');
			for(var key in input)
				$input.append('<option value="'+input[key]+'">'+key+'</option>');
		}
		else
			$input = $('<input type="text">');
		
		
		this.$input = $input;
		
		$input.addClass('f-input');
		
		this.isFormControl = $input.is('textarea,select,input:not([type="checkbox"]):not([type="file"]):not([type="button"])');
		
		if(this.isFormControl)
			$input.addClass('form-control');
		
		if($.isPlainObject(options.attr))
			for(var i in options.attr)
				$input.prop(i,$.isFunction(options.attr[i]) ? options.attr[i].call(this) : options.attr[i]);
		
		$input.addClass(options['class']);
		
		if($.isFunction(options.set) && options.value!==null && (typeof options.value != 'undefined'))
			options.set.call(this,$input,options.value);
		
		if($input.is('input') || $input.is('textarea') || $input.is('select'))
			$input.change(function(){
				//self.setError(false);
				self.validate();
			});
		
		// events
		if($.isPlainObject(options.on)){
			for(var eventName in options.on){
				if(typeof options.on[eventName] == 'function')
					$input.on(eventName, function(ev){
						options.on[eventName].call(self,ev);
					});
			}
		}
		
		var id = $input.attr('id');
		if(!id){
			id = String(Math.round(Math.random()*100000));
			$input.attr('id', id);
		}
		
		// description
		var description = options.description;
		if(typeof description == 'function')
			description = description.call(this);
		
		this.$error_fb_ctrl = null;
		if(this.isFormControl)
			this.$error_fb_ctrl = $('<span class="glyphicon glyphicon-remove form-control-feedback">').hide();
		
		this.$element.append(
			description ? $('<p class="f-description">').html(description) : null,
			$input,
			this.$error_fb_ctrl,
			this.$error.hide()
		);
		
		this.onload(function(){
			if(typeof self.options.onload == 'function')
				self.options.onload.call(self,self.$input);
		});
		
		
	}
	inherits(Form.StandardItem,Form.Item);
	
	Form.StandardItem.prototype.setError = function(message){
		Form.Item.prototype.setError.call(this,message);
		
		message = String(message);
		
		if(this.hasError() && message.length)
			this.$error.html(message).show();
		else
			this.$error.hide();
		
		if(this.isFormControl){
			this.$element.toggleClass('has-error',this.hasError());
			this.$element.toggleClass('has-feedback',this.hasError());
			this.$error_fb_ctrl.toggle(this.hasError());
		}
	};
	Form.StandardItem.prototype.getValue = function(){
		var r;
		try {
			if(typeof this.options.get == 'function')
				r = this.options.get.call(this,this.$input,false)
		}
		catch(e){}
		return r;
	};
	Form.StandardItem.prototype.setValue = function(v){
		this.setError(false); // remove any error
		
		try {
			if(typeof this.options.set == 'function'){
				this.options.set.call(this,this.$input,v);
				
				var validators = this.options.validator || [];
				if(!Array.isArray(validators)) validators = [validators];
				for(var i=0; i<validators.length; i++)
					if(typeof validators[i] == 'function')
						validators[i].call(this,v);
			}
		}
		catch(e){
			this.setError(e || '');
		}
	}
	Form.StandardItem.prototype.validate = function(){
		var r, dfr = $.Deferred(), self = this;
		
		this.setError(false); // remove any error
		
		try {
			if(typeof this.options.get == 'function'){
				r = this.options.get.call(this,this.$input,true);
				
				var validators = this.options.validator || [];
				if(!Array.isArray(validators)) validators = [validators];
				for(var i=0; i<validators.length; i++)
					if(typeof validators[i] == 'function')
						validators[i].call(this,r);
			}
		}
		catch(e){
			this.setError(e || '');
			dfr.rejectWith(this);
		}
		
		if(dfr.state()=='pending')
			$.when(r).done(function(value){
				dfr.resolveWith(self,[value]);
			}).fail(function(e){
				self.setError(e || '');
				dfr.rejectWith(self);
			});
		
		return dfr.promise();
	};
	Form.StandardItem.prototype.input = function(){
		return this.$input;
	};
	
	
	
	
	
	
	Form.Duration = function(opt){
		
		
		Form.StandardItem.call(this,$.extend(true,{
			input: function(){
				
				var $form = $('<div class="form-inline">'), self = this;
		
				function createInput(name){
					var uid = Math.random()*10000000,
						$input = $('<input class="form-control" id="'+uid+'" name="'+name+'" type="number" step="1" value="0" min="0">');
					
					$('<div class="form-group">').append(
						$input,
						'<label for="'+uid+'">'+name+'(s)</label>'
					).appendTo($form).change(function(){
						$form.trigger('change',[secondes]);
					});
					
					return $input;
				}
				
				
				if(this.options.day){
					createInput('day');
				}
				if(this.options.hour){
					createInput('hour').attr('max','24');
				}
				if(this.options.minute){
					createInput('minute').attr('max','60');
				}
				
				return $form;
				
			},
			get: function($form){
				var seconds = 0;
				seconds += 86400 * parseInt($form.find('input[name="day"]').val() || 0);
				seconds += 3600 * parseInt($form.find('input[name="hour"]').val() || 0);
				seconds += 60 * parseInt($form.find('input[name="minute"]').val() || 0);
				return seconds;
			},
			set: function($form,v){
				
				var secondes = v,
					day = Math.floor(secondes / 86400),
					hour = Math.floor((secondes - day * 86400) / 3600),
					minute = Math.floor((secondes-day*86400-hour*3600) / 60);
				
				$form.find('input[name="day"]').val(day);
				$form.find('input[name="hour"]').val(hour);
				$form.find('input[name="minute"]').val(minute);
				
				$form.trigger('change',[secondes]);
			}
		},{
			minute: true, // show minute
			hour: true, // show hour
			day: true // show day
		},opt));
		
		this.$element.addClass("f-duration");
	}
	inherits(Form.Duration,Form.StandardItem);
	
	
	
	function resourceToSelectDataContent(resource){
		return '<span class="f-select-resource">'+$.Browser.generateSvgResourceIcon(resource, false)+' <span>'+resource.name()+'</span></span>';
	}
	
	
	Form.ResourceSelect = function(opt){
		var dfr = $.when(EThing.arbo.load(),dependency.require());
		
		Form.StandardItem.call(this,$.extend(true,{
			input: function(){
				var $resources = $('<select class="form-control">'),
					$input = $('<div>').html('loading...'),
					self = this;
				
				$resources.change(function(){
					var resource = EThing.arbo.findOneById($(this).val());
					if(resource){
						if(typeof self.options.onChange == 'function')
							self.options.onChange.call(self,resource);
					}
				});
				
				dfr.done(function(){
					var resources = EThing.arbo.find(self.options.filter);
					
					for(var i=0; i<resources.length; i++){
						$resources.append('<option data-content=\''+resourceToSelectDataContent(resources[i])+'\' value="'+resources[i].id()+'">'+resources[i].name()+'</option>');
					}
					
					$input.empty().append($resources);
					
					$resources.selectpicker({
						title: 'Select a resource',
						showTick: true,
						header: 'Select a resource',
						width: 'fit'
					});
					
					$('select',$input).change();
				});
				
				return $input;
			},
			onload: function($input){
				$('select',$input).change();
			},
			get: function($input){
				return $('select',$input).val();
			},
			set: function($input,v){
				dfr.done(function(){
					valSelectPicker($('select',$input),v).change();
				});
			}
		},{
			filter: null,
			onChange: null
		},opt));
		
		this.$element.addClass("f-resourceselect");
	}
	inherits(Form.ResourceSelect,Form.StandardItem);
	
	Form.TableFieldSelect = function(opt){
		var dfr = $.when(EThing.arbo.load(),dependency.require());
		
		function updateFieldList($input){
			var $tables = $('select[name="table"]',$input),
				$fields = $('select[name="field"]',$input),
				tableId = $tables.val(),
				fieldTableId = $fields.data('tableId');
			
			if(tableId != fieldTableId){
				// the field list does not match the selected table, update it !
				$fields.empty();
				var table = EThing.arbo.findOneById(tableId);
				if(table && table instanceof EThing.Table){
					var fields = table.keys();
					for(var i=0; i<fields.length; i++)
						$fields.append('<option>'+fields[i]+'</option>');
					refreshSelectPicker($fields);
					showSelectPicker($fields);
					$fields.data('tableId',tableId);
				}
				else
					hideSelectPicker($fields);
			}
		}
		
		Form.StandardItem.call(this,$.extend(true,{
			input: function(){
				var $tables = $('<select class="form-control" name="table">'),
					$fields = $('<select class="form-control" name="field">'),
					$input = $('<div class="form-inline">').html('loading...'),
					self = this;
				
				$tables.change(function(){
					updateFieldList($input);
					$fields.change();
				});
				
				$fields.change(function(){
					var $this = $(this),
						field = $this.val(),
						fieldTableId = $this.data('tableId'),
						table = EThing.arbo.findOneById(fieldTableId);
					
					self.setError(false);
					
					if(typeof self.options.onChange == 'function')
						self.options.onChange.call(self,table,field);
				});
				
				dfr.done(function(){
					var tables = EThing.arbo.find(function(r){
						return r instanceof EThing.Table;
					});
					
					for(var i=0; i<tables.length; i++){
						$tables.append('<option data-content=\''+resourceToSelectDataContent(tables[i])+'\' value="'+tables[i].id()+'" '+(tables[i].keys().length?'':'disabled')+'>'+tables[i].name()+'</option>');
					}
					
					$input.empty().append($tables," ",$fields);
					
					$tables.selectpicker({
						title: 'Select a table',
						showTick: true,
						header: 'Select a table',
						width: 'fit'
					});
					$fields.selectpicker({
						title: 'Select a field',
						showTick: true,
						header: 'Select a field',
						width: 'fit'
					});
					
					
					
					updateFieldList($input);
				});
				
				return $input;
			},
			onload: function($input){
				dfr.done(function(){
					$('select[name="field"]',$input).change();
				});
			},
			get: function($input){
				var tableId = $('select[name="table"]',$input).val(),
					field = $('select[name="field"]',$input).val();
				if(!tableId)
					throw 'No table selected';
				if(!field)
					throw 'No field selected';
				return {
					'tableId':tableId,
					'field':field
				};
			},
			set: function($input,v){
				dfr.done(function(){
					valSelectPicker($('select[name="table"]',$input), v.tableId);
					updateFieldList($input);
					valSelectPicker($('select[name="field"]',$input), v.field).change();
				});
			}
		},{
			onChange: null
		},opt));
		
		this.$element.addClass("f-tablefieldselect");
	}
	inherits(Form.TableFieldSelect,Form.StandardItem);
	
	
	
	
	Form.DeviceOperationSelect = function(opt){
		var dfr = $.when(EThing.arbo.load(),dependency.require()), swaggerClient;
		
		function updateOperationList($input, cb){
			var $devices = $('select[name="device"]',$input),
				$operations = $('select[name="operation"]',$input),
				$loading = $input.children('span'),
				deviceId = $devices.val(),
				operationDeviceId = $operations.data('deviceId'),
				cdfr;
			
			if(deviceId !== operationDeviceId){
				// the field list does not match the selected table, update it !
				hideSelectPicker($operations).empty();
				var device = EThing.arbo.findOneById(deviceId);
				if(device && device instanceof EThing.Device){
					$loading.show();
					cdfr = device.getSwaggerClient().done(function(client){
						swaggerClient = client;
						for(var opname in client.operations){
							$operations.append('<option data-subtext="'+client.operations[opname].api.method+'">'+opname+'</option>');
						}
						refreshSelectPicker($operations);
						showSelectPicker($operations);
						$loading.hide();
					});
					$operations.data('deviceId',deviceId).data('cdfr',cdfr);
				}
			}
			
			cdfr = $operations.data('cdfr');
			if(cdfr)
				cdfr.done(cb);
		}
		
		
		Form.StandardItem.call(this,$.extend(true,{
			input: function(){
				var $devices = $('<select class="form-control" name="device">'),
					$loading = $('<span>').html('loading...'),
					$operations = $('<select class="form-control" name="operation">'),
					$input = $('<div class="form-inline">').append(' ',$loading,' '),
					self = this;
				
				$devices.change(function(){
					updateOperationList($input, function(){
						$operations.change();
					});
				});
				
				$operations.change(function(){
					var $this = $(this),
						operation = $this.val(),
						operationDeviceId = $this.data('deviceId'),
						device = EThing.arbo.findOneById(operationDeviceId);
					
					if(operation && typeof self.options.onChange == 'function')
						self.options.onChange.call(self,device,operation,swaggerClient);
				});
				
				
				dfr.done(function(){
					var devices = EThing.arbo.find(function(r){
						return r instanceof EThing.Device;
					});
					
					for(var i=0; i<devices.length; i++){
						$devices.append('<option data-content=\''+resourceToSelectDataContent(devices[i])+'\' value="'+devices[i].id()+'" '+(devices[i].url()?'':'disabled')+'>'+devices[i].name()+'</option>');
					}
					
					$input.prepend($devices);
					$input.append($operations);
					
					$devices.selectpicker({
						title: 'Select a device',
						showTick: true,
						header: 'Select a device',
						width: 'fit'
					});
					
					selectPicker($operations, {
						title: 'Select an operation',
						showTick: true,
						header: 'Select an operation',
						width: 'fit'
					});
					
					$loading.hide();
					
					updateOperationList($input);
				});
				
				
				
				return $input;
			},
			onload: function($input){
				dfr.done(function(){
					updateOperationList($input,function(){
						$('select[name="operation"]',$input).change();
					});
				});
			},
			get: function($input){
				var deviceId = $('select[name="device"]',$input).val(),
					operation = $('select[name="operation"]',$input).val();
				if(!deviceId)
					throw 'No device selected';
				if(!operation)
					throw 'No operation selected';
				return {
					'deviceId':deviceId,
					'operation':operation
				};
			},
			set: function($input,v){
				dfr.done(function(){
					valSelectPicker($('select[name="device"]',$input),v.deviceId);
					updateOperationList($input,function(){
						valSelectPicker($('select[name="operation"]',$input),v.operation).change();
					});
				});
			}
		},{
			onChange: null
		},opt));
		
		this.$element.addClass("f-deviceoperationselect");
	}
	inherits(Form.DeviceOperationSelect,Form.StandardItem);
	
	
	Form.File = function(opt){
		Form.StandardItem.call(this,$.extend(true,{
			input: function(){
				var self = this,
					$fileSelector = $('<input type="file">').change(function(){
						if(typeof self.options.onChange == 'function'){
							try{
								self.options.onChange.call(self, $(this)[0]);
							} catch(e){
								self.setError(e);
							}
						}
					}),
					$btn = $('<button class="btn btn-default">'+self.options.title+'</button>').click(function(){
						$fileSelector.click();
						return false;
					});
				if(this.options.accept)
					$fileSelector.attr('accept',this.options.accept);
				this.$fileSelector = $fileSelector;
				return $btn;
			},
			set: function($input,v){}, // read only
			get: function($input){
				// returns the content of the file as an ArrayBuffer
				var input = this.$fileSelector[0], self = this;
				if (!input.files) {
					throw "This browser doesn't seem to support the `files` property of file inputs.";
				}
				else if (!input.files[0]) {
					if(self.options.allowEmpty)
						return null;
					throw "Please select a file";
				}
				else {
					var file = input.files[0];
					return (typeof self.options.transform == 'function') ? self.options.transform.call(self, file) : file;
				}
			}
		},{
			onChange: null, // is fired every time a new set of files have been selected function(input)  get the files through input.files 
			transform: null, // function(File) -> newContent
			accept: null, // The accept attribute specifies the types of files that is accepted (ie : '.csv,.tsv,.tab,text/plain' )
			title: 'browse', // the title of the file dialog
			allowEmpty: false // allow empty selection. Return null value instead of the content of a file.
		},opt));
		
	}
	inherits(Form.File,Form.StandardItem);
	// basic transformation function
	Form.File.toArrayBuffer = function(file){
		var fr = new FileReader()
			dfr = $.Deferred();
		fr.onload = function(){
			dfr.resolve(fr.result);
		};
		fr.onerror = fr.onabort = function(){
			dfr.reject();
		}
		fr.readAsArrayBuffer(file);
		return dfr.promise();
	}
	Form.File.toBase64 = function(file){
		return Form.File.toArrayBuffer(file).then(function(data){
			// transform the result into base64 string
			var binary = '',
				bytes = new Uint8Array(data);
			for (var i = 0; i < bytes.byteLength; i++) {
				binary += String.fromCharCode( bytes[ i ] );
			}
			return window.btoa(binary);
		});
	}
	Form.File.toString = function(file){
		return Form.File.toArrayBuffer(file).then(function(data){
			return String.fromCharCode.apply(null, new Uint16Array(data));
		});
	}
	
	
	
	Form.Image = function(opt){
		
		var self = this,
			$fileSelector = $('<input type="file">'),
			$defaultImg = $('<div class="f-image-thumbnail-empty">empty</div>'),
			$preview = $('<img>'),
			$meta = $('<div class="f-image-meta"></div>'),
			$browseBtn = $('<button class="btn btn-primary">Browse</button>'),
			$removeBtn = $('<button class="btn btn-default">Remove</button>'),
			undefined,
			value = undefined,
			beforeSet,
			cnt = 0;
		
		function change(v){
			var ok = true;
			self.setError();
			if(typeof self.options.onChange == 'function'){
				try{
					self.options.onChange.call(self, v);
				} catch(e){
					self.setError(e);
					ok = false;
				}
			}
			if(ok) value = v;
			return ok;
		}
		
		function set(v){
			
			var id = ++cnt; // used for async operation
			
			if(typeof beforeSet == 'function')
				beforeSet();
			
			beforeSet = null;
			
			if(!v){ // remove
				$preview.hide().attr('src','');
				$defaultImg.show();
				$meta.empty().hide();
				$removeBtn.hide();
				change();
				return;
			}
			
			if(typeof v == 'string'){ //image url
				
				value = $.Deferred();
				
				var xhr = new XMLHttpRequest();
				xhr.open('GET', v, true);
				xhr.responseType = 'blob';
				 
				xhr.onload = xhr.onerror = function(e) {
				  if (this.status && this.status >= 200 && this.status < 400) {
					// get binary data as a response
					value.resolve(this.response);
				  }
				  else
					value.reject('unable to load');
				};
				 
				xhr.send();
				
				beforeSet = function(){
					if(typeof xhr.abort == 'function') xhr.abort(); // do not go further if not already loaded !
				}
				
				value.done(function(blob){
					if(id!=cnt) return;
					set(blob);
				});
				
				return;
			}
			
			
			if(!v || v instanceof Blob){
				if(change(v)){
					$removeBtn.show();
					$defaultImg.hide();
					
					if(v instanceof File){
					
						var reader = new FileReader();
						
						reader.onload = function () {
							if(id!=cnt) return;
							$preview.attr('src',reader.result).show();
						}
						
						$meta.append(
							'<div class="f-image-meta-name">'+v.name+'</div>',
							'<div class="f-image-meta-size">'+EThing.utils.sizeToString(v.size)+'</div>'
						).show();
						
						reader.readAsDataURL(v);
					}
					else if(v instanceof Blob){
						var urlCreator = window.URL || window.webkitURL;
						var imageUrl = urlCreator.createObjectURL( v );
						$preview.attr('src',imageUrl).show();
					}
				}
			}
			else
				set();
			
		}
		
		$browseBtn.click(function(){
			$fileSelector.click();
			return false;
		});
		
		$removeBtn.click(function(){
			set();
		});
		
		Form.StandardItem.call(this,$.extend(true,{
			input: function(){
				var $cntr = $('<div class="f-image thumbnail">'),
					$drop = $('<span class="glyphicon glyphicon-download" aria-hidden="true"></span>');
				
				$fileSelector.change(function(){
					var file = $(this)[0].files[0];
					if(file)
						set(file);
				});
				
				if(this.options.accept)
					$fileSelector.attr('accept',this.options.accept);
				
				
				var collection = $();

				$cntr.on('dragenter', function(e) {
				  if (collection.length === 0) {
					$cntr.addClass('f-image-drop');
					
				  }
				  collection = collection.add(e.target);
				});

				$cntr.on('dragleave drop', function(e) {
				  collection = collection.not(e.target);
				  if (collection.length === 0) {
					$cntr.removeClass('f-image-drop');
				  }
				});
				
				$cntr.on('dragover', function(e) {
					e.preventDefault(); // Cancel drop forbidding
					e.stopPropagation();
					return false;
				});
				
				$cntr.on('drop', function(e) {	
					if(e.originalEvent.dataTransfer){
						var dataTransfer = e.originalEvent.dataTransfer;
					   if(dataTransfer.files.length == 1) {
							// Stop the propagation of the event
							e.preventDefault();
							e.stopPropagation();
							
							// fetch FileList object
							var file = dataTransfer.files[0];

							if(/^image\//.test(file.type))
								set(file);
							else
								self.setError('Only image is accepted');
					   }
					}
					return false;
				});
				
				$cntr.append(
					$defaultImg,
					$preview.hide(),
					$meta,
					$('<div class="f-image-btns">').append($browseBtn,$removeBtn.hide())
				);
				
				return $cntr;
			},
			set: function($input,v){
				set(v);
			},
			get: function($input){
				// returns the content of the file as a File/Blob object
				if(!value)
					throw "Please select a file";
				
				return $.when(value).then(function(blob){
					return (typeof self.options.transform == 'function') ? self.options.transform.call(self, blob) : blob;
				});
			}
		},{
			onChange: null, // is fired every time a new set of files have been selected function(Blob)
			transform: null, // function(File) -> newContent
			accept: 'image/*' // The accept attribute specifies the types of files that is accepted (default : 'image/*' )
		},opt));
		
	}
	inherits(Form.Image,Form.StandardItem);
	
	
	Form.Checkbox = function(opt){
		
		var options = $.extend(true,{
			description: null,
			label: null,
			name: '',
			value: false, // initial value
			onChange: null
		},opt);
		
		Form.Item.call(this,options);
		
		var self = this,
			$cb = $('<input type="checkbox">');
		
		this.$element.addClass("form-group").append(
			options.description ? $('<p class="f-description">').html(options.description) : null,
			options.label ? (options.label+' ') : null,
			$cb
		);
		
		this.$cb = $cb;
		
		$cb.change(function(){
			var state = $cb.prop('checked');
			if(typeof options.onChange == 'function')
				options.onChange.call(self, state);
		});
		
		// beautiful bootstrap switch
		dependency.require(function(){
			$cb.bootstrapToggle({
				size: 'mini'
			});
		});
		
		this.onload(function(){
			self.setValue(options.value);
		});
		
	}
	inherits(Form.Checkbox,Form.Item);
	
	Form.Checkbox.prototype.getValue = function(){
		return this.$cb.prop('checked');
	};
	Form.Checkbox.prototype.setValue = function(v){
		var current = this.$cb.prop('checked');
		v = !!v;
		if(current != v)
			this.$cb.prop('checked',v).change();
	};
	
	
	/*
	* FieldsEnabler
	* 
	* options:
	*  item : <Form.Item>
	*  label: <string>
	*  value: <boolean>
	*/
	Form.FieldsEnabler = function(opt){
		var self = this;
		
		if(!$.isPlainObject(opt) || typeof opt.item == 'undefined')
			opt = {
				item: opt
			};
		
		var options = $.extend(true,{
			item: null
		},opt);
		
		Form.Item.call(this,options);
		
		var item = options.item;
		
		this.$element.addClass('f-fieldsenabler');
		
		var self = this;
		
		this.cb = new Form.Checkbox($.extend(true,{},options,{
			onChange: function(state){
				self.enable = state;
				
				// hide item
				item.$element.toggle(self.enable);
				
				if(typeof self.options.onChange == 'function')
					self.options.onChange.call(self,state);
			}
		}));
		
		this.cb.setParent(this);
		item.setParent(this);
		
		item.on('error-state-changed.f',function(evt,item,message){
			// propagate
			self.setError(message);
		});
		
		this.$element.append(
			this.cb.$element,
			item.$element.hide() // default state is false
		);
		
		this.item = item;
		
		
		
	}
	inherits(Form.FieldsEnabler,Form.Item);
	
	Form.FieldsEnabler.prototype.setValue = function(v){
		this.item.setValue(v);
		this.cb.setValue(true); // enable it !
	};
	Form.FieldsEnabler.prototype.validate = function(){
		if(this.enable)
			return this.item.validate();
	};
	
	
	
	Form.Select = function(opt){
		var self = this;
		
		opt = opt || {};
		
		var items = {};
		if(Array.isArray(opt.items))
			for(var i=0; i<opt.items.length; i++)
				items[ opt.items[i] ] = opt.items[i];
		else if($.isPlainObject(opt.items))
			items = $.extend({},opt.items);
		
		var onChange = opt.onChange;
		
		delete opt.items;
		delete opt.onChange;
		
		var defaultValue = opt.defaultValue;
		
		if((typeof opt.defaultKey == 'string') && (opt.defaultKey in items))
			defaultValue = items[opt.defaultKey];
		
		
		Form.StandardItem.call(this,$.extend(true,{
			input: items,
			on: {
				'change': function(){
					var value = this.getValue();
					if(typeof onChange == 'function')
						onChange.call(self,value);
				}
			},
			onload: function($input){
				$input.change();
			},
			value: defaultValue
		},opt));
	}
	inherits(Form.Select,Form.StandardItem);
	
	Form.Select.prototype.addItem = function(label, value){
		var $select = this.input();
		$select.append( '<option '+(typeof value != 'undefined' ? ('value="'+value+'"') : '')+'>'+label+'</option>' );
	}
	
	
	
	
	/*
	* SelectPanels
	* 
	* options:
	*  items : [{name: <string>, item: <Form.Item>}]
	*  label: <string>
	*  value: <string>
	*/
	Form.SelectPanels = function(opt){
		
		var options = $.extend(true,{
			onChange: null,
			label: null,
			name: null
		},sanitizeLayoutOptions(opt));
		
		var items = [];
		if(Array.isArray(options.items))
			items = options.items;
		else if($.isPlainObject(options.items))
			for(var i in options.items){
				items.push({
					name: i,
					item: options.items[i]
				});
			}
		
		options.items = [], options.itemsOptions = [];
		
		for(var i=0; i<items.length; i++){
			var name = items[i].name,
				item = items[i].item;
			
			options.items.push(item);
			options.itemsOptions.push({
				name: name
			});
		}
		
		
		
		this.$element = $('<div>').addClass('f-selectpanels');
		this.$content = $('<div>');
		
		var self = this, label = options.label===false ? false : (options.label || options.name);
		
		this.select = new Form.Select({
			items: [],
			value: options.value,
			onChange: function(value){
				
				var selectedItem = self.getItemByValue(value);
				
				// hide every items except the selected one
				self.items().forEach(function(item){
					item.$element.toggle(item === selectedItem);
				});
				
				if(typeof self.options.onChange == 'function')
					self.options.onChange.call(self,selectedItem);
			}
		});
		
		this.select.setParent(this);
		
		this.$element.append(
			$('<div class="form-group">').append(
				label ? ('<label>'+label+'</label>') : null,
				this.select.$element
			),
			this.$content
		);
		
		
		Form.Layout.call(this,options);
	}
	inherits(Form.SelectPanels,Form.Layout);
	
	Form.SelectPanels.prototype.update = function(){
		this.select.input().change();
	}
	Form.SelectPanels.prototype.addItem = function(item,options){
		
		item = Form.Layout.prototype.addItem.call(this,item, options);
		
		this.select.addItem(options.name);
		
		this.$content.append( item.$element.hide() );
		
		return item;
	}
	Form.SelectPanels.prototype.getItemByValue = function(value){
		var items = this.items();
		for(var i=0; i<items.length; i++){
			var options = this.getItemOptions(i);
			if(options.name === value)
				return items[i];
		}
	}
	Form.SelectPanels.prototype.getSelectedValue = function(){
		return this.select.getValue();
	}
	Form.SelectPanels.prototype.getSelectedItem = function(){
		return this.getItemByValue(this.getSelectedValue());
	}
	Form.SelectPanels.prototype.setValue = function(v){
		this.select.setValue(v.type);
		var item = this.getItemByValue(v.type);
		if(item)
			item.setValue( (typeof v.value == 'undefined') ? v : v.value );
	};
	Form.SelectPanels.prototype.validate = function(){
		
		// validate all the items
		var selectedValue = this.getSelectedValue(),
			item = this.getItemByValue(selectedValue),
			prop = {
				type: selectedValue
			},
			dfr = $.Deferred(), promises = [], self = this;
		
		if(item){
			$.when(item.validate()).done(function(value){
				if($.isPlainObject(value))
					$.extend(true,prop,value);
				else if(typeof value != 'undefined')
					prop.value = value;
				dfr.resolveWith(self,[prop]);
			}).fail(function(e){
				dfr.rejectWith(self,[e]);
			});
		};
		
		return dfr.promise();
	};
	
	
	
	
	
	
	
	
	
	
	/**
	*
	* Validators
	*
	**/
	Form.validator = {};
	
	Form.validator.NotEmpty = function(value){
		var t = false, typeof_ = typeof value;
		
		if(typeof_ == 'string' || Array.isArray(value))
			t = value.length > 0;
		else if(typeof_ == 'number')
			t = !isNaN(value);
		else 
			t = !(value === null || value === {} || typeof_ == 'undefined');
		
		if(!t)
			throw 'The value must not be empty';
	}
	
	Form.validator.RegExp = function(regexp){
		return function(value){
			return (typeof value == 'string') ? regexp.test(value) : false;
		};
	}
	
	
	
	
	
	
	
	
	
	
	
	
	
	/* register as a plugin in jQuery */
	if (window.jQuery)
		window.jQuery.addPlugin('Form',Form);

	
	
})();
 
/* @file: src\ui\modal.js */ 
(function(){
	
	if(!window.jQuery.fn.modal){
		console.error('bootstrap.js not loaded ! Needed for the modal plugin.');
		return;
	}
	
	var $ = window.jQuery,
		BsModal = $.fn.modal.Constructor;
	
	
	
	/*
	 * Enable Overlapping modals
	 * see : https://github.com/twbs/bootstrap/issues/15260
	*/
	(function(Modal) {
	  var show = Modal.prototype.show;

	  Modal.prototype.show = function() {
		this.modalOpen = !this.$body.hasClass('modal-open');
		show.apply(this, arguments);
	  };

	  Modal.prototype.hideModal = function() {
		var that = this;
		this.$element.hide();
		this.backdrop(function() {
		  if (that.modalOpen) {
			that.$body.removeClass('modal-open');
		  }
		  that.resetScrollbar();
		  that.$element.trigger('hidden.bs.modal');
		});
	  };
	})(BsModal);
	
	
	var Modal = function (element, options) {
		
		var $element = $(element),
			self = this,
			id = 'modal-'+String(Math.round(Math.random()*10000)),
			hiddenModals = null,
			hasParent = $element.parent().length > 0;
		
		this.options = $.extend(true,{
			title: null,
			buttons: {},
			removeOnClose: !hasParent, // destroy element on close
			size: null
		},BsModal.DEFAULTS, {
			backdrop: 'static'
		}, $element.data(), options);
		
		
		if(!$element.is('.modal')){
			
			// the element represent the body of the modal dialog
			var $wrapper = $(
				'<div class="modal fade">'+
					  '<div class="modal-dialog'+(this.options.size ? ' modal-'+this.options.size : '')+'">'+
						'<div class="modal-content">'+
							'<div class="modal-header">'+
								'<button type="button" class="close" data-dismiss="modal" aria-label="Close"><span aria-hidden="true">&times;</span></button>'+
								'<h4 class="modal-title"></h4>'+
							'</div>'+
							'<div class="modal-body"></div>'+
						'</div>'+
					  '</div>'+
					'</div>'
				);
			
			$wrapper.find('.modal-body').append($element);
			
			(function($p,$e){
				$p.on('show.bs.modal shown.bs.modal hide.bs.modal hidden.bs.modal loaded.bs.modal',function(e){
					$e.triggerHandler(e);
				});
			})($wrapper,$element);
			
			$element = $wrapper;
			
		}
		
		if(this.options.title){
			$element.find('.modal-title').html(this.options.title);
		}
		
		if(this.options.buttons){
			
			var $btns = []; 
			
			var createCallback = function(cb){ // if the callback return false, the modal dialog is not closed. it it returns a function, that function will be fired at the very end of the closing (after any animation or hash event)
				return function(e){
					var r = (typeof cb == 'function') ? cb.call(element) : true;
					if(r!==false){
						self.hide(r);
					}
				};
			}
			
			for(var btnName in this.options.buttons){
				var buttonOptions = this.options.buttons[btnName], $btn;
				
				if(typeof buttonOptions == 'function')
					buttonOptions = {
						handler: buttonOptions
					};
				
				if($.isPlainObject(buttonOptions) || buttonOptions===null){
					
					buttonOptions = $.extend({
						'handler': null,
						'class': null
					},buttonOptions);
					
					var extraClass = '';
					if(/^\+/.test(btnName)){
						extraClass += " btn-primary";
						btnName = btnName.substr(1);
					}
					else if(/^\!/.test(btnName)){
						extraClass += " btn-warning";
						btnName = btnName.substr(1);
					}
					else
						extraClass += " btn-default";
					
					$btn = $('<button type="button" class="btn '+buttonOptions['class']+extraClass+'">'+btnName+'</button>')
								.click(createCallback(buttonOptions.handler));
				}
				else
					$btn = buttonOptions;
				
				$btn.addClass('modal-btn');
				
				$btns.push($btn);
			}
			
			if($btns.length){
				var $footer = $element.find('.modal-footer');
				if(!$footer.length){
					$footer = $('<div class="modal-footer">').appendTo($element.find('.modal-content'));
				}
				$footer.addClass('btn-toolbar form-inline').append($btns);
			}
		}
		
		
		
		$element.attr('data-id',id);
		
		BsModal.call(this, $element[0], this.options);
		
		// events
		var isHidden = false;
		this.epilogFct = null;
		var epilog = function(){
			// this function is executed at the very end :
			//  - after any animation
			//  - after any hash change
			
			// restore the hidden modals
			
			if(hiddenModals)
				hiddenModals.show();
			
			if(typeof self.epilogFct == 'function'){
				self.epilogFct.call(element);
				self.epilogFct = null;
			}
		}
		
		var hashHandler = function(){
			// remove this modal
			if(window.location.hash.indexOf(id)==-1){ // the hash tag from this modal just disappear, hide it !
				$(window).off('hashchange', hashHandler);
				if(!isHidden){
					self.hide();
				}
				else{
					epilog();
				}
			}
		};
		
		$element.on('hidden.bs.modal', function (e) {
			isHidden = true;
			
			if(self.options.removeOnClose)
				$element.remove();
			
			if(window.location.hash.indexOf(id)>=0){
				history.back();
			}
			else{
				epilog();
			}
			
		});
		
		$element.on('shown.bs.modal', function(){
			window.location.hash += '#' + id;
			$(window).on('hashchange', hashHandler);
		});
		
		$element.on('show.bs.modal', function(){
			// if there is other modal dialog opened, just hide them
			hiddenModals = $('div.modal:visible').not('[data-id="'+self.id+'"]').hide();
		});
		
		if(this.options.show)
			this.show();
		
	}
	Modal.prototype = Object.create(BsModal.prototype);
	
	Modal.prototype.hide = function(callback){
		if(typeof callback == 'function')
			this.epilogFct = callback;
		BsModal.prototype.hide.call(this);
	}
	
	// disable the buttons
	Modal.prototype.disable = function(){
		this.$element.find('.modal-footer .modal-btn').attr('disabled','disabled');
	}
	Modal.prototype.enable = function(){
		this.$element.find('.modal-footer .modal-btn').removeAttr('disabled');
	}
	
	
	
	/* register as a plugin in jQuery */
	if (window.jQuery)
		window.jQuery.addPlugin('Modal',Modal);
	
})();
 
/* @file: src\ui\table.js */ 
(function(){
	
	
	
	/*
	events :
		- "selection.change" // is fired each time the selection change, (note: the selection is cleared when the page change or the data is reloaded
	*/
	
	var Table = function(element,opt){
		
		$.AbstractPlugin.call(this,element,$.extend(true,{
			model: null, // Model instance or array (will be converted into an ArrayModel, can be an URL pointing to JSON data)
			view: null, // View instance or options for the TableView 
			selectable: {
				enable: false, // enable selecting
				limit: 1, // limit the selection to a specific number, if 0 or null -> unlimited (for activating shift & ctrl selection, limit must be 0 or null)
				filter: null, // function(item) -> return boolean , if it returns false, this item is not selectable
				trigger: 'click', // null or 'click' only available value
				cumul: true // if true the selection is cumulative, else the selection is reset at every new selection
			},
			openable:{
				enable: true, // if the item has has children, open that children
				trigger: 'dbclick' // click or dbclick or any jquery event that are available on <tr> item
			},
			row: {
				class: null, // className(s) to be added to the table's item DOM element, multiple classname must be separated by space
				events: {}
			},
			before: null, // function, fired before the view and the model
			loaded: null, // function, fired when the browser has finished to load primary data
			error: null, // function, fired when the data could not have been loaded
			class: null, // className(s) to be added to the table DOM element, multiple classname must be separated by space
			pagination:{
				itemsPerPage: 20, // may be an array of available values [20,50,100,'all']
				enable: false // enable the pagination
			},
			sortBy: null, // can either be a string (ie: "+field" or "-field" or "field") or an object { field: "field", ascending: true|false }
			message: {
				empty: '<span class="tbl-message-warning">empty</span>',
				modelLoadError: '<span class="tbl-message-warning">error</span>',
				loading: '<span class="tbl-message-warning">loading...</span>'
			}
		},opt));
		
		var self = this;
		
		// some internal array
		this._items = [];
		this._map = [];
		
		
		
		
		// get the model
		this._model = (this.options.model instanceof Model) ? 
						this.options.model : 
						new ArrayModel( 
							(typeof this.options.model == 'string') ? 
							$.getJSON(this.options.model) : // if a string is given, assume it is an URL 
							this.options.model
						); // else must be an array
		
		
		
		
		/*
		dom building
		*/
		
		this.$element.empty().addClass('tbl').addClass(this.options.class);
		
		
		// construct the toolbar toolbar and prepend it to _$
		var hasToolbar = this.options.pagination.enable;
		if(hasToolbar){
			var $toolbar = $('<div class="tbl-toolbar toolbar btn-toolbar" role="toolbar">');
				
			// page length
			var itemsPerPage = this.options.pagination.itemsPerPage;
			if(!$.isArray(itemsPerPage))
				itemsPerPage = [itemsPerPage];
			var pageLengthTpl = (this.options.pagination.enable && itemsPerPage.length>1) ?
				'<div class="btn-group btn-group-sm" role="group" name="page-length">'+
					'<button type="button" class="btn btn-default dropdown-toggle" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">'+
						'<span><span class="glyphicon glyphicon-eye-open" aria-hidden="true"></span> <span class="value"></span></span>'+
						'<span class="caret"></span>'+
					  '</button>'+
					 '<ul class="dropdown-menu"></ul>'+
				'</div>' : null;
			
			// pagination + go to page N
			var pageSelectorTpl = this.options.pagination.enable ?
				'<div name="pagination-div" class="btn-group btn-group-sm" role="group">'+
					  '<ul class="pagination pagination-sm" style="margin:0;"></ul>'+
				'</div>'+
				'<div name="jump-div" class="btn-group btn-group-sm hidden-xs" role="group">'+
					'<div class="input-group input-group-sm" style="width:120px;">'+
					  '<input name="jump" type="number" class="form-control" placeholder="page" min="1">'+
					  '<span class="input-group-btn">'+
						'<button name="jump-btn" class="btn btn-default" type="button">Go!</button>'+
					  '</span>'+
					'</div>'+
				'</div>' : null;
			
			
			// actions
			var actionsTpl = 
				'<div class="btn-group btn-group-sm" role="group" name="actions"></div>';
			
			$toolbar
				.append(
					pageLengthTpl,
					pageSelectorTpl,
					actionsTpl
				)
				.prependTo(this.$element);
			
			
			if(pageSelectorTpl){
				var $goto = $('[name="jump-div"]',$toolbar),
					fn = function(){
						var $input = $('input',$goto),
							pageIndex = parseInt($input.val()),
							min = parseInt($input.prop('min')),
							max = parseInt($input.prop('max'));
						if(isNaN(pageIndex) || pageIndex<min || (!isNaN(max) && pageIndex>max)){
							// invalid
							$input.val(min);
							pageIndex = 1;
						}
						self.moveToPage(pageIndex-1);
					};
				
				$goto
					.find('button')
					.click(fn);
				$('input',$goto).keypress(function (event) {
					var keycode = (event.keyCode ? event.keyCode : event.which);
					if (keycode == 13) {
						fn();
						return false;
					}
				});
			}
			
			if(pageLengthTpl){
				var pageLengthItems = [];
				
				itemsPerPage.forEach(function(item){
					pageLengthItems.push(
						$('<li>')
							.attr('value',item)
							.append('<a>'+item+'</a>')
							.click(function(){
								self.setItemsPerPage(item);
							})
					);
				});
			
				$('[name="page-length"]',this.$element)
					.find('ul')
					.append(pageLengthItems);
			}
			
		}
		
		
		// initialize the view
		this._view = (this.options.view instanceof View) ? this.options.view : new TableView(this.options.view);
		this._$view = $('<div class="view">').appendTo(this.$element);
		
		
		
		
		
		
		// init pagination
		if(this.options.pagination.enable){
			this._setItemsPerPage($.isArray(this.options.pagination.itemsPerPage) ? this.options.pagination.itemsPerPage[0] : this.options.pagination.itemsPerPage);
			this._index = 0;
		}
		
		
		if($.isFunction(this.options.before))
			this.options.before.call(self);
		
		// once the model is ready ...
		
		this._loader();
		
		$.when(
			this.model().init(self)
		).done(function(){
			
			// the model is ready now !
			
			
			
			if(self.options.sortBy){
				if(typeof self.options.sortBy == 'string')
					self.sort(self.options.sortBy,null,true);
				else
					self.sort(self.options.sortBy.field,self.options.sortBy.ascending,true);
			}
			
			// Initialize the view only after the model was initialized
			
			$.when( self.view().init(self._$view, self) ).done(function(){
				
				// load the data from the model
				self
					.open()
					.done(function(){
						
						if($.isFunction(self.options.loaded))
							self.options.loaded.call(self);
						
						setTimeout(function(){
							self.$element.trigger('load');
						},1);
					});
					
			});
		});
		
	}
	Table.prototype.model = function(){
		return this._model;
	}
	Table.prototype.view = function(){
		return this._view;
	}
	Table.prototype.items = function(){
		return this._items;
	}
	Table.prototype.selection = function(){
		var s = [];
		this._map.forEach(function(meta,i){
			if(meta.selected)
				s.push(this._items[i]);
		},this);
		return s;
	}
	Table.prototype._itemToIndex = function(item){
		var index;
		if(typeof item == 'function'){
			index = this._map.filter(function(meta,i){
				return item.call(this,this._items[i],meta.index);
			},this).map(function(meta){
				return meta.index;
			});
		}
		else if(Array.isArray(item)){
			index = item.map(function(e){
				return this.model().index(e);
			},this);
		}
		else if( typeof item != 'undefined')
			index = this.model().index(item);
		return index;
	}
	
	// index might be a function(item) -> return Boolean to select the elements that match some criteria
	// or an index used by the Model.index(item) function
	// returns true if there was a change
	Table.prototype.select = function(item){
		var selectable = this.options.selectable;
			
		if(!selectable.enable) return false;
		
		// remove previous selection
		this._select(this._itemToIndex(this.selection()), false, true);
		
		return this._select(this._itemToIndex(item) , true);
	}
	// index = model index !
	// table.selectByIndex(table.model().index(item)) <=> table.select(item)
	Table.prototype.selectByIndex = function(index){
		var selectable = this.options.selectable;
			
		if(!selectable.enable) return false;
		
		return this._select(index , true);
	}
	// the next function is for internal purpose only !
	// returns true only if there was a state change
	// index must be the one used by the model and stored in this._map[].index
	// if trigger == true, an event will be triggered on change only
	Table.prototype._select = function(index,state,notrigger){
		state = !!state;
		
		if($.isArray(index)){
			var change = false;
			index.forEach(function(si){
				if(this._select(si,state,true))
					change = true;
			},this);
			
			if(change && !notrigger)
				this.$element.trigger('selection.change');
			
			return change;
		}
		
		if(typeof index == 'undefined')
			return false;
		
		var i = this._indexToPosition(index),
			item = this._items[i],
			meta = this._map[i];
		
		// match the filter ?
		var filter = this.options.selectable.filter;
		if(i!=-1 && (!$.isFunction(filter) || filter.call(this,item,index))){
			
			var currentState = meta.selected;
			if(currentState != state){ // else nothing to do ! already in that state
				
				if(state){
					// check if the selection limit is reached
					var limit = this.options.selectable.limit;
					if(limit>0){
						var selectionLength = 0, firstSelectedIndex;
						this._map.forEach(function(meta,i){
							if(meta.selected){
								if(selectionLength==0)
									firstSelectedIndex = meta.index;
								selectionLength++;
							}
						},this);
						if(selectionLength >= limit){
							// limit reached
							if(limit>1)
								// do not check that item
								state = false;
							else
								// uncheck the previous one only if limit===1
								this._select(firstSelectedIndex,false);
						}
					}
				}
				
				// update the state
				meta.selected = state;
				
				// update the dom
				var $item = meta.$item;
				if(state)
					$item.addClass('selected');
				else
					$item.removeClass('selected');
				// update the view
				this.view().setSelectState($item,state);
				
				
				if(currentState != state){
					
					if(!notrigger)
						this.$element.trigger('selection.change');
					
					return true;
				}
			}
			
		}
		
		return false;
	}
	// internal use only, add ctr & shift feature on user selection
	Table.prototype._selectExtended = function(e,index,state){
		var i = this._indexToPosition(index),
			ctrlAndShiftSelectionEnable = !this.options.selectable.limit;
		
		// enable selecting multiple rows with the shift key
		if(e.shiftKey && ctrlAndShiftSelectionEnable){// to enable that feature, there must be no limit for the selection
			
			var selection = this._map.filter(function(meta){
				return meta.selected;
			});
			
			if(selection.length>0){
				var positionEnd = i,
					positionStart = this._indexToPosition(selection.length>1 ? this._selectSrc : selection[0].index);
				
				if(positionStart>positionEnd){
					positionEnd = positionStart;
					positionStart = i
				}
				
				this._select(this._map.filter(function(m,i){
					return i>=positionStart && i<=positionEnd;
				}).map(function(m){
					return m.index;
				}),true);
				
				this._selectType = 'shift';
				
				return;
			}
			
		}
		
		if(!this.options.selectable.cumul && !(e.ctrlKey && ctrlAndShiftSelectionEnable)){
			// remove previous selection
			this._select(this._map.filter(function(meta){
				return meta.selected;
			}).map(function(m){
				return m.index;
			}),false,true);
		}
		
		this._selectSrc = index;
		this._select(index,state);
	}
	Table.prototype.open = function(parent){
		
		var model = this.model(),
			view = this.view(),
			self = this;
		
		this._parent = parent || null;
		
		// reset the items
		var hasItemSelected = this.selection().length;
		this._items = [];
		this._map = [];
		if(hasItemSelected)
			this.$element.trigger('selection.change'); // the selection was lost
		
		
		this._loader();
		
		return $.when( model.data(this._parent, this._index, this._itemsPerPage) )
			.done(function(items){
				
				self._items = items || [];
				
				// pagination : if we do not know the total number of rows, ask the model !
				if(self.options.pagination.enable && !self._length){
					self._length = model.rows();
					self._updatePagination();
				}
				
				self._loader(false);
				
				self._update();
				
			})
			.fail(function(e){
				
				self._message(typeof self.options.message.modelLoadError == 'function' ? self.options.message.modelLoadError.call(self,e) : self.options.message.modelLoadError);
				
				if(typeof self.options.error == 'function')
					self.options.error.apply(self,arguments);
			})
		
	}
	Table.prototype._indexToPosition = function(index){
		for(var i=0; i<this._map.length; i++)
			if(this._map[i].index === index)
				return i;
	}
	Table.prototype._loader = function(enable){
		this._message(enable===false ? null : (typeof this.options.message.loading == 'function' ? this.options.message.loading.call(this) : this.options.message.loading));
	}
	Table.prototype._message = function(message){
		if(message===null){
			if(this._$notify)
				this._$notify.hide();
			this._$view.show();
		}
		else {
			if(!this._$notify){
				this._$notify = $('<div>').addClass('tbl-notify');
				this._$view.after(this._$notify);
			}
			this._$notify.html(message).show();
			this._$view.hide();
		}
	}
	Table.prototype._update = function(){
		
		var rowClass = (this.options.row || {}).class,
			rowEvents = (this.options.row || {}).events,
			selectable = this.options.selectable || {},
			selectOnClick = (typeof selectable.trigger == 'string' && selectable.trigger.indexOf('click')>=0),
			openable = this.options.openable || {},
			model = this.model(),
			view = this.view(),
			self = this;
		
		view.clear();
		
		this._map = []; // it map some state/relation information to the index
		/*
		{
			$item: jquery dom element (from the view)
			index: can be anything, given by the Model.index() function, but is unique in the items collection
			selected: boolean
		}
		*/
		
		if(this._items.length==0){
			this._message(typeof this.options.message.empty == 'function' ? this.options.message.empty.call(this) : this.options.message.empty);
			return;
		}
		
		this._items.forEach(function(item,i){
			
			var index = model.index(item);
			
			// create the item in the view
			var $tr = view.createItem(item, index);
			
			$tr.attr('data-role','item');
			$tr.addClass(rowClass);
			
			if(index===null)
				index = i; // if the modal have no index, a default one is given corresponding of the position of the item in the collection
			
			this._map.push({
				$item: $tr,
				index: index,
				selected: false
			});
			
			// user events (first so the user event can cancel default event)
			for(var event in rowEvents)
				$tr.on( event , {
					item: item,
					index: index
				}, rowEvents[event] );
			
			// selection
			if(selectable.enable){
				var itemSelectable = $.isFunction(selectable.filter) ? selectable.filter.call(this,item,index) : true;
				if(selectOnClick && itemSelectable)
					$tr.on( 'click' , function(e){
						self._selectExtended(e,self._map[i].index,!self._map[i].selected); // toggle
					});
			}
			
			// openable ?
			if(openable.enable && model.hasChildren(item)){
				$tr.on( openable.trigger , function(){
						self.open(item);
					});
			}
			
			
			
			
			
			// data
			$tr.data('table',this);
			$tr.data('item',item);
			
			
		},this);
		
		this.$element.trigger('redraw');
		
	}
	
	Table.prototype.destroy = function(){
		this.$element.empty().removeClass('tbl').removeClass(this.options.class);
		
		this.$element.trigger('destroy');
	}
	// if sens==true, ascending order, else descending order
	// if sens is ommited, then its default value is true (ascending order)
	// if sens is ommited and field start with '+', then the sort will be in ascending order (ie: +field)
	// if sens is ommited and field start with '-', then the sort will be in descending order (ie: -field)
	Table.prototype.sort = function(field, sens, __noUpdate){ // the third parameter is for internal use only
		if(typeof field != 'string' || !/^[+-]?.+$/.test(field))
			return;
		
		if(typeof sens == 'undefined' || sens === null)
			sens = !/^\-/.test(field);
		
		field = field.replace(/^[+-]?/,'');
		
		
		this._sortedBy = (sens ? '+' : '-') + field;
		this.model().sort(field,sens);
		if(__noUpdate!==true)
			this.open(this._parent);

	}
	Table.prototype.sortedBy = function(){
		return this._sortedBy;
	}
	Table.prototype.reload = function(){
		return this.open(this._parent);
	}
	
	// pagination
	
	// pageIndex starts from 0
	// pageIndex === '+1' -> go to next page
	// pageIndex === '-1' -> go to previous page
	Table.prototype.moveToPage = function(pageIndex){
		var self = this;
		if(this.options.pagination.enable){
			
			if(typeof pageIndex == 'string'){
				var currentPage = Math.floor((this._index || 0) / this._itemsPerPage);
				currentPage += parseInt(pageIndex);
				return this.moveToPage(currentPage);
			}
			
			if(pageIndex<0)
				pageIndex = 0;
			
			this._index = (pageIndex || 0 )* this._itemsPerPage;
			
			this._updatePagination();
			
			// reload !
			this.open(this._parent);
			
		}
	}
	Table.prototype.setItemsPerPage = function(itemsPerPage){
		if(this.options.pagination.enable){
			
			this._setItemsPerPage(itemsPerPage);
			
			// reload
			this.moveToPage(0);
			
		}
	}
	Table.prototype._setItemsPerPage = function(itemsPerPage){
		
		if(typeof itemsPerPage == 'string' && /^all$/i.test(itemsPerPage))
			this._itemsPerPage = null;
		else if(typeof itemsPerPage == 'number' && itemsPerPage>0)
			this._itemsPerPage = itemsPerPage;
		
		var $epp = $('[name="page-length"]',this.$element);
		
		$epp.find('.value').html(itemsPerPage);
		
		$epp
			.find('li')
			.removeClass('selected')
			.filter('[value="'+(this._itemsPerPage || 'all')+'"]')
			.addClass('selected');
	}
	Table.prototype.numberOfPage = function(){
		return (this.options.pagination.enable && this._itemsPerPage !== null) ? (this._length>0 ? Math.ceil(this._length/this._itemsPerPage) : null) : 1;
	}
	Table.prototype.currentPage = function(){
		return this._itemsPerPage ? Math.floor(this._index / this._itemsPerPage) : 0;
	}
	// internal use only 
	Table.prototype._updatePagination = function(){
		if(this.options.pagination.enable){
			
			// update the toolbar
			
			var self = this,
				nbPage = this.numberOfPage(),
				currentPage = this.currentPage(); // start from 0
			
			var $goto = $('[name="jump-div"]',this.$element),
				$navigator = $('[name="pagination-div"]',this.$element);
			
			if(nbPage===1){
				// only one page ! so do not show the pagination controls
				$goto.hide();
				$navigator.hide();
			}
			else {
			
				if(nbPage) // the number of page is known
					$goto
						.find('input')
						.attr('max',nbPage);
				else
					$goto
						.find('input')
						.removeAttr('max');
				
				
				var $ul = $navigator
					.find('ul')
					.empty();
				
				var hasNext = !nbPage || (currentPage+1 < nbPage),
					hasPrev = (currentPage > 0),
					maxItem = 3; // must be odd
					
				if(hasPrev)
					$('<a aria-label="Previous"><span aria-hidden="true">&laquo;</span></a>')
						.click(function(){
							self.moveToPage('-1');
						})
						.appendTo($ul)
						.wrap('<li>');
				
				var nbNext = nbPage ? (nbPage - 1 - currentPage) : 0,
					half = Math.floor(maxItem/2),
					decal = nbNext >= half ? 0 : (nbNext-half),
					pageIndex = currentPage /*+ 1*/, // start from 1
					indexes = [];
				for(var i=-half+decal+pageIndex, j=0; j<maxItem && i<=(nbPage?(nbPage-1):pageIndex); i++){
					if(i>=0){
						indexes.push(i);
						j++;
					}
				}
				indexes.forEach(function(i){
					$('<a>'+(i+1)+'</a>')
						.click(function(){
							self.moveToPage(i);
						})
						.appendTo($ul)
						.wrap('<li '+(pageIndex==i?'class="active"':'')+'>');
				},this);
				
				if(hasNext)
					$('<a aria-label="Next"><span aria-hidden="true">&raquo;</span></a>')
						.click(function(){
							self.moveToPage('+1');
						})
						.appendTo($ul)
						.wrap('<li>');
				
				

				// show pagination's controls
				$goto.show();
				$navigator.show();
			
			}
			
			
		}
		
	}
	
	
	
	
	
	
	
	/*
	  Model interface
	*/
	
	var Model = function() {}
	// init the model, may return a deferred object for asynchronous init model, or nothing else
	// override this for asynchronous model initialization
	Model.prototype.init = function(tableInstance){}
	// return the keys/columns
	Model.prototype.keys = function(){
		return [];
	}
	// return the number of rows, null if not known
	Model.prototype.rows = function(){
		return null;
	}
	// return the items
	// offset and length are used for pagination
	// may return a jquery deferred object if the processus is asynchronous
	Model.prototype.data = function(parent, offset, length){
		// parent is null if root
		// an item must be an object
		// the property '__index' must be set with a unique identifier representing the item (for table model, it can be an integer index)
		return [];
	}
	// check if an item has children or not (tree model may have)
	Model.prototype.hasChildren = function(item){
		return false;
	}
	// sort the data
	Model.prototype.sort = function(field, ascending){}
	// return a unique index identifying an items according to the data given in argument
	// if null returned, a default index will be assigned corresponding to the position of the item in the collection
	Model.prototype.index = function(item){
		return null;
	}
	
	
	Table.Model = Model;
	
	
	
	/*
	ArrayModel
	*/
	
	// items must be an array or a jquery deferred object !
	var ArrayModel = function(items) {
		
		var self = this,
			setData = function(data){
				self._items = Array.isArray(data) ? data : [];
				self._type = self._items.length ? (typeof self._items[0]) : 'undefined';
				if(self._type == 'undefined')
					self._items = []; // make an array of undefined unvalid
			};
		
		setData(items);
		
		
		// deferred object given ?
		this._deferred = null;
		if(typeof items == 'object' && !Array.isArray(items)){
			this._deferred = items;
			this._deferred.done(setData);
		}
		
		
		Model.call(this);
	}
	ArrayModel.prototype = Object.create(Model.prototype);
	
	// execute the callback when the model is ready (ie: the keys are known)
	ArrayModel.prototype.init = function(){
		return this._deferred ? this._deferred : null;
	}
	
	// return the keys/columns
	ArrayModel.prototype.keys = function(){
		switch(this._type){
			case 'object':
				return Object.keys(this._items[0]).filter(function(k){
					return !/^__/.test(k); // skip the key starting with '__' (double underscores)
				});
			case 'number':
			case 'function':
			case 'boolean':
			case 'string':
				return ['value'];
			default:
				return [];
		}
	}
	// return the number of rows, null if not known
	ArrayModel.prototype.rows = function(){
		return this._items.length;
	}
	// return the items
	// offset and length are used for pagination
	ArrayModel.prototype.data = function(parent, offset, length){
		// parent is null if root
		// an item must be an object
		// the property '__index' may be set with a unique identifier representing the item (for table model, it can be an integer index)
		offset = offset||0;
		return length ? this._items.slice(offset,offset+length) : this._items.slice(offset);
	}
	// sort the data
	ArrayModel.prototype.sort = function(field, ascending){
		if(this._type == 'object')
			this._items.sort(function(a, b){
				a = typeof a.field == 'function' ? a.field() : a.field;
				b = typeof b.field == 'function' ? b.field() : b.field;
				if(a < b) return -1;
				if(a > b) return 1;
				return 0;
			});
		else if(this._type == 'function')
			this._items.sort(function(a, b){
				a = a();
				b = b();
				if(a < b) return -1;
				if(a > b) return 1;
				return 0;
			});
		else
			this._items.sort();
		
		if(!ascending)
			this._items.reverse();
	}
	// return a unique index identifying an items according to the item given in argument
	ArrayModel.prototype.index = function(item){
		return this._items.indexOf(item);
	}
	
	
	Table.ArrayModel = ArrayModel;
	
	
	
	
	/*
	* View
	*/
	var View = function() {}
	// init the view, may return a deferred object for asynchronous init view, or nothing else
	// the first parameter is the container (jQuery object) where to build the view
	// table : the parent table
	View.prototype.init = function($container, table){
		// the next line is important if you do not override the View.prototype.$ function.
		this.$ = function(){
			return $($container);
		};
		this.table = function(){
			return table;
		};
	}
	// clear all items in the view
	View.prototype.clear = function(){}
	// create a new item into the view
	View.prototype.createItem = function(item,index){}
	// update the select state of an item
	View.prototype.setSelectState = function($item, checked){}
	
	
	Table.View = View;
	
	
	
	var TableView = function(opt) {
		
		View.call(this);
		
		this.options = $.extend(true,{
			header: {
				enable: true // make the header visible or not !
			},
			selectable: {
				check: false // enable selecting rows with a checkbox
			},
			fields: {}, // field option, see below for details
			showOnlySpecifiedField: false // if set, only the fields set in 'fields' will be show (ie: white list)
		},opt);
		
		this._fields = {};
		
		
	}
	TableView.prototype = Object.create(View.prototype);
	
	TableView.prototype.init = function($container, table){
		
		View.prototype.init.call(this,$container,table);
		
		// checkable column
		var selectable = table.options.selectable;
		if(selectable.enable && this.options.selectable.check){
			// prepend a special field '__check'
			this._fields['__check'] = {
				label:'',
				get: function(item,index){
					var itemSelectable = $.isFunction(selectable.filter) ? selectable.filter.call(table,item) : true;
					if(itemSelectable){
						// check for a limitation
						return $('<input type="checkbox" data-role="select"/>').on('change',function(e){
							// on checkbox change
							table._selectExtended(e,index,$(this).prop("checked"));
							// do not fire the row's click event
							e.preventDefault();
							return false;
						});
					}
					return null;
				}
			};
		}
		
		
		/*
		fields management (the model must be ready !)
		*/
		
		$.extend(true,this._fields,this.options.fields);
		
		// set default fields
		if(!this.options.showOnlySpecifiedField)
			table.model().keys().forEach(function(field){
				if(!this._fields.hasOwnProperty(field))
					this._fields[field] = {};// defaults will be set just below
			},this);
		for(var i in this._fields){
			this._fields[i] = $.extend({
				label: i, // displayed name of that field
				get: null, // function(item) -> return value
				formatter: null, // function(value) -> return String
				enable: true, // show/hide this field
				default: null, // default value
				class : null, // className(s) to be added to the td/th DOM element for this field, multiple classname must be separated by space
				hidden: false,
				event: null // object, used to attach event on a TD dom element
			},this._fields[i]);
		}
		
		
		/*
		* DOM
		*/
		
		$container.addClass('tableview');
		
		var fields = this._fields, self = this;
		
		this._$table = $('<table><tbody>').appendTo($container);
		this._$tbody = $('tbody',this._$table);
		
		// set the index, internal usage only, todo : make it private ? (used in setVisible())
		this._index = {};
		var coln = 0;
		$.each(fields,function(field,fieldOptions){
			if(fieldOptions.enable)
				self._index[field] = coln++;
		});
		
		var sortedBy = table.sortedBy(), sortField, sortSens;
		if(sortedBy){
			sortField = sortedBy.replace(/^[-+]?/,'');
			sortSens = !/^\-/.test(sortedBy);
		}
		
		// update the DOM header element
		$('thead',this._$table).remove();
		if(this.options.header.enable){
			var $thead = $('<thead>').prependTo(this._$table),
				$tr = $('<tr>');
			
			$.each(fields,function(field,fieldOptions){
				if(fieldOptions.enable){
					var $th = $('<th>');
					$th
						.html(fieldOptions.label)
						.addClass(fieldOptions.class);
					
					if(field!="__check"){ // make all the field sortable except the special '__check' field 
						$th
							.addClass('sortable')
							.on('click',function(){
								var $this = $(this),
									ascending = !Boolean($this.data('ascending'));
								$this.data('ascending',ascending);
								table.sort(field,ascending);
								
								// update the header
								$('th',$thead).each(function(){
									var $this = $(this);
									$this
										.removeClass('sort-asc sort-desc');
								});
								
								$this.addClass(ascending ? 'sort-asc' : 'sort-desc');
							});
						
						if(sortField === field)
							$th.addClass(sortSens ? 'sort-asc' : 'sort-desc');
					}
					
					if(fieldOptions.hidden)
						$th[0].style.display = "none";
					
					$th.data('field',field);
					
					$tr.append($th);
				}
			});
			
			$tr.appendTo($thead);
			
		}
	}
	TableView.prototype.clear = function(){
		this._$tbody.empty();
	}
	TableView.prototype.createItem = function(item,index){
		// construct the item dom element
		var $tr = $('<tr>');
		
		for(var field in this._fields){
			var fieldOptions = this._fields[field];
			if(fieldOptions.enable){
				var value = $.isFunction(fieldOptions.get) ? fieldOptions.get.call(this,item,index) : (
						(typeof item[field] != 'undefined') ? 
						($.isFunction(item[field]) ? item[field]() : item[field])
						: (fieldOptions.default===null ? "" : fieldOptions.default)
					);
				
				if($.isFunction(fieldOptions.formatter))
					value = fieldOptions.formatter.call(this,value);
				
				
				var $td = $('<td>');
				
				$td
					.html( value )
					.addClass(fieldOptions.class);
				
				if(fieldOptions.hidden)
					$td[0].style.display = "none";
				
				if(typeof fieldOptions.events == 'object')
					for(var eventName in fieldOptions.events){
						$td.on(eventName,{
							item: item
						},fieldOptions.events[eventName]);
					}
				
				$tr.append($td);
			}
		}
		
		this._$tbody.append($tr);
		
		return $tr;
	}
	TableView.prototype.setSelectState = function($item, checked){
		// check the checkbox (if any)?
		$('input[data-role="select"]',$item)
			.prop("checked",checked);
	}
	TableView.prototype.setVisible = function(field, show){
		if(this._fields.hasOwnProperty(field) && this._fields[field].enable){
			// update the view
			// get the index of the column
			var index = this._index[field] + 1; // start from 1
			// hide/show it !
			var $col = $("thead tr th:nth-child("+index+"), tbody tr td:nth-child("+index+")",this._$table);
			$col.toggle(Boolean(show));
			
			// save the state
			this._fields[field].hidden = !show;
		}
	}
	TableView.prototype.hide = function(field){
		this.setVisible(field,false);
	}
	TableView.prototype.show = function(field){
		this.setVisible(field,true);
	}
	TableView.prototype.isVisible = function(field){
		return this._fields.hasOwnProperty(field) && this._fields[field].enable && !this._fields[field].hidden;
	}
	
	
	Table.TableView = TableView;
	
	
	/* register as a plugin in jQuery */
	if (window.jQuery)
		window.jQuery.addPlugin('Table',Table);
	

})();
 
/* @file: src\ui\browser.js */ 
(function(){
	
	var undefined;
	
	
	function inherits(extended, parent){
		extended.prototype = Object.create(parent.prototype);
	};
	
	
	
	/*
	* Browser
	*/
	
	function generateSvgResourceIcon(resource, square, style){
		var icon = {
			'File': 'F',
			'Device': 'D',
			'Table': 'T',
			'App': 'A',
			'Folder': '+',
			'Unk': '?'
		},type = typeof resource == 'string' ? resource : resource.type();
		/*return '<span class="icon-'+type+'">'+icon[type]+'</span>';
		*/
		if(!icon.hasOwnProperty(type))
			type = 'Unk';
		return '<svg class="icon-'+type+'" '+(style ? 'style="'+style+'"' : '')+' viewBox="0 0 32 32">'+(square ? '<rect x="0" y="0" width="32" height="32"/>' : '<circle cx="16" cy="16" r="16" />')+'<text x="16" y="24" font-size="22" fill="white" font-weight="bold" font-family="Arial" text-anchor="middle">'+icon[type]+'</text></svg>';
	}
	
	
	
	function Browser(dom,opt){
		
		var options = $.extend(true,{
			model:null, // will be set after
			// table options
			class: "explorer",
			view: 'Table',
			row: {
				class: 'item'
			},
			openable:{
				enable: true,
				trigger: EThing.utils.isTouchDevice ? 'click' : 'dblclick'
			},
			sortBy: '-modifiedDate'
		},opt);
		
		if(!(options.model instanceof $.Table.Model))
			options.model = new ArboModel(options.model);
			
		if(typeof options.view == 'string'){
			options.view = new Browser.Views[options.view]();
		}
		
		$.Table.call(this,dom,options);
		
		this.$element.find('table').addClass('table table-hover');
		
	}
	inherits(Browser,$.Table);
	
	Browser.prototype.pwd = function(){
		return this.model().getResource(this._parent || null);
	}
	
	
	
	
	
	var ArboModel = function(options){
		
		this._options = $.extend(true,{
			filter: null, // function(resource) -> return boolean , if it returns false, the resource is ignored
			showParentDirectoryFolder: true, // display the previous directory link, no sort is made on that item : always on top (not available if root field is an array)
			root: null // root directory, may be a EThing.Folder instance or a string of a path or an array of resources (default to null which means the root of the user system files)
		},options);
		
		
		$.Table.Model.call(this,this._options);
		
		this._sort = null; // by default, no sort is made
		
	}
	inherits(ArboModel,$.Table.Model);
	
	ArboModel.prototype.init = function(tableInstance){
		EThing.arbo.on('resource-remove resource-add',function(){
			tableInstance.reload();
		});
	}
	
	// return the keys/columns
	ArboModel.prototype.keys = function(){
		return ['name','size','modifiedDate'];
	}
	// return the number of rows, null if not known
	ArboModel.prototype.rows = function(){
		var root = this.getResource();
		return (root instanceof EThing.Folder) ? root.ls().length : ($.isArray(root) ? root.length : null);
	}
	// return the items, may be a deferred object
	// offset and length are used for pagination
	ArboModel.prototype.data = function(parent, offset, length){
		// parent is null if root
		var deferred = $.Deferred(),
			self = this;
		
		EThing.arbo.load().done(function(){
			parent = self.getResource(parent);
			
			var children = (parent instanceof EThing.Folder) ? parent.children() : ($.isArray(parent) ? parent : []);
			
			if(self._filter || self._options.filter)
				children = $.grep(children,self._filter || self._options.filter)
			
			if(self._sort)
				children.sort(self._sort);
			
			if(self._options.showParentDirectoryFolder && (parent instanceof EThing.Folder)){
				if(parent!==EThing.arbo.root()){
					var prev = new EThing.Folder({
							'name': '.. (go to parent directory)',
							'id': '____prev____'
						});
					prev._pwd = parent.parent().id();
					children.unshift(prev);
				}
			}
			
			// pagination
			if(typeof offset == 'number')
				children = children.slice(offset,length ? (offset+length) : undefined);
			
			deferred.resolve(children);
			
		}).fail(function(){
			deferred.reject();
		});
		
		return deferred.promise();
	}
	// check if an item has children or not (tree model may have)
	ArboModel.prototype.hasChildren = function(item){
		return item instanceof EThing.Folder;
	}
	// sort the data
	ArboModel.prototype.sort = function(field, ascending){
		var sortfn;
		
		if(field=="size"){
			sortfn = function(a, b) {
				return (
					isFinite(a) && isFinite(b) ?
					((ascending ? 1 : -1) * (a - b)):
					NaN
				);
			};
			// special case (mix between table length & resource size)
			this._sort = function(a,b){
				a = (typeof a.size != 'undefined') ? a.size() : (typeof a.length != 'undefined' ? a.length() : null);
				b = (typeof b.size != 'undefined') ? b.size() : (typeof b.length != 'undefined' ? b.length() : null);
				return sortfn(a,b);
			};
			return;
			
		}
		else if(field=="modifiedDate"){
			sortfn = function(a, b) {
				return (
					isFinite(a) && isFinite(b) ?
					((ascending ? 1 : -1) * ((a>b)-(a<b))):
					NaN
				);
			};
		}
		else {
			// default
			sortfn = function(a,b){
				return (ascending ? 1 : -1) * a.localeCompare(b);
			};
		}
		
		this._sort = function(a,b){
			a = (typeof a[field] != 'undefined') ? a[field]() : null;
			b = (typeof b[field] != 'undefined') ? b[field]() : null;
			return sortfn(a,b);
		};
		
	}
	// return a unique index identifying an items according to the data given in argument
	ArboModel.prototype.index = function(resource){
		var r = (resource instanceof EThing.Resource) ? resource : EThing.arbo.findOneById(resource);
		return r ? r.id() : null;
	}
	// specific
	ArboModel.prototype.getResource = function(item){
		if(!item){
			// root directory asked
			if(typeof this._options.root == 'string')
				return EThing.arbo.findOneById(this._options.root);
			if(!this._options.root)
				return EThing.arbo.root();
			return this._options.root;
		}
		if(item.id()==='____prev____')
			return EThing.arbo.findOneById(item._pwd);
		return item;
	}
	ArboModel.prototype.filter = function(filter){
		this._filter = filter;
	}
	
	
	
	var ArboTableView = function(opt) {
		
		opt = $.extend(true,{
			fields: {
				'icon': {
					label: "",
					get: function(r){
						return generateSvgResourceIcon(r);
					},
					class: "col-icon",
					sortable: false
				},
				'name':{
					formatter: EThing.Resource.basename,
					class: "col-name"
				},
				'size':{
					get: function(resource){
						if(typeof resource.size === "function")
							return EThing.utils.sizeToString(resource.size());
						else if(resource instanceof EThing.Table)
							return resource.length()+' rows';
						else if(resource instanceof EThing.Folder)
							return resource.length()+' resources';
						else
							return '-';
					},
					class: "col-size"
				},
				'modifiedDate':{
					label: "modified",
					formatter: function(v){
						return v===null ? '-' : EThing.utils.dateToString(v);
					},
					class: "col-modified"
				}
			},
			showOnlySpecifiedField: true
		},opt);
		
		$.Table.TableView.call(this,opt);
	}
	inherits(ArboTableView,$.Table.TableView);
	
	
	
	
	var ArboWallView = function(opt) {
		
		this._options = $.extend(true,{
			class: 'wallview'
		},opt);
		
		$.Table.View.call(this);
	}
	inherits(ArboWallView,$.Table.View);
	
	ArboWallView.prototype.init = function($container, table){
		
		$.Table.View.prototype.init.call(this,$container,table);
		
		this._$grid = $('<div>').appendTo(this.$()).addClass(this._options.class);
		
	}
	ArboWallView.prototype.clear = function(){
		this._$grid.empty();
	}
	ArboWallView.prototype.createItem = function(resource, id){
		
		var $item = $('<div>');
		
		// construct the item dom element
		
		// icon
		var $icon = $('<div>').html(generateSvgResourceIcon(resource,true)).addClass("col-icon");
		
		// name
		var $name = $('<div>').html(resource.name()).addClass("col-name");
		
		$item.append(
			$icon,
			$name
		);
		
		this._$grid.append($item);
		
		return $item;
	}
	ArboWallView.prototype.setSelectState = function($item, checked){
		// todo
	}
	
	

	
	
	Browser.Views = {
		'Wall': ArboWallView,
		'Table': ArboTableView
	};
	
	
	Browser.generateSvgResourceIcon = generateSvgResourceIcon;
	
	
	/* register as a plugin in jQuery */
	if (window.jQuery)
		window.jQuery.addPlugin('Browser',Browser);
	
	
	
})();
 
/* @file: src\ui\opendialog.js */ 
(function(){

	
	var extract = function(obj,properties){
		var keys = Object.keys(obj), extracted = {};
		for(var i=0; i<keys.length; i++){
			if(properties.indexOf(keys[i])>=0){
				extracted[keys[i]] = $.isPlainObject(obj[keys[i]]) ? jQuery.extend(true, {}, obj[keys[i]]) : obj[keys[i]];
				delete obj[keys[i]];
			}
		}
		return extracted;
	}
	
	
	/**
	 * @description Pop up an open dialog
     * @param {object} opt options
     */
	function OpenDialog(opt){
	
		var deferred = $.Deferred(),
			rejectOnClose = true;
		
		if(typeof opt == 'function')
			opt = {
				done:opt
			};
		
		var options = $.extend({
				filter: null, // function(resource) -> return boolean
				limit: 1, // limit the selection to a specific number
				title: "Open",
				preset: null, // a resource instance
				size: null // size of the modal dialog
			},opt),
			localOptions = extract(options,['filter','limit','title','preset','size']);
		
		
		var success = function(resource){
			rejectOnClose = false; // the modal may be closed before the done callback is finished
			
			$browser.modal('hide',function(){
				deferred.resolve(resource);
			});
		}
		
		// table explorer
		
		var rowEvents = function(){
			var evfct = function(e){
				var resource = e.data.item;
				if(!localOptions.filter || localOptions.filter(resource)){
					e.stopImmediatePropagation(); // disable default behaviour
					success([resource]);
				}
			};
			if(EThing.utils.isTouchDevice){
				if(localOptions.limit==1)
					return {
						'click': evfct
					}
			}
			else
				return {
					'dblclick': evfct
				};
			return {};
		}
		
		var $browser = $('<div>')
			.browser($.extend(true,{
					model:{
						filter : function(r){
							return localOptions.filter && !(r instanceof EThing.Folder) ? localOptions.filter(r) : true;
						}
					},
					selectable:{
						enable: true,
						limit: localOptions.limit,
						filter: localOptions.filter
					},
					loaded: function(){
						if(localOptions.preset)
							this.select(localOptions.preset);
					},
					row: {
						events: rowEvents()
					}
				},options))
			.modal({
				title: localOptions.title,
				buttons: {
					'+Open': function(){
						
						var $this = $(this),
							selection = $this.browser().selection();
						
						if(selection.length == 0){
							alert('No resource selected !');
							return false;
						}
						
						success(selection);
					},
					'!Cancel': null
				},
				size: localOptions.size
			})
			.on('hidden.bs.modal',function(){
				if(rejectOnClose)
					deferred.reject(null); // the user close the dialog, gives null as the parameter
			});
		
		
		return deferred.promise();
		
	}
	
	
	/* register as a plugin in jQuery */
	if (window.jQuery) {
		window.jQuery.OpenDialog = OpenDialog;
    }
	
	
})();
 
/* @file: src\ui\savedialog.js */ 
(function(){
	
	
	var extract = function(obj,properties){
		var keys = Object.keys(obj), extracted = {};
		for(var i=0; i<keys.length; i++){
			if(properties.indexOf(keys[i])>=0){
				extracted[keys[i]] = $.isPlainObject(obj[keys[i]]) ? jQuery.extend(true, {}, obj[keys[i]]) : obj[keys[i]];
				delete obj[keys[i]];
			}
		}
		return extracted;
	}
	
	
	/**
	 * @description Pop up a save dialog
     * @param {object} opt options
     */
	function SaveDialog(opt){
		
		var deferred = $.Deferred(),
			rejectOnClose = true;
		
		if(typeof opt == 'function')
			opt = {
				done:opt
			};
		
		var options = $.extend({
				filter: null, // function(resource) -> return boolean
				title: "Save",
				done: null, // done(resource) // the selected resource for saving, (must return a deferred object when this operation is asynchronous)
				preset: null, // a resource instance
				size: null, // size of the modal dialog
				canCreate: true, // if the user is able to create a new resource
				createPreset: null // create preset data as { name: "", type: 'File'|'Table'|'App'}
			},opt),
			localOptions = extract(options,['filter','title','done','preset','size','canCreate','createPreset']);
		
		
		var success = function(resource){
			rejectOnClose = false; // the modal may be closed before the done callback is finished
			
			$browser.modal('hide',function(){
				deferred.resolve(resource);
			});
		}
		
		
		var rowEvents = function(){
			var evfct = function(e){
				var resource = e.data.item;
				if(!localOptions.filter || localOptions.filter(resource)){
					e.stopImmediatePropagation(); // disable default behaviour
					success(resource);
				}
			};
			if(EThing.utils.isTouchDevice){
				return {
					'click': evfct
				}
			}
			else
				return {
					'dblclick': evfct
				};
		}
		
		var btns = {
			'+Save': function(){
				
				var $this = $(this),
					browser = $this.browser(),
					selection = browser.selection();
				
				if(selection.length == 0){
					alert('No resource selected !');
					return false;
				}
				
				success(selection[0]);
				
			},
			'!Cancel': null
		};
		
		if(localOptions.canCreate){
			btns['Create a new resource'] = function(){
				
				$('<div>')
					.form({
						'type': {
							input: ['File','Table','App'] // save for Device is meaningless
						},
						'name': {
							input: 'text',
							validator: $.Form.validator.NotEmpty
						}
					})
					.modal({
						title: 'Create a new resource',
						buttons:{
							'+Create': function(){
								
								var $this = $(this);
								
								$this.form().validate().done(function(props){
									EThing[props.type].create({
										name: props.name
									},function(r){
										if(r instanceof EThing.Resource){
											// the creation was successfull, close the dialog and reload the savedialog
											EThing.arbo.add(r);
											$this.modal('hide');// will be autoremoved
										}
										else
											// print the error message but do not close the modal dialog
											$this.form().setError(r.message);
									});
								});
								
								return false;
							},
							'!Cancel': null
						},
						size: localOptions.size
					}).form('setValue',localOptions.createPreset);
				
				return false; // do not close the dialog
			};
		}
		
		var $browser = $('<div>')
			.browser($.extend(true,{
					model:{
						filter : function(r){
							return localOptions.filter && !(r instanceof EThing.Folder) ? localOptions.filter(r) : true;
						}
					},
					selectable:{
						enable: true,
						limit: 1,
						filter: localOptions.filter
					},
					loaded: function(){
						if(localOptions.preset)
							this.select(localOptions.preset);
					}
				},options))
			.modal({
				title: localOptions.title,
				buttons: btns,
				size: localOptions.size
			})
			.on('hidden.bs.modal',function(){
				if(rejectOnClose)
					deferred.reject(null); // the user close the dialog, gives null as the parameter
			});
		
		return deferred.promise();
		
	}
	
	
	/* register as a plugin in jQuery */
	if (window.jQuery) {
		window.jQuery.SaveDialog = SaveDialog;
    }
	
	
})();
 
/* @file: src\ui\textviewer.js */ 
(function(){

var filter = function(r){
	// File => open everything except image, audio or video
	return ((r instanceof EThing.File) && !/^(image|audio|video)\//.test(r.mime())) || (r instanceof EThing.App);
}

var baseUrlSrc = '//cdnjs.cloudflare.com/ajax/libs/codemirror/5.14.2';

var dependency = $.Dependency({
	base: baseUrlSrc,
	url: ["codemirror.min.css","codemirror.js"],
	then: [
		"mode/meta.js",
		"addon/mode/loadmode.min.js",
		
		// search addon, see https://codemirror.net/demo/search.html
		(!EThing.utils.isTouchDevice) ? [
			"addon/search/matchesonscrollbar.min.css",
			"addon/dialog/dialog.min.css",
			"addon/dialog/dialog.min.js",
			"addon/search/search.min.js",
			"addon/search/searchcursor.min.js",
			"addon/scroll/annotatescrollbar.min.js",
			"addon/search/matchesonscrollbar.min.js",
			"addon/search/jump-to-line.min.js"
		] : null,
		
		// autoformating
		'//cdn.rawgit.com/beautify-web/js-beautify/v1.6.3/js/lib/beautify.js',
		'//cdn.rawgit.com/beautify-web/js-beautify/v1.6.3/js/lib/beautify-html.js',
		'//cdn.rawgit.com/beautify-web/js-beautify/v1.6.3/js/lib/beautify-css.js'
		
	]
}, function(){
	CodeMirror.modeURL = baseUrlSrc+"/mode/%N/%N.min.js";
	CodeMirror.modeInfo.sort(function(a,b){
		return a.name.localeCompare(b.name);
	});
	
});



var re_autoformat = /html|json|javascript|css/i;

var defaultOptions = {
	readonly: false, // if set, readonly mode, no change can be made, no save available
	data: null, // can either be a string to be shown or a deferred object (AJAX request ...) or a resource
	mode: null, // for syntax coloration ..., default to 'text/plain'
	filename: null, // the name of the current content, null if none
	lint: false, // activate the lint add-on for some compatible languages
	toolbar: {
		enable: true,
		filename: {
			enable: true,
			format: '%f' // format string (%f: filename) or function
		}
	}
};

var defaultActions = {
	'open': {
		icon: 'glyphicon-folder-open',
		on: function(tv){
			// returns a deferred object
			return $.OpenDialog({
				filter: filter,
				limit: 1
			}).then(function(r){
				return tv.open(r[0]); // piped deferred
			});
		}
	},
	'save':{
		icon: 'glyphicon-floppy-disk',
		before:function(tv){
			if(!tv.resource){
				tv.triggerAction('saveas');
				return false;
			}
			if(tv.hasLintError()){
				if(tv.resource instanceof EThing.Device){
					tv.notify('Invalid JSON !');
					return false;
				}
				else if(!confirm('Do you really want to save with some errors ?'))
					return false;
			}
			tv.__saveNotifUid = tv.notify('Saving ...');
		},
		on: function(tv){
			var text = tv.text(), d = (tv.resource instanceof EThing.Device) ? tv.resource.setDescriptor(text) : tv.resource.write(text);
			return d.fail(function(e){
				tv.notify(e.message);
			});
		},
		after:function(tv,deferred){
			deferred
				.always(function(){
					if(tv.__saveNotifUid){
						tv.removeNotification(tv.__saveNotifUid);
						delete tv.__saveNotifUid;
					}
				})
				.then(
					function(){
						// save successfull
						tv.markClean(); // Set the editor content as 'clean', a flag that it will retain until it is edited, and which will be set again when such an edit is undone again
					},
					function(){
						// on fail do nothing, do not mark the content as clean
					}
				);
		},
		showOnReadOnly: false
	},
	'saveas':{
		icon: 'glyphicon-floppy-save',
		on:function(tv){
			// SaveDialog returns a deferred object
			return $.SaveDialog({
				title: 'Save as ...',
				filter: filter,
				preset: tv.resource || null,
				createPreset:{
					name: tv.getFilename()
				}
			}).then(function(r){
				// must return a deferred object when the saving is asynchrone
				tv.resource = r;
				return tv.triggerAction('save').done(function(){
					tv.open(r);
				});
			});
		},
		showOnReadOnly: false
	},
	'undo':{
		icon:'glyphicon-arrow-left',
		before:function(tv){
			tv.editor().undo();
		},
		showOnReadOnly: false
	},
	'redo':{
		icon:'glyphicon-arrow-right',
		before:function(tv){
			tv.editor().redo();
		},
		showOnReadOnly: false
	},
	'autoformat':{
		icon:'glyphicon-indent-left',
		on:function(tv){
			var cm = tv.editor(),
				text = tv.text(),
				mode = cm.getOption("mode"), // cm.getMode().name
				fn = /css/i.test(mode) ? css_beautify : (/(javascript|json)/i.test(mode) ? js_beautify : html_beautify),
				sweetText = fn(text,{
					indent_size: cm.getOption('indentUnit'),
					indent_inner_html: true, // indent <head> and <body> sections
					wrap_line_length: 0 // disable wrap
				});
			
			tv.text(sweetText);
		},
		showOnReadOnly: false
	},
	'mode':{
		enable: false,
		tooltip: false,
		html: '<div class="btn-group btn-group-sm tv-mode" role="group"><button type="button" class="btn btn-default dropdown-toggle" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false"></button><ul class="dropdown-menu dropdown-menu-right"></ul></div>'
	},
	'fullscreen':{
		enable: true,
		icon:'glyphicon-resize-full',
		on: function(tv){
			tv.isFullscreen = !tv.isFullscreen;
			tv.$element.toggleClass('tv-fullscreen',tv.isFullscreen);
			tv.editor().refresh();
			
			$('.tv-action[data-role="fullscreen"] .glyphicon',tv.$element).removeClass(tv.isFullscreen ? 'glyphicon-resize-full' : 'glyphicon-resize-small').addClass(tv.isFullscreen ? 'glyphicon-resize-small' : 'glyphicon-resize-full');
		}
	}
};




var TextViewer = function(element,options) {
	
	var self = this;
	
	$.AbstractPlugin.call(this,element,$.extend(true,{actions: defaultActions},defaultOptions,options));
	
	
	this.$element.empty().removeClass('tv-fullscreen tv-readonly tv-toolbar').addClass('TextViewer');
	
	/*
	 build the toolbar
	*/
	
	// build the toolbar
	var $tb = $('<div class="tv-toolbar"><div class="btn-group btn-group-sm tv-actions"></div><div class="tv-filename"></div></div>')
		.hide()
		.appendTo(this.$element);
	
	$.each(this.options.actions,function(name,action){
		self.addAction(name,action);
	});
	
	if(!this.options.actions.mode.enable){
		$tb.append('<div class="tv-mode dropdown"><span data-toggle="dropdown" aria-haspopup="true" aria-expanded="false"></span><ul class="dropdown-menu dropdown-menu-right"></ul></div>');
	}
	
	
	
	
	/*
	* init Codemirror instance
	*/
	
	var $content = $('<div>').addClass('tv-content').appendTo(this.$element);
	
	dependency.require(function(){
		
		// fill the mode dropdown list with the available modes :
		var $ulmode = $('.tv-mode>ul',self.$element);
		for(var i = 0; i<CodeMirror.modeInfo.length; i++)
			$ulmode.append('<li><a>'+CodeMirror.modeInfo[i].name+'</a></li>');
		$ulmode.find('li > a').click(function(){
			var modeName = $(this).text();
			self.setMode(CodeMirror.findModeByName(modeName));
		});
		
		self._editor = new CodeMirror($content[0], {
			"lineNumbers": true,
			"lineWrapping": false,
			'mode': 'text/plain',
			'viewportMargin':Infinity,
			'extraKeys': {
				"Ctrl-S": function(cm) {
					self.triggerAction('save');
				},
				// fullscreen mode
				"Esc": function(cm) {
				  if (self.isFullscreen) self.triggerAction('fullscreen');
				}
			},
			
		});
		
		self._editor.setSize(null,'auto');
		self._editor.off();
		self._editor.refresh();
		
		
		var $undo = $('.tv-action[data-role="undo"]',self.$element),
			$redo = $('.tv-action[data-role="redo"]',self.$element),
			$save = $('.tv-action[data-role="save"]',self.$element),
			$filename = $('.tv-filename',self.$element);
		
		self._editor.on('change',function(instance,changeObj){
			// The changeObj is a {from, to, text, removed, origin} object containing information about the changes that occurred
			if(instance.isClean())
				$filename.removeClass('tv-dirty');
			else
				$filename.addClass('tv-dirty');
			
			$undo.prop( "disabled", instance.historySize().undo==0 );
			$redo.prop( "disabled", instance.historySize().redo==0 );
			$save.prop( "disabled", instance.isClean() );
			
		});
		
		setTimeout(function(){
			self.$element.trigger('editor-loaded.tv');
			
			/*
			* Open the data
			*/
			self.open(options);
		},1);
		
		
		// refresh until there is some line shown, the content may not show on modal for instance
		var el = self.$element.find('.CodeMirror-code')[0];
		var rtid = setInterval(function(){
			if(el.childElementCount){
				clearInterval(rtid);
				return;
			}
			if(el.offsetParent!==null){
				self._editor.refresh();
			}
		},200);
		
		
		
	});
	
	

};
TextViewer.prototype.open = function(options){
	var self = this, deferred = $.Deferred();
	
	if(!$.isPlainObject(options))
		options = {
			data: options
		};
	
	$.extend(true,this.options,{
		data: null,
		mode: null,
		filename: null
	},options);
	
	// data as resource
	delete this.resource;
	if(this.options.data instanceof EThing.Resource){
		var resource = this.resource = this.options.data, mime;
		
		console.log('mime: ',resource.mime());
		// specificities
		if(resource instanceof EThing.File){
			if(!this.options.mode)
				this.options.mode = resource.mime();
			this.options.data = resource.read();
		}
		else if(resource instanceof EThing.App){
			this.options.mode = 'text/html'; // override
			this.options.data = resource.read();
		}
		else if(resource instanceof EThing.Device){
			this.options.mode = 'application/json'; // override
			var d = $.Deferred();
			resource.getDescriptor()
				.done(function(spec){
					d.resolve(JSON.stringify(spec,null,2));
				})
				.fail(function(e){
					d.reject(e);
				});
			this.options.data = d.promise();
		}
		else {
			this.notify('Invalid data !');
			return;
		}
		
		if(!this.options.filename)
			this.options.filename = resource.name();
		
	}
	else if(this.options.data instanceof File){
		
		var file = this.options.data;
		
		if(!this.options.filename)
			this.options.filename = file.name;
		
		this.options.mode = file.type;
		
		var fr = new FileReader()
			dfr = $.Deferred();
		fr.onload = function(){
			var text = fr.result;
			dfr.resolve(text);
		};
		fr.onerror = fr.onabort = function(){
			dfr.reject();
		}
		fr.readAsText(file);
		
		this.options.data = dfr.promise();
	}
	
	// update toolbar
	$('.tv-toolbar',this.$element).toggle(this.options.toolbar.enable);
	$.each(this.options.actions,function(name,action){
		var $action = $('.tv-action[data-role="'+name+'"]',self.$element);
		if($action.length)
			$action.toggle(action.enable && (!self.options.readonly || action.showOnReadOnly));
		else
			self.addAction(name,action);
	});
	
	// set filename
	$('.tv-filename',this.$element)
		.html(this.options.toolbar.filename.enable ? (typeof this.options.toolbar.filename.format == 'function' ? this.options.toolbar.filename.format.call(this,this.getFilename()) : this.options.toolbar.filename.format.replace('%f', this.getFilename())) : '');
	
	
	this.$element.toggleClass('tv-readonly',self.options.readonly);
	this.$element.toggleClass('tv-toolbar',self.options.toolbar.enable);
	
	var nuid = this.notify(this.options.filename ? ('Opening '+this.getFilename()) : 'Opening ...');
	
	var lint;
	if(this.options.lint && !self.options.readonly){
		if(/json/i.test(this.options.mode || ''))
			lint = 'js';
	}
	
	// load some extra addon if necessary
	var addondfr = EThing.utils.require(
		(lint) ? {
			base: baseUrlSrc,
			url:[
				"addon/lint/lint.min.css",
				"addon/lint/lint.min.js",
				(lint=='js') ? [
					"https://cdn.rawgit.com/zaach/jsonlint/79b553fb65c192add9066da64043458981b3972b/lib/jsonlint.js",
					"addon/lint/json-lint.min.js"
				] : null
			]} : null );
	
	// load the data
	$.when(this.options.data || '', addondfr).done(function(){
		var text = typeof arguments[0] == 'string' ? arguments[0] : arguments[0][0];
		
		if($.isPlainObject(text))
			text = JSON.stringify(text,null,2);
		
		self.setMode(self.options.mode || self.getFilename());
		
		self.editor().setOption('readOnly',self.options.readonly ? 'nocursor' : false);
		self.editor().setOption('gutters',lint ? ["CodeMirror-lint-markers"] : []);
		self.editor().setOption('lint',lint);
		
		self.editor().setValue(text);
		
		self.markClean();
		self.clearHistory();
		
		console.log('mode: ',self.editor().getOption('mode'));
		
		self.removeNotification(nuid);
		
		deferred.resolveWith(self,[text]);
		
		self.$element.trigger('data-loaded.tv');
	}).fail(function(e){
		deferred.rejectWith(self,[e]);
	});
	
	return deferred.promise();
	
}
TextViewer.prototype.addAction = function(name,props){
	
	var self = this;
	
	props = $.extend(true,{
		name: name,
		enable: true,
		icon: null,
		showOnReadOnly: true,
		tooltip: null,
		html: function(tv){
			var $html = $('<button type="button" class="btn btn-default">'), name = this.name;
			if(this.icon){
				if(typeof this.icon == 'string' && /^glyphicon-/.test(this.icon))
					$html.prepend('<span class="glyphicon '+this.icon+'" aria-hidden="true">');
				else
					$html.prepend(this.icon);
			}
			else
				$html.prepend(name);
			
			$html.click(function(){
				tv.triggerAction(name);
			});
			
			return $html;
		},
		on: null,
		before: null,
		after: null
	},props);
	
	if(props.tooltip===null)
		props.tooltip = name;
	
	var $action = $(typeof props.html == 'function' ? props.html.call(props,self) : props.html);
	
	$action.attr('data-role',name).addClass('tv-action');
	
	if(!EThing.utils.isTouchDevice){
		if(props.tooltip!==false)
			$action.tooltip({
				container: this.$element,
				trigger:'hover',
				placement: 'bottom',
				title: props.tooltip
			});
	}
	
	$action.toggle(props.enable && (!this.options.readonly || props.showOnReadOnly));
	
	this.options.actions[name] = props;
	
	$('.tv-actions',this.$element).append($action);
}
TextViewer.prototype.setMode = function(info){
	var self = this;
	
	if(typeof info == 'string'){
		var value = info;
		if (m = /.+\.([^.]+)$/.exec(value)) { // filename
			info = CodeMirror.findModeByExtension(m[1]);
		} else if (/\//.test(value)) { // mime
			info = CodeMirror.findModeByMIME(value);
		} else { // name
			info = CodeMirror.findModeByName(value);
		}
	}
	
	if(!info)
		info = CodeMirror.findModeByMIME('text/plain');
	
	if($.isPlainObject(info)){
		dependency.require(function(){
			self.editor().setOption('theme',info.mode + ' default');
			self.editor().setOption('mode',info.mime);
			CodeMirror.autoLoadMode(self.editor(), info.mode);
			
			var action = self.options.actions['autoformat'];
			if(action && action.enable)
				$('.tv-action[data-role="'+action.name+'"]',self.$element).prop( "disabled",!re_autoformat.test(info.mode));
		});
		$('.tv-mode>span,.tv-mode>button',self.$element).html(info.name);
	}
}
TextViewer.prototype.markClean = function(){
	if(this.editor()){
		this.editor().markClean();
	}
	$('.tv-filename',this.$element).removeClass('tv-dirty');
	$('.tv-action[data-role="save"]',this.$element).prop( "disabled",true);
}
TextViewer.prototype.clearHistory = function(){
	if(this.editor()){
		this.editor().clearHistory();
	}
	$('.tv-action[data-role="undo"]',this.$element).prop( "disabled",true);
	$('.tv-action[data-role="redo"]',this.$element).prop( "disabled",true);
}

TextViewer.prototype.hasLintError = function(){
	var editor = this.editor(), lint;
	if(editor && (lint = editor.getHelper(CodeMirror.Pos(0, 0), "lint"))){
		var state = editor.state.lint;
		if(state.marked.length)
			return true;
	}
	return false;
}
TextViewer.prototype.notify = function(message, timeout){
	if(!message || message ==="") return;
	
	var self = this;
	
	var $notify = this.$element.find('.tv-notification');
	if(!$notify.length){
		$notify = $('<div class="tv-notification">').appendTo(this.$element);
	}
	
	// build the message
	var uid = "message-"+String(Math.round(Math.random()*1000000)),
		$message = $('<div id="'+uid+'" class="alert alert-info alert-dismissible" role="alert">').append('<button type="button" class="close" data-dismiss="alert" aria-label="Close"><span aria-hidden="true">&times;</span></button>',message.message || message);
	
	$message.appendTo($notify);
	
	$notify.show();
	
	if((typeof timeout == 'number') && timeout>0)
		window.setTimeout(function(){
			self.removeNotification(uid);
		},timeout);
	
	return uid;
}
TextViewer.prototype.removeNotification = function(uid){
	var $notify = this.$element.find('.tv-notification');
	if($notify.length){
		$notify.find('#'+uid).remove();
		if(!$notify.find('[id^="message-"]').length){
			$notify.hide();
		}
	}
}
TextViewer.prototype.editor = function(){
	return this._editor || null;
}
TextViewer.prototype.isClean = function(){
	return this.editor() && this.editor().isClean();
}
TextViewer.prototype.value = function(value) {
	// No value passed, act as a getter.
	if ( value === undefined ) {
		return this.text();
		
	// Value passed, act as a setter.
	} else { 
		return this.open(value);
	}
}
TextViewer.prototype.text = function(content) {
	return typeof content == 'undefined' ? this.editor().getValue() : this.editor().setValue(content);
};
TextViewer.prototype.getFilename = function() {
	return this.options.filename || 'untitled';
};
TextViewer.prototype.triggerAction = function(actionName, data) {
	var deferred = $.Deferred(),
		self = this;
	
	var parts = actionName.split('.');
	actionName = parts.shift();
	var subaction = parts.length>0 ? parts.join('.') : null;
	
	if(this.options.actions.hasOwnProperty(actionName) && this.options.actions[actionName].enable){
		var action = this.options.actions[actionName];
		
		var e = $.Event( 'before-trigger-'+actionName+'.tv', { action: actionName } );
		this.$element.trigger(e);
		
		if(e.isDefaultPrevented())
			deferred.rejectWith(self);
		
		if(deferred.state() != "rejected" && $.isFunction(action.before))
			if(action.before.call(action,self,data,subaction) === false){
				deferred.rejectWith(self);
			}
		if(deferred.state() != "rejected"){
			if($.isFunction(action.on)){
				// this handler may return a jQuery deferred object
				try {
					var def = action.on.call(action,self,data,subaction);
					if(def===false)
						deferred.rejectWith(self);
					else
						$.when(def).then(function(result){
							deferred.resolveWith(self,[result]);
						},function(){
							deferred.rejectWith(self);
						});
				}
				catch(e){
					console.log(e);
					self.notify(e);
					deferred.rejectWith(self);
				}
			}
			else{
				deferred.resolveWith(self);
			}
			
			if($.isFunction(action.after))
				action.after.call(action,self,deferred,data,subaction);
		}
	}
	else
		deferred.rejectWith(self);
	
	deferred.done(function(){
		self.$element.trigger('trigger-'+actionName+'.tv');
	});
	
	return deferred.promise();
};
TextViewer.prototype.toggleAction = function(actionName, state) {
	var action = this.options.actions[actionName];
	if(action){
		action.enable = !!state;
		$('.tv-action[data-role="'+action.name+'"]',this.$element).toggle(action.enable);
	}
};


TextViewer.accept = filter;


/* register as a plugin in jQuery */
if (window.jQuery)
	window.jQuery.addPlugin('TextViewer',TextViewer);


})(); 
/* @file: src\ui\tableviewer.js */ 
(function(){
	
	
	function inherits(extended, parent){
		extended.prototype = Object.create(parent.prototype);
	};
	
	
	function TableViewer(element,opt){
		
		var self = this;
		
		if(opt instanceof EThing.Table)
			opt = {
				table: opt
			};
		
		var options = $.extend(true,{
			table: null,
			view: new $.Table.TableView({
				fields:{
					'__check':{
						hidden: true
					},
					'date':{
						formatter: function(d){
							function pad(n, width, z) {
								z = z || '0';
								n = n + '';
								return n.length >= width ? n : new Array(width - n.length + 1)
									.join(z) + n;
							}
							return pad(d.getFullYear(), 4) + '/' + pad(d.getMonth() + 1, 2) + '/' + pad(d.getDate(), 2) + ' ' + pad(d.getHours(), 2) + ':' + pad(d.getMinutes(), 2) + ':' + pad(d.getSeconds(), 2);
						},
						class: 'date'
					}
				},
				selectable:{
					check: true
				}
			}),
			selectable:{
				enable: true,
				limit: null,
				trigger: null
			},
			pagination:{
				itemsPerPage: [20,50,100,'all'], // may be an array of available values [20,50,100,'all']
				enable: true // enable the pagination
			},
			sortBy: '-date',
			class: 'tableviewer',
			readonly: false
		},opt);
		
		this._table = options.table;
		
		if(this._table instanceof EThing.Table){
			delete options.table;
			if(!options.model)
				options.model = new TableModel(this._table);
		}
		
		
		$.Table.call(this,element,options);
		
		this.$element.find('table').addClass('table table-hover');
		
		// add specific actions :
		var actions = {
			'update':{
				fn: function(){
					self.reload();
				},
				icon: 'repeat',
				tooltip: 'reload the data'
			},
			'edit':this._table && !this.options.readonly ? {
				fn: function(){
					self.view().setVisible('__check',!self.view().isVisible('__check'));
					$actions.find('[data-name="remove"]').toggle();
				},
				icon: 'check',
				tooltip: 'edit the table'
			} : null,
			'remove':this._table && !this.options.readonly ? {
				fn: function(){
					var selection = self.selection();
					if(selection.length){
						if(confirm('Remove the '+selection.length+' selected row(s) ?')){
							var ids = selection.map(function(el){
								return el.id;
							});
							self._table.removeRow(ids,function(){
								// reload the table
								self.reload();
							});
						}
					}
					else
						alert('No rows selected.');
				},
				icon: 'trash',
				tooltip: 'remove the selected rows'
			} : null,
			'filter':this._table ? {
				fn: function(){
					
					var $html = $('<div><textarea class="form-control" placeholder="field == value"></textarea><div class="alert alert-danger" role="alert" style="display: none;"></div></div>'),
						currentFileter = self.model().filter();
					
					if(currentFileter)
						$html.find('textarea').val(currentFileter);
					
					$html.find('textarea').change(function(){
						$html.find('.alert').hide();
					});
					
					$html.modal({
						title: 'Filter data',
						buttons: {
							'+Filter': function(){
								var query = $html.find('textarea').val(), $this = $(this);
								self.model().filter(query);
								self.reload().done(function(){
									$this.modal('hide');
								}).fail(function(e){
									$html.find('.alert').html(e.message).show();
								});
								return false;
							},
							'Cancel': null
						}
					});
				},
				icon: 'filter',
				tooltip: 'apply a filter'
			} : null,
			'add':this._table && !this.options.readonly ? {
				fn: function(){
					
					var table = self._table,
						$html = $('<div class="container-fluid">');
					
					var addField = function(){
						
						var $row = $('<div class="row">'+
									  '<div class="col-sm-5">'+
										'<div class="input-group field">'+
										  '<input type="text" class="form-control" placeholder="field">'+
										  '<div class="input-group-btn">'+
											'<button type="button" class="btn btn-default dropdown-toggle" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false"><span class="caret"></span></button>'+
											'<ul class="dropdown-menu dropdown-menu-right">'+
											'</ul>'+
										  '</div>'+
										'</div>'+
									  '</div>'+
									  '<div class="col-sm-6">'+
										'<div class="input-group value">'+
										  '<div class="input-group-btn">'+
											'<button type="button" class="btn btn-default dropdown-toggle" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false"><span class="type">String</span> <span class="caret"></span></button>'+
											'<ul class="dropdown-menu">'+
											  '<li><a>String</a></li>'+
											  '<li><a>Number</a></li>'+
											  '<li><a>Boolean</a></li>'+
											  '<li><a>Text</a></li>'+
											'</ul>'+
										  '</div>'+
										  '<input type="text" class="form-control" placeholder="value">'+
										'</div>'+
									  '</div>'+
									  '<div class="col-sm-1">'+
										'<button type="button" class="btn btn-default" data-role="remove"><span class="glyphicon glyphicon-trash" aria-hidden="true"></span></button>'+
									  '</div>'+
									'</div>');
						
						
						var li = [], keys = table.keys();
						for(var i=0; i<keys.length; i++)
							li.push('<li><a>'+keys[i]+'</a></li>');
						$row.find('.field ul').append(li);
						
						$row.find('.value ul a').click(function(){

						  var type = $(this).text(),
							  $input = $(this).closest('.value').find('input,select,textarea'),
							  replace;
						  
						  $(this).closest('.value').find('span.type').text(type);
						  
						  switch(type.toLowerCase()){
							case 'string':
							  if(!$input.is('input[type="text"]'))
								replace = '<input type="text">';
							  break;
							case 'number':
							  if(!$input.is('input[type="number"]'))
								replace = '<input type="number" value="0">';
							  break;
							case 'boolean':
							  if(!$input.is('select'))
								replace = '<select><option>true</option><option>false</option></select>';
							  break;
							case 'text':
							  if(!$input.is('textarea'))
								replace = '<textarea>';
							  break;
						  }
						  
						  if(replace)
							$input.replaceWith($(replace).addClass('form-control'));
						  
						})

						$row.find('.field ul a').click(function(){
						  var fieldname = $(this).text();
						  $(this).closest('.field').find('input').val(fieldname);
						})
						
						$row.find('[data-role="remove"]').click(function(){
							$row.remove();
						});
						
						$row.insertBefore($html.children('.row').last());
						
					}
					
					var getValue = function(){
						var out = {}, err = false;
						
						$html.children('.row').each(function(){
							
							var $this = $(this),
								fieldname = $this.find('.field').find('input').val(),
								$input = $this.find('.value').find('input,select,textarea'),
								value;
							
							if(typeof fieldname == 'undefined')
								return;
							
							if(fieldname.length == 0){ // empty field name
								err = true;
								return;
							}
							
							if($input.is('input[type="number"]')){
								value = parseFloat($input.val()); // number
							}
							else if($input.is('select')){
								value = /true/i.test($input.val()); // boolean
							}
							else {
								value = $input.val(); // string
							}
							
							out[fieldname] = value;
							
						});
						
						if(Object.keys(out).length === 0)
							err = true;
						
						return err ? null : out;
					}
					
					$html.append( $('<div class="row row-top-space">').append(
						$('<div class="col-sm-1">').append(
							$('<button type="button" class="btn btn-default"><span class="glyphicon glyphicon-plus" aria-hidden="true"></span> field</button>').click(addField)
						)
					));
					
					// at 1 field by default
					addField();
					
					$html.modal({
						title: 'Add data',
						buttons: {
							'+Add': function(){
								var modal = this, data = getValue();
								if(data)
									table.insert(data).done(function(){
										$html.modal('hide');
										self.reload();
									});
								return false;
							},
							'Cancel': null
						},
						size: 'lg'
					});
					
					
				},
				icon: 'plus',
				tooltip: 'add data'
			} : null
		},
		$actions = this.$element.find('div[name="actions"]');
		
		for(var i in actions){
			$('<button type="button" class="btn btn-default" data-name="'+i+'">')
				.append('<span class="glyphicon glyphicon-'+actions[i].icon+'" aria-hidden="true">')
				.click(actions[i].fn)
				.tooltip({
					container: this.$element,
					trigger:'hover',
					placement: 'bottom',
					title: actions[i].tooltip
				})
				.appendTo($actions);
		}
		
		$actions.find('[data-name="remove"]').hide();
		
		
	}
	inherits(TableViewer,$.Table);
	
	
	
	
	var TableModel = function(options){
		if(options instanceof EThing.Table)
			options = {
				table: options
			};
		
		this._options = $.extend(true,{
			table: null
		},options);
		
		$.Table.Model.call(this,this._options);
		
		this._table = this._options.table;
		this._sort = null;
		this._filter = null;
	}
	inherits(TableModel,$.Table.Model);
	
	// return the keys/columns
	TableModel.prototype.keys = function(){
		var ks = this._table.keys();
		ks.unshift('date');
		return ks;
	}
	// return the number of rows, null if not known
	TableModel.prototype.rows = function(){
		return this._table.length();
	}
	// return the items, may be a deferred object
	// offset and length are used for pagination
	TableModel.prototype.data = function(parent, offset, length){
		var deferred = $.Deferred(),
			self = this;
		EThing.Table.select(this._table,{
			start: offset || 0,
			length: length || this._table.length(),
			sort: this._sort || "-date",
			query: this._filter
		})
			.done(function(items){
				deferred.resolve(
					items.map(function(item){
						item.date = new Date(item.date);
						return item;
					})
				);
			})
			.fail(function(e){
				deferred.reject(e);
			});
		
		return deferred;
	}
	// check if an item has children or not (tree model may have)
	TableModel.prototype.hasChildren = function(item){
		return false;
	}
	// sort the data
	TableModel.prototype.sort = function(field, ascending){
		this._sort = (ascending ? '+' : '-') + field;
	}
	// return a unique index identifying an items according to the data given in argument
	TableModel.prototype.index = function(tableItem){
		return tableItem.id;
	}
	TableModel.prototype.filter = function(query){
		if(typeof query == 'undefined')
			return this._filter;
		this._filter = (typeof query == 'string') ? query : null;
	}
	
	
	/* register as a plugin in jQuery */
	if (window.jQuery)
		window.jQuery.addPlugin('TableViewer',TableViewer);
	

})();
 
/* @file: src\ui\mapviewer.js */ 
(function(){
	
	var dependency = $.Dependency({
		url: ['//cdnjs.cloudflare.com/ajax/libs/ol3/3.15.1/ol.js','//cdnjs.cloudflare.com/ajax/libs/ol3/3.15.1/ol.css']/*,
		then: '//cdn.rawgit.com/walkermatt/ol3-layerswitcher/master/src/ol3-layerswitcher.js'*/
	},function(){
		// custom control
		ol.control.CustomControl = function(opt_options) {

			var options = opt_options || {
				glyphicon: null,
				click: null,
				class: null
			};

			var button = document.createElement('button');
			button.innerHTML = '<span class="glyphicon glyphicon-'+options.glyphicon+'" aria-hidden="true"></span>';

			button.addEventListener('click', options.click, false);
			button.addEventListener('touchstart', options.click, false);

			var el = document.createElement('div');
			el.className = options.class + ' ol-unselectable ol-control';
			el.appendChild(button);

			ol.control.Control.call(this, {
				element: el,
				target: options.target
			});

		};
		ol.inherits(ol.control.CustomControl, ol.control.Control);
	});
	

	
	
	
	
	function getResourceLocation(resource){
		return (typeof resource.location == 'function' && resource.location()) ? resource.location() : null;
	}
	
	
	function MapViewer(element,options){
		var self = this;
		
		$.AbstractPlugin.call(this,element,$.extend(true,{
			marker:{
				onClick: null // function(resource) fired when a marker is clicked
			},
			center: null, // can either be google.maps.LatLng, or a resource
			onload: null,
			resources: []
		},options));
		
		
		this.$element.empty().addClass('mapviewer');
		
		
		function init(){
			
			var center = this.options.center,
				autocenter = false;
			
			if(Array.isArray(center) && center.length == 2){
				center = ol.proj.fromLonLat(center);
			}
			else if(center instanceof EThing.Resource){
				var loc = getResourceLocation(center);
				center = ol.proj.fromLonLat([loc.longitude, loc.latitude]);
			}
			else {
				autocenter = true;
				center = null;
			}
			
			
			// feature layer
			this._featuresLayer = new ol.layer.Vector({
				source: new ol.source.Vector({})
			});
			
			var _map = new ol.Map({
				target: this.$element[0],
				layers: [
					// maps
					new ol.layer.Tile({
						title: 'Map',
						type: 'base',
                        visible: true,
						source: new ol.source.OSM()
					}),
					/*new ol.layer.Tile({
                        title: 'Satellite',
                        type: 'base',
                        visible: false,
                        source: new ol.source.MapQuest({layer: 'sat'}) // need an api key since 11 july 2016
                    }),*/
					// features
					this._featuresLayer
				],
				view: new ol.View({
					center: center || ol.proj.fromLonLat([1.443962, 43.604482]),
					zoom:5
				}),
				controls: ol.control.defaults().extend([
					new ol.control.CustomControl({
						click: function(){
							self.autoCenter();
						},
						class: 'map-center-control',
						glyphicon: 'screenshot'
					})/*, new ol.control.LayerSwitcher()*/
				])
			});
			
			this.map = function(){
				return _map;
			}
			
			
			// tooltip
			var $tooltip = $('<div class="map-tooltip">').appendTo(this.$element);
			$tooltip.tooltip({
			  animation: false,
			  trigger: 'manual'
			});
			
			// setup popup overlay
			var $popup = $('<div>').appendTo(this.$element);
			this._popup = new ol.Overlay({
			  id: "popup",
			  element: $popup[0],
			  positioning: 'bottom-center',
			  stopEvent: false,
			  autoPan: true,
			  autoPanAnimation: {
			    duration: 250
			  }
			});
			_map.addOverlay(this._popup);
			
			
			// events
			_map.on('click', function(e) {
			  var feature = _map.forEachFeatureAtPixel(e.pixel,
				  function(feature, layer) {
					return feature;
				  });
			  if (feature) {
				var resource = feature.get('resource');
				
				self.showPopup(resource);
				
				if(typeof self.options.marker.onClick == 'function')
					self.options.marker.onClick.call(self,resource);
				
			  } else {
				self.hidePopup();
			  }
			});

			
			if(!EThing.utils.isTouchDevice) _map.on('pointermove', function(e) {
			  if (e.dragging) {
				$tooltip.tooltip('hide');
				return;
			  }
			  
			  var feature = _map.forEachFeatureAtPixel(e.pixel, function(feature, layer) {
				return feature;
			  });
			  
			  // change mouse cursor when over marker
			  _map.getTarget().style.cursor = feature ? 'pointer' : '';
			  
			  // tooltip
			  if (feature && $popup.data('f') !== feature) {
				var geometry = feature.getGeometry(),
					coordinates = (geometry instanceof ol.geom.Point) ? geometry.getCoordinates() : e.coordinate,
					pixel = _map.getPixelFromCoordinate(coordinates);
				
				$tooltip
					.tooltip('hide')
					.css({
						left: pixel[0] + 'px',
						top: (pixel[1] - 35) + 'px'
					  })
					.attr('data-original-title', feature.get('name'))
					.tooltip('fixTitle')
					.tooltip('show');
			  } else {
				$tooltip.tooltip('hide');
			  }
			  
			});
			
			
		
			if(this.add(this.options.resources)){
				if(autocenter)
					this.autoCenter();
			}
			else {
				// no resource to draw
				this.$element.prepend('<div class="alert alert-warning map-alert" role="alert">No resource to show !</div>');
			};
			
			if(typeof this.options.onload == 'function')
				this.map().once('postrender',this.options.onload,this);
		}
		
		dependency.require(function(){
			init.call(self);
		});
		
	}
	
	MapViewer.prototype.autoCenter = function(){
		
		var map = this.map(),
			source = this._featuresLayer.getSource(),
			length = source.getFeatures().length;
		
		if(length)
			map.getView().fit(source.getExtent(), map.getSize(), {
				maxZoom: length>1 ? 19 : 15
			});
		
	}
	
	MapViewer.prototype.add = function(resources, cb){
		var added = 0;
		
		if(!Array.isArray(resources))
			resources = (resources===null || typeof resources == 'undefined') ? [] : [resources];
		
		resources.forEach(function(resource){
			
			// check if this resource has a loaction attribute set
			var loc = getResourceLocation(resource);
			
			if(loc){
				
				
				var color;
			
				switch(resource.type()){
					case 'Device':
						color = "9b59b6";
						break;
					case 'File':
						color = "1abc9c";
						break;
					case 'Table':
						color = "3498db";
						break;
					case 'App':
						color = "2ecc71";
						break;
					default:
						color = "CC2EAD";
						break;
				}
				
				var map = this.map(),
					vectorSource = this._featuresLayer.getSource(),
					icon = "//chart.googleapis.com/chart?chst=d_map_pin_letter&chld="+resource.type()[0]+"|" + color,
					coordinates = ol.proj.fromLonLat([loc.longitude,loc.latitude]);
				
				
				var iconStyle = new ol.style.Style({
				  image: new ol.style.Icon({
					anchor: [0.5, 1],
					anchorXUnits: 'fraction',
					anchorYUnits: 'fraction',
					opacity: 0.75,
					src: icon
				  })
				});
				//create icon at new map center
				var iconFeature = new ol.Feature({
					geometry: new ol.geom.Point(coordinates),
					name: resource.name(),
					resource: resource
				});
				
				iconFeature.setStyle(iconStyle);

				//add icon to vector source
				vectorSource.addFeature(iconFeature);
				added++;
				
			}
			
		},this);
		
		return added;
	}
	
	
	MapViewer.prototype.showPopup = function(resource){
		if(!resource) 
			return;
		var feature = this._feature(resource),
			popup = this._popup,
			map = this.map();
		if(!feature || !popup) 
			return;
		
		// calculate the center of the geometry !
		var extent = feature.getGeometry().getExtent(),
			coordinates = [ (extent[0] + extent[2])/2 , (extent[1] + extent[3])/2 ];
		
		var popupGenerateContent = function(resource){
			var loc = resource.location(),
				content = '<div class="map-popup-content">';
			
			content += '<h4>'+resource.name()+' <small>['+resource.type()+']</small></h4>';
			
			// print location
			content += '<p><span class="glyphicon glyphicon-map-marker" aria-hidden="true"></span> '+loc.latitude+"N "+loc.longitude+"E"+'</p>';
			
			// print date
			var date = (resource instanceof EThing.Device) ? resource.lastSeenDate() : resource.modifiedDate();
			content += '<p><span class="glyphicon glyphicon-time" aria-hidden="true"></span> '+(date ? EThing.utils.dateDiffToString( Math.floor( (Date.now() - date.getTime()) / 1000 ) ) : 'never')+'</p>';
			
			// print description if any
			var description = resource.description();
			if( description && description.length)
				content += '<p>'+description+'</p>';
			
			content += '</div>';
			
			return content;
		}
		
		// popup
		popup.setPosition(coordinates);
		$(popup.getElement())
			.data('f',feature)
			.popover({
			  'trigger': 'manual',
			  'placement': 'top',
			  'html': true,
			  'template': '<div class="popover map-popup" role="tooltip"><div class="arrow"></div><h3 class="popover-title"></h3><div class="popover-content"></div></div>',
			  'content': function(){
				return popupGenerateContent.call(map,$(this).data('f').get('resource'));
			  }
			})
			.popover('show');
		
	}
	
	MapViewer.prototype.hidePopup = function(){
		var $popup = $(this._popup.getElement());
		$popup.popover('destroy');
		$popup.data('f',null);
	}
	
	MapViewer.prototype._feature = function(resource){
		// return the feature of a resource
		var features = this._featuresLayer.getSource().getFeatures();
		for(var i=0; i<features.length; i++){
			if(features[i].get('resource').id() == resource.id())
				return features[i];
		}
	}
	
	
	
	/* register as a plugin in jQuery */
	if (window.jQuery)
		window.jQuery.addPlugin('MapViewer',MapViewer);
	
	
})(); 
/* @file: src\ui\imageviewer.js */ 
(function(){


//var dependency = $.Dependency('//cdn.rawgit.com/exif-js/exif-js/master/exif.js');


var MOBILE_REGEX = /mobile|tablet|ip(ad|hone|od)|android/i;

var SUPPORT_TOUCH = ('ontouchstart' in window);
//var SUPPORT_POINTER_EVENTS = prefixed(window, 'PointerEvent') !== undefined;
var SUPPORT_ONLY_TOUCH = SUPPORT_TOUCH && MOBILE_REGEX.test(navigator.userAgent);



var blobToImage = function(blob){
	// build an image from the blob data
	var urlCreator = window.URL || window.webkitURL;
	var imageUrl = urlCreator.createObjectURL( blob );
	
	var image = new Image();
	image.src = imageUrl;
	return image;
};


var defaultOptions = {
	elements: [], // array of elements to be shown in the gallery, see below for details
	ajax:{
		headers: null, // header to be sent for each http request
		client: null
	},
	index: 0, // the index of the picture to be shown, default to the first one
	navigator:{
		enable: true, // enable the navigator, the navigator is disabled by default if the elements size is 1 or 0
		loadOnAppear: true, // load the thumbnail image only when the thumbnail is visible in the viewport, avoid to load all the thumbnail in the same time
		event: {} // event to be bind on each thumbnail
	},
	preload: false // if true, the previous image and the next one of the current image will be also loaded. 'next' to load only the next one. 'prev' to load only the previous one.
};

var defaultElementOptions = {
	name: null, // string
	content: null, // blob|Image|Resource|string|function(elementOptions) , load the content of the image, (if string ==> url)
	url: null, // string|function(elementOptions)->string , work only if 'content' attribute is not set
	thumbnailUrl: null, // string|function(elementOptions)->string , if not set, no thumbnail will be shown
	meta: null // object , a key-value pairs object of metadata concerning the image to be shown when the user ask to show the property of the image
};



var defaultHttpClient = function(url, options){
	return EThing.request({
		url : url,
		dataType: 'blob',
		headers: options.headers
	});
}

var defaultMeta = function(img){
	var meta = {};
	
	if(img instanceof EThing.File){
		$.extend(meta,{
			'name': img.name(),
			'size' : EThing.utils.sizeToString(img.size()),
			'mime' : img.mime(),
			'created' : EThing.utils.dateToString(img.createdDate()),
			'modified' : EThing.utils.dateToString(img.modifiedDate())
		});
	}
	else if(typeof img == 'string'){ // url
		var url = img;
		$.extend(meta,{
			'name': url.split('/').pop().split('?').shift()
		});
	}
	
	return meta;
}

var getNaturalResolution = function(img, cb){
	if(typeof img.naturalWidth != 'undefined' && img.naturalWidth != 0)
		cb(img.naturalWidth,img.naturalHeight);
	else {
		var i = new Image;
		i.src = img.src;
		
		i.onload = function(){
			cb(this.width,this.height);
		}
	}
}

// cf: https://css-tricks.com/the-javascript-behind-touch-friendly-sliders/
var Slider = function(element, options){
	this.$element = $(element);
	var self = this;
	
	this.options = $.extend(true,{
		change: null
	},options);
	
	this.index = 0;
	
	
	
	var events = {
		start: function (event) {
			self.longTouch = false;
			delete self.movex;
			setTimeout(function () {
				self.longTouch = true;
			}, 250);
			self.touchstartx = event.originalEvent.touches[0].pageX;
			self.$element.removeClass('iv-animate');
		},
		move: function (event) {
			var width = self.width();
			self.touchmovex = event.originalEvent.touches[0].pageX;
			self.movex = self.index * width + (self.touchstartx - self.touchmovex);
			var panx = 100 - self.movex / 6;
			if (self.movex < width*(self.length-1)) {
				self.$element.css('transform', 'translate3d(-' + self.movex + 'px,0,0)');
			}
		},
		end: function (event) {
			if(typeof self.movex == 'undefined') return; // no movement
			var slideWidth = self.width(), index = self.index;
			var absMove = Math.abs(self.index * slideWidth - self.movex);
			if (absMove > slideWidth / 2 || self.longTouch === false) {
				if (self.movex > self.index * slideWidth) {
					index++;
				} else if (self.movex < self.index * slideWidth && self.index > 0) {
					index--;
				}
			}
			self.go(index);
		}
	}
	
	this.update();
	
	this.$element.on('touchstart', function (event) {
		events.start(event);
	});
	this.$element.on('touchmove', function (event) {
		events.move(event);
	});
	this.$element.on('touchend', function (event) {
		events.end(event);
	});
	
	$(window).resize(function(){
		self.redraw();
	});
	
}
Slider.prototype.width = function(){
	return this.$element.width() / this.length;
}
Slider.prototype.update = function(){
	this.length = this.$element.children().length;
	this.$element.css('width',(this.length*100)+'%');
	this.$element.children().css('width',(100/this.length)+'%');
}
Slider.prototype.redraw = function(){
	this.$element.removeClass('iv-animate').css('transform', 'translate3d(-' + this.index * this.width() + 'px,0,0)');
}
Slider.prototype.go = function(index){
	if(index<0) index=0;
	if(index>= this.length) index = this.length-1;
	var change = this.index != index;
	this.index = index;
	this.$element.addClass('iv-animate').css('transform', 'translate3d(-' + this.index * this.width() + 'px,0,0)');
	
	if(change && typeof this.options.change == 'function')
		this.options.change.call(this,index);
}
Slider.prototype.next = function(){
	this.go(this.index+1);
}
Slider.prototype.prev = function(){
	this.go(this.index-1);
}
	
var ImageViewer = function(element,options) {
	
	var self = this;
	
	$.AbstractPlugin.call(this,element,$.extend(true,{},defaultOptions,options));
	
	
	this.$element.empty();
	
	this.$element
		.removeClass('iv-nonav iv-fullscreen')
		.addClass('ImageViewer');
	
	
	this._elements = [];
	
	var $view = $('<div class="iv-view">'),
		$ui = $('<div class="iv-ui">'),
		$meta = $('<div class="iv-meta">').hide(),
		$navigator = $('<div class="iv-navigator">'),
		$header = $('<div class="iv-header">'),
		$title = $('<div class="iv-title">'),
		$actions = $('<div class="iv-actions">');
	
	this.$element.append($view,$ui);
	$ui.append($header,$meta,$navigator);
	$header.append($title, $actions);
	
	$('<span class="glyphicon glyphicon-resize-full iv-action-fullscreen" title="fullscreen" aria-hidden="true">').click(function(){
		self.toggleFullscreen();
	}).appendTo($actions);
	
	$('<span class="glyphicon glyphicon-download iv-action-download" title="download" aria-hidden="true">').click(function(){
		
		
		var $img = self.$element.find('.iv-cntr').children().eq(self.currentIndex()).find('img');
		if($img.length){
			var img = $img[0], element = self.currentElement();
			
			
			
			var hyperlink = document.createElement('a');
			hyperlink.href = img.src;
			hyperlink.target = '_blank';
			hyperlink.download = (element.name || element.meta.name || 'image').replace( /.*\//,'');
			
			
			if (!!navigator.mozGetUserMedia) {
				hyperlink.onclick = function() {
					(document.body || document.documentElement).removeChild(hyperlink);
				};
				(document.body || document.documentElement).appendChild(hyperlink);
			}
			
			//This is true only for IE,firefox
			var evt;
			if(document.createEvent){
			    // To create a mouse event , first we need to create an event and then initialize it.
				evt = document.createEvent("MouseEvent");
				evt.initMouseEvent("click",true,true,window,0,0,0,0,0,false,false,false,false,0,null);
			}
			else{
				 evt = new MouseEvent('click', {
							'view': window,
							'bubbles': true,
							'cancelable': true
						});
			}

			hyperlink.dispatchEvent(evt);

			if (!navigator.mozGetUserMedia) {
				URL.revokeObjectURL(hyperlink.href);
			}
			
		}
		
	}).appendTo($actions);
	
	/*$('<span class="glyphicon glyphicon-info-sign iv-action-toggle-meta" title="info" aria-hidden="true">').click(function(){
		
		var $img = self.$element.find('.iv-view').find('img');
		if($img.length && $img.data('data')){
			dependency.require(function(){
				
				EXIF.getData($img[0], function() {
					console.log(arguments);
					console.log(EXIF.pretty(this));
				});
				
			});
		}
		
		$meta.toggle();
	}).appendTo($actions);*/
	
	$('<span class="glyphicon glyphicon-refresh iv-action-toggle-reload" title="reload" aria-hidden="true">').click(function(){
		
		self.show(self.currentIndex(),true);
		
	}).appendTo($actions);
	
	
	
	$view.append(
		'<div class="iv-cntr">'
	);
	
	this.slider = new Slider(this.$element.find('.iv-cntr'),{
		change: function(index){
			self.show(index);
		}
	});
	
	if(!SUPPORT_TOUCH){
		// add prev and next buttons
		$('<div class="iv-prev"><span class="glyphicon glyphicon-chevron-left" aria-hidden="true"></span></div>').click(function(e){
			self.previous();
			e.stopPropagation();
			return false;
		}).prependTo($view);
		$('<div class="iv-next"><span class="glyphicon glyphicon-chevron-right" aria-hidden="true"></span></div>').click(function(e){
			self.next();
			e.stopPropagation();
			return false;
		}).appendTo($view);
	}
	
	
	if(this.options.navigator.enable){
		
		EThing.utils.require('//cdnjs.cloudflare.com/ajax/libs/jquery-mousewheel/3.1.13/jquery.mousewheel.min.js',function(){
			$navigator.mousewheel(function(event, delta) {
				if($navigator.css('overflow-x')!=='hidden'){
					this.scrollLeft -= (delta * 60);
					event.preventDefault();
				}
			});
		});
	
		// load thumbnail only when visible
		if(this.options.navigator.loadOnAppear){
			var check_lock = false;
			var appear_offset = 128;
			var checkVisible = function(){
				if (check_lock) {
					return;
				}
				check_lock = true;
				
				setTimeout(function(){
					check_lock = false;
					$navigator.children().each(function(i){
						
						// is visible ?
						var $element = $(this),
							state = $element.data('state');
						if (state===1 || !$element.is(':visible'))
							return;

						var offset = $element.position();
						var left = offset.left;
						var top = offset.top;
							
						if (
							left + $element.width() + appear_offset >= 0 &&
							left - appear_offset <= $navigator.width() &&
							top + $element.height() + appear_offset >= 0 &&
							top - appear_offset <= $navigator.height()
						) {
							$element.data('state',1);
							$element.trigger('appear');
						}
							
						
					});
				}, 250);
			}
			$navigator.scroll(checkVisible);
			$(window).resize(checkVisible);
		}
		
	}
	
	// cached image loader
	
	this._loadImage = EThing.utils.createCache(function(url) {
		var options = self.options.ajax;
		return typeof options.client == 'function' ? options.client(url,options) : defaultHttpClient(url,options);
	});
	
	
	setTimeout(function(){
		
		self.setItems(self.options.elements, self.options.index);		
		
	},1)

};


ImageViewer.prototype.setItems = function(items, index){
	
	var self = this,
		$cntr = this.$element.find('.iv-cntr'),
		$navigator = this.$element.find('.iv-navigator');
	
	// clear
	this._elements = [];
	$cntr.empty();
	$navigator.empty();
	
	
	
	if(!$.isArray(items))
		items = [items];
	
	var showNavigator = this.options.navigator.enable && items.length>1;
	
	if(!showNavigator)
		// no navigator
		this.$element.addClass('iv-nonav');
		
	items.forEach(function(el, index){
		
		var $item = $('<div class="iv-item">').appendTo($cntr);
		
		if(!$.isPlainObject(el))
			el = {
				content: el
			};
		
		var element = $.extend(true,{},defaultElementOptions, el);
		
		if(!element.content)
			element.content = element.url;
		
		element.meta = $.extend({}, defaultMeta(element.content), element.meta);
		
		if(!element.thumbnailUrl && element.thumbnailUrl!==false){
			if(element.content instanceof EThing.File)
				element.thumbnailUrl = element.content.thumbnailLink();
		}
		
		$item.html('<div>'+(element.name || element.meta.name)+'</div>');
		
		element.state = 'pending';
		
		function setError(evt){
			
			$item.removeClass('iv-vertical-align').html('<div class="error">error: '+(e && e.message ? e.message : (e || 'unknown'))+'</div>');
			element.state = 'error';
			
			if(typeof callback == 'function')
				callback.call(self,element);
		}
		
		function asyncload(dfr, callback){
			dfr
				.done(function(img){
					setImage(img, callback);
				})
				.fail(setError)
				.progress(function(evt){
					if (evt.lengthComputable)
						$('.loader',$item).html(Math.round((evt.loaded / evt.total)*100)+'% loaded');
				});
		}
		
		function setImage(img, callback){
			
			if($.isPlainObject(img) && typeof img.promise == 'undefined'){ // an element object
				$.extend(true,element,img); // extend the actual property
				img = element.content;
			}
			
			$.extend(element.meta, defaultMeta(img)); // update the meta data
			
			if(typeof img == 'string'){ // url
				return asyncload( self._loadImage(img), callback );
			}
			else if(img instanceof EThing.File){
				return asyncload( img.binaryRead(), callback );
			}
			else if(img instanceof Blob){
				img = blobToImage(img);
			}
			else if(typeof img.promise == 'function'){ // a deferred object
				return asyncload(img, callback);
			}
			
			
			var $image = $(img);
			
			$image.on('error',setError);
			
			$image.click(function(evt){
				if(!self.isFullscreen()){
					self.toggleFullscreen();
					evt.stopPropagation();
				}
			});
			
			$item.addClass('iv-vertical-align').html($image);
			
			// update meta information
			getNaturalResolution(img,function(width,height){
				var meta = $.extend(element.meta, {
					width: width+'px',
					height: height+'px'
				});
			});
			
			element.state = 'loaded';
			
			if(typeof callback == 'function')
				callback.call(self,element);
			
			if(typeof element.onload == 'function')
				element.onload.call(element);
			
		}
		
		element.load = function(callback){
			
			$item.html('<div>'+(element.name || element.meta.name)+'<div class="loader">0% loaded</div></div>');
			
			element.state = 'loading';
			
			$item.removeClass('iv-vertical-align');
			
			var content = (typeof element.content == 'function') ? element.content.call(self,element) : element.content;
			
			if(!content)
				content = typeof element.url == 'function' ? element.url.call(self,element) : element.url;
			
			setImage(content,callback);
			
		}
		
		
		// navigator
		if(showNavigator){
			var $d = $('<div>')
				.append('<span class="glyphicon glyphicon-picture" aria-hidden="true">');
			
			if(!SUPPORT_ONLY_TOUCH)
				$d.tooltip({
					container: this.$element,
					trigger:'hover',
					placement: 'top',
					title: function(){
						return (element.name || element.meta.name || 'untitled').replace( /.*\//,'');
					}
				})
				.on('show.bs.tooltip',function(e,a){
					// if the navigator is in the right, show the tooltip on the left
					$d.data('bs.tooltip').options.placement = $navigator.css('overflow-x')==='hidden' ? 'left' : 'top';
				});
			
			$d.click(function(evt){
				if(self.currentIndex() != index)
					self.show(index);
				evt.stopPropagation();
				evt.preventDefault();
				return false;
			});
			
			if(self.options.navigator.event)
				for(var e in self.options.navigator.event)
					$d.on(e,self.options.navigator.event[e]);
			
			$navigator.append($d);
			
			element.$nav = $d;
		}
		
		
		this._elements.push(element);
		
	}, this);
	
	
	
	this.slider.update();
	
	
	if(this._elements.length){
		// show the first picture
		this.show(index || 0, false, function(){
			
			//load the thumbnails only after the first image was loaded
			if(showNavigator){
				self._elements.forEach(function(element, index){
					
					var thumbnailUrl = typeof element.thumbnailUrl == 'function' ? element.thumbnailUrl.call(self,element) : element.thumbnailUrl;
					
					if(typeof thumbnailUrl == 'string'){
						
						var show = function(){
							self
								._loadImage(thumbnailUrl)
								.done(function(blob){
									var $image = $(blobToImage(blob));
									
									element.$nav.html($image);
								});
						};
						
						if(self.options.navigator.loadOnAppear)
							element.$nav.on('appear',show);
						else
							show();
					}
					
				}, self)
				
				$navigator.trigger('scroll');
			}
			
		});
	} else {
		// empty !
	}
	
}
ImageViewer.prototype.show = function(index, forceRefresh, callback){
	var self = this;
	
	if(index < 0 || index >= this._elements.length)
		return this; // invalid index !
	
	var element = this._elements[index];
	if(!element)
		return this;
	
	var $title = $('.iv-header>.iv-title',this.$element).html(element.name || element.meta.name || 'loading...');
	
	var hasNext = index < (this._elements.length - 1);
	var hasPrevious = index > 0;
	
	$('.iv-next',this.$element).toggle(hasNext);
	$('.iv-prev',this.$element).toggle(hasPrevious);
	
	var onload = function(){
		
		if(typeof callback == 'function')
			callback.call(self,element);
		
		// pre load the next image
		if(hasNext && (self.options.preload===true || /next/i.test(self.options.preload))){
			var nextElement = self._elements[index+1];
			if(nextElement.state === 'pending')
				nextElement.load();
		}
		// pre load the previous image
		if(hasPrevious && (self.options.preload===true || /prev/i.test(self.options.preload))){
			var prevElement = self._elements[index-1];
			if(prevElement.state === 'pending')
				prevElement.load();
		}
		
		self.trigger('shown.imageviewer',[element,index]);
	}
	
	this.index = index;
	
	if(this.slider.index != this.index)
		this.slider.go(this.index);
	
	this.trigger('show.imageviewer',[element,index]);
	
	if(element.state === 'pending' || (forceRefresh && element.state != 'loading'))
		element.load(function(element){
			if(self.index != index) return;
			
			// update title
			$title.text(element.name || element.meta.name || 'untitled');
			
			onload();
		});
	else if(element.state === 'loading'){
		var p_onload = element.onload || null;
		element.onload = function(){
			this.onload = p_onload;
			onload();
		}
	}
	else if(element.state === 'loaded')
		onload();
	
	
	return this;
}
ImageViewer.prototype.currentIndex = function(){
	return this.index;
}
ImageViewer.prototype.next = function(){
	return this.show(this.currentIndex()+1);
}
ImageViewer.prototype.previous = function(){
	return this.show(this.currentIndex()-1);
}
ImageViewer.prototype.currentElement = function(){
	return this._elements[this.currentIndex()];
}
ImageViewer.prototype.isFullscreen = function(){
	return this.$element.hasClass('iv-fullscreen');
}
ImageViewer.prototype.toggleFullscreen = function(state){
	var isFullscreen = this.isFullscreen(),
		self = this;
	
	if(typeof state != 'undefined' && state == isFullscreen)
		return;
	
	var $view = this.$element.find('.iv-view'),
		$ui = this.$element.find('.iv-ui, .iv-prev>span, .iv-next>span');
	
	
	function showAutoHide(){
		$ui.fadeIn(400);
		if(self.fsuito) clearTimeout(self.fsuito);
		self.fsuito = setTimeout(function(){
			$ui.fadeOut(400); // auto hide the ui layer after a N seconds
		},5000);
	}
	
	if(!this._keyupHandler){
		this._keyupHandler = function(e) {
			 e.preventDefault();
		     e.stopImmediatePropagation();
			 if (e.keyCode == 27){ // escape key maps to keycode `27`
				self.toggleFullscreen(false);
			 }
			 else if(e.keyCode == 37){
				self.previous();
			 }
			 else if(e.keyCode == 39){
				self.next();
			 }
			 return false;
		};
	}
	if(!this._showHandler){
		this._showHandler = function(e) {
			if(e.type == "mousemove" && self._mousemoveCoord && self._mousemoveCoord.x == e.pageX && self._mousemoveCoord.y == e.pageY) return;
			self._mousemoveCoord = {
				x: e.pageX,
				y: e.pageY
			};
			showAutoHide();
		};
	}
	if(!this._exitHandler){
		this._exitHandler = function(e) {
			self.toggleFullscreen(false);
		};
	}
	
	this.$element.toggleClass('iv-fullscreen',!isFullscreen);
	
	$(document.body).toggleClass('iv-fullscreen',!isFullscreen);
	
	// force resize
	$(window).resize();
	
	
	if(isFullscreen){
		$(document).off("keyup",this._keyupHandler);
		this.$element.off("mousemove",this._showHandler);
		this.$element.find('.iv-navigator').off("scroll",this._showHandler);
		$view.off("click",this._showHandler);
		$view.off("dblclick",this._exitHandler);
		if(this.fsuito) clearTimeout(this.fsuito);
		$ui.show();
	}
	else {
		// make it fullscreen
		$(document).on("keyup",this._keyupHandler);
		this.$element.on("mousemove",this._showHandler);
		this.$element.find('.iv-navigator').on("scroll",this._showHandler);
		$view.on("click",this._showHandler);
		$view.on("dblclick",this._exitHandler);
		showAutoHide();
	}
	
	// update action icon
	if(self.isFullscreen())
		self.$element.find('.iv-action-fullscreen').addClass('glyphicon-resize-small').removeClass('glyphicon-resize-full');
	else
		self.$element.find('.iv-action-fullscreen').removeClass('glyphicon-resize-small').addClass('glyphicon-resize-full');
}


/* register as a plugin in jQuery */
if (window.jQuery)
	window.jQuery.addPlugin('ImageViewer',ImageViewer);


})(); 
/* @file: src\ui\graph.js */ 
(function(){


var dependency = $.Dependency({
	url: '//code.highcharts.com/stock/highstock.js',
	then: '//code.highcharts.com/stock/modules/exporting.js'
});


// the second arg must be a Table resource or an option object 
var Graph = function(element, options) {
	
	$.AbstractPlugin.call(this,element);
	
	
	this.$element.empty().addClass('Graph')
	
	var _defaultOpt = {
			/* internal */
			splitInPanes: false,
			highstock: true,
			
			/* highcharts */
			chart: {
				type: 'spline',
				zoomType: 'x'
			},
			rangeSelector : {
                buttons: [{
                    type: 'day',
                    count: 1,
                    text: 'Day'
                }, {
                    type: 'day',
                    count: 7,
                    text: 'Week'
                }, {
                    type: 'month',
                    count: 1,
                    text: 'Month'
                }, {
                    type: 'all',
                    text: 'All'
                }],
                buttonTheme: {
                    width: 60
                },
                selected: 0
            },
			title: {
				text: null
			},
			navigator : {
				enabled : true
			},
			xAxis: {
				type: 'datetime',
				title: {
					text: 'time'
				},
				ordinal: false
			},
			plotOptions: {
				spline: {
					marker: {
						enabled: true
					}
				}
			},
			series: [],
			yAxis: [],
			credits: {
				enabled: false
			},
			exporting:{
				buttons:{
					contextButton:{
						menuItems: null
					}
				}
			},	
			navigation: {
				menuItemStyle: {
					fontWeight: 'normal',
					background: 'none'
				},
				menuItemHoverStyle: {
					fontWeight: 'bold',
					background: 'none',
					color: 'black'
				}
			}
		},
		_defaultyAxis = {
			alternateGridColor: '#FDFFD5'
		},
		_defaultSerie = {
		
		},
		_opt = null,
		_self = this;





	var loader = function() {
		return $('<div style="text-align: center;margin: 40px;">loading ...</div>');
	}

	var printError = function(message){
		this.$element.empty().append('<div style="margin:10px;">'+message+'</div>');
		throw message;
	}


	this.open = function(options) {
		
		var self = this;
		
		if(options instanceof EThing.Table)
			options = Graph.defaultOptionsFromTable(options);
		
		_opt = $.extend(true,{}, _defaultOpt, options);
		
		if (!_opt.series || _opt.series.length == 0) {
			printError('no series to plot.');
			return;
		}
		
		var navigatorSeries = [], hasNavigator = _opt.navigator.enabled;
		
		var $loader = loader().appendTo(this.$element.empty());
		
		// extend default
		for(var i=0; i<_opt.series.length; i++)
			_opt.series[i] = $.extend(true,{},_defaultSerie,_opt.series[i]);
		for(var i=0; i<_opt.yAxis.length; i++)
			_opt.yAxis[i] = $.extend(true,{},_defaultyAxis,_opt.yAxis[i]);
		
		
		
		
		
		
		var instanciate = function(){
			$loader.remove();
			
			Highcharts.setOptions({
				global: {
					useUTC: false
				}
			});
			
			
			/*
			Update the menu
			*/
			
			var popupOptions = function () {
				
				$('<div>')
					.graphWizard(options)
					.modal({
						title: "Graph ...",
						buttons: {
							'+graph': function(){
								var $this = $(this);
								$this.graphWizard().validate(function(options){
									$this.modal('hide',function(){
										new Graph(element, options);
									});
								});
								return false;
							},
							'Cancel': null
						}
					});
			};
			
			_opt.exporting.buttons.contextButton.menuItems = [].concat({
				text: 'Options',
				onclick: popupOptions
			}, _opt.exporting.buttons.contextButton.menuItems || Highcharts.getOptions().exporting.buttons.contextButton.menuItems);
			
			
			try {
				
				if(hasNavigator)
					$.extend(true,_opt,{
						navigator:{
							series: {
								data: navigatorSeries[0],
								type: 'spline'
							}
						}
					});
				
				var $g = $('<div class="chart"></div>')
					.appendTo(self.$element)
					.highcharts( _opt.highstock ? 'StockChart' : 'Chart',_opt,function(chart){
						
						if(hasNavigator)
							for(var i=1; i<navigatorSeries.length; i++)
								chart.addSeries({
									enableMouseTracking: false,
									data: navigatorSeries[i],
									xAxis:'navigator-x-axis',
									yAxis: 'navigator-y-axis',
									name: null,
									isInternal: true,
									showInLegend: false,
									color: chart.series[i].color,
									type: 'spline',
									fillOpacity: 0.05,
									dataGrouping: {
										smoothed: true
									},
									lineWidth: 1,
									marker: {
										enabled: false
									}
								});
						
					});
			}
			catch(e){
				console.log(e);
				self.$element.html(e);
			}
			
		};
		
		var isRSerie = function(serie){
			return $.isPlainObject(serie.data) && serie.data.hasOwnProperty('tableId') && serie.data.hasOwnProperty('field');
		}
		
		// download the necessary data
		
		var seriesForDL = [];
		for(var i=0; i<_opt.series.length; i++){
			if(isRSerie(_opt.series[i])){
				seriesForDL.push({
					tableId: _opt.series[i].data.tableId,
					field: _opt.series[i].data.field,
					length: _opt.series[i].data.length,
					query: _opt.series[i].data.query
				});
			}
		}
		DataLoader(seriesForDL,function(results){
			
			// all the data are loaded
			
			// replace the table/field object by its data
			for(var i=0; i<_opt.series.length; i++){
				
				if(isRSerie(_opt.series[i]))
					_opt.series[i].data = results[i].data;
				
				var data = _opt.series[i].data;
				
				// if empty data, remove this serie
				if(!data || !data.length){
					var removedSerie = _opt.series.splice(i, 1)[0];
					i--;
					
					// remove this yAxis if not shared with another serie
					var sharedyaxis = false;
					for(var j=0; j<_opt.series.length; j++)
						if(_opt.series[j].yAxis === removedSerie.yAxis){
							sharedyaxis = true;
							break;
						}
					if(!sharedyaxis){
						for(var j=0; j<_opt.yAxis.length; j++)
							if(_opt.yAxis[j].id === removedSerie.yAxis){
								_opt.yAxis.splice(j, 1);
								break;
							}
					}
					
					continue;
				}
				
				// create navigators series
				if(hasNavigator){
					// normalize
					var max = null, min = null, navdata = [], sampling = data.length > 100 ? Math.round(data.length / 100) : 1;
					for(var j=0; j<data.length; j++){
						if(j%sampling != 0)
							continue;
						if(max===null || data[j][1] > max)
							max = data[j][1];
						if(min===null || data[j][1] < min)
							min = data[j][1];
					}
					if(min === max){
						min -= 1;
						max += 1;
					}
					for(var j=0; j<data.length; j++){
						if(j%sampling != 0)
							continue;
						navdata.push([
							data[j][0],
							(data[j][1] - min) / (max - min)
						]);
					}
					navigatorSeries.push(navdata);
				}
			}
			
			// split in panes
			if(_opt.splitInPanes){
				var marge = 5, // vertical space between 2 panes (in %)
					N = _opt.yAxis.length;// number of panes
				
				var panesHeight = (100-(N-1)*marge)/N;
				_opt.yAxis.forEach(function(yAxe, index){
					yAxe.height = panesHeight+'%';
					yAxe.top = (index*(panesHeight+marge))+'%';
					yAxe.offset = 0;
				});
				
			}
			
			// load the highcharts library
			dependency.require(instanciate);
			
		});

	};

	this.options = function(){
		return _opt;
	};
	
	this.chart = function(){
		return self.$element.children('.chart').highcharts();
	};

	this.open(options);

};

Graph.defaultOptionsFromTable = function(table, keysToPlot, length, query){
	
	if(arguments.length < 4 && arguments.length > 1 && typeof keysToPlot == 'number'){
		query = length;
		length = keysToPlot;
		keysToPlot = null;
		if(typeof query == 'undefined' && typeof length == 'string'){
			query = length;
			length = null;
		}
	}
	
	var opt = {
		splitInPanes: true,
		title: {
			text: table.name()
		},
		series:[],
		yAxis:[]
	};
	
	var keys;
	if(Array.isArray(keysToPlot) && keysToPlot.length)
		keys = keysToPlot;
	else if (typeof keysToPlot == 'string')
		keys = [keysToPlot];
	else
		keys = table.keys();
	
	
	
	for(var i=0; i<keys.length; i++){
		
		var key = keys[i],
			axisId = 'axis'+i;
		
		opt.series.push({
			data: {
				tableId: table.id(),
				field: key,
				length: length,
				query: query
			},
			yAxis: axisId,
			name: key
		});
		
		opt.yAxis.push({
			id: axisId,
			title: {
				text: key
			}
		});
		
	}
	
	
	return opt;
}

/*
preset = {
	
	yAxis: [
		{
			id: "axis0",
			title: "field1"
		},
		...
	],
	series: [
		{
			data: {
				tableId: "tableId",
				field: "fieldName"
			},
			yAxis: "axis0"
		},
		...
	]
	
}
*/
var GraphWizard = function(element, preset) {
	
	$.AbstractPlugin.call(this,element);
	
	
	if(preset instanceof EThing.Table)
		preset = Graph.defaultOptionsFromTable(preset);
	
	preset = $.extend({
		series:[{}],
		yAxis:[{}]
	},preset);
		
	
	var MAX_SERIES = 5;
	var MAX_YAXIS = 5;
	
	this.$element.html(
	  '<ul class="nav nav-tabs" role="tablist">'+
		'<li role="presentation" class="active"><a href="#series" aria-controls="series" role="tab" data-toggle="tab">Series</a></li>'+
		'<li role="presentation"><a href="#yaxis" aria-controls="yaxis" role="tab" data-toggle="tab">y-Axis</a></li>'+
		'<li role="presentation"><a href="#appearance" aria-controls="appearance" role="tab" data-toggle="tab">Appearance</a></li>'+
	  '</ul>'+
	  '<div class="tab-content">'+
		'<div role="tabpanel" class="tab-pane active" id="series"><div id="series-list" style="margin:20px 0;"></div></div>'+
		'<div role="tabpanel" class="tab-pane" id="yaxis"><div id="yaxis-list" style="margin:20px 0;"></div></div>'+
		'<div role="tabpanel" class="tab-pane" id="appearance" style="margin:20px 0;"></div>'+
	  '</div>'
	);
	
	var yaxisIndex = 0,
		seriesIndex = 0,
		$series = function(){
			return $('div.serie',$('#series-list',self.$element));
		},
		$yaxis = function(){
			return $('div.yAxis',$('#yaxis-list',self.$element));
		},
		self = this;
	
	this.addSerie = function(value){
		
		var $form = $('<div>').form({
			'name':{
				input: 'text',
				validator: $.Form.validator.NotEmpty
			},
			'data': new $.Form.TableFieldSelect({
				onChange: function(table,field){
					var item = this.form().findItem('name');
					if(item)
						item.setValue(field);
				}
			}),
			'yAxis':{
				input: '<select>',
				attr: {
					name: "yaxis"
				},
				get: function($e){
					var v = $e.val();
					if(v===null || v=="_")
						throw "no y-Axis selected";
					
					return String(v);
				}
			},
			'type':{
				input: ['line','spline','area','areaspline','column','scatter']
			}
			
		});
		
		var form = $form.form();
		
		var $serieHtml = $('<div class="panel panel-default serie">').append(
			$('<div class="panel-heading"></div>').append(
				'Serie #'+(++seriesIndex),
				$('<span class="glyphicon glyphicon-trash" aria-hidden="true"></span>').css({
					float: 'right',
					cursor: 'pointer'
				}).click(function(){
					// self destruction !
					$serieHtml.remove();
					update();
				})
			),
			$('<div class="panel-body">').append($form)
		).appendTo($('#series-list',this.$element)).data('form',form).data('id',seriesIndex).attr('name',seriesIndex);
		
		update();
		
		if(value)
			form.setValue(value);
		
		return form;
	};
	
	this.addyAxis = function(value){
		
		var $form = $('<div>').form(new $.Form.FormLayout([{
			name: 'title',
			item: {
				input: function(){
					return $('<input type="text">').change(update);
				},
				get: function($e){
					var v = $e.val().trim();
					if(!v)
						throw "the name must not be empty";
					return {text:v};
				},
				set:function($e,v){
					if(typeof v == 'string')
						$e.val(v);
					else if($.isPlainObject(v) && v.hasOwnProperty('text')){
						$e.val(v.text);
					}
				},
				value: "a.u."
			}
		},{
			name: 'id',
			item: {
				input: 'text',
				value: "axis"+yaxisIndex
			},
			hidden: true
		}]));
		
		var form = $form.form();
		
		if(value)
			form.setValue(value);
		
		var $yAxisHtml = $('<div class="panel panel-default yAxis">').append(
			$('<div class="panel-heading"></div>').append(
				'Y-Axis #'+(yaxisIndex+1),
				$('<span class="glyphicon glyphicon-trash" aria-hidden="true"></span>').css({
					float: 'right',
					cursor: 'pointer'
				}).click(function(){
					// self destruction !
					$yAxisHtml.remove();
					update();
				})
			),
			$('<div class="panel-body">').append($form)
		).appendTo($('#yaxis-list',this.$element)).data('form',form).data('id',yaxisIndex).attr('name',yaxisIndex);
		
		yaxisIndex++;
		
		update();
		
		return form;
	};
	
	var update = function(){
		
		// 1 - list the available y-Axis
		var $options = ['<option selected disabled value="_">select ...</option>'];
		$yaxis().each(function(){
			
			var id = $(this).data('id'),
				form = $(this).data('form'),
				titleItem = form.findItem('title'),
				name = titleItem.getValue().text;
			
			$options.push('<option value="axis'+id+'">#'+(id+1)+(name.length ? ' ['+name+']' : '')+'</option>');
		});
		
		
		// update the yaxis select element
		$series().each(function(){
			var form = $(this).data('form'),
				$input = form.findItem('yAxis').input(),
				save = $input.val();
			$input.empty().append($options).val(save);
		});
		
		
		// update other things
		if($series().length>MAX_SERIES)
			$('#series-add',self.$element).hide();
		else
			$('#series-add',self.$element).show();
		
		
		if($yaxis().length>MAX_YAXIS)
			$('#yaxis-add',self.$element).hide();
		else
			$('#yaxis-add',self.$element).show();
		
	}
	
	
	$('#series',this.$element).append($('<div id="series-add" style="cursor: pointer;color: #5CAEF2;">+ Add a serie</div>').click(function(){self.addSerie();}));
	$('#yaxis',this.$element).append($('<div id="yaxis-add" style="cursor: pointer;color: #5CAEF2;">+ Add an Y-Axis</div>').click(function(){self.addyAxis();}));
	
	
	
	
	
	// appearance
	
	var $formAppearance = $('#appearance',this.$element).form(new $.Form.FormLayout([{
		name: 'title',
		item: {
			input: 'text',
			validator: $.Form.validator.NotEmpty,
			set:function($e,v){
				if(typeof v == 'string')
					$e.val(v);
				else if($.isPlainObject(v) && v.hasOwnProperty('text')){
					$e.val(v.text);
				}
			}
		},
		checkable:true,
		checked:false
	},{
		name: 'subtitle',
		item:{
			input: 'text',
			validator: $.Form.validator.NotEmpty,
			set:function($e,v){
				if(typeof v == 'string')
					$e.val(v);
				else if($.isPlainObject(v) && v.hasOwnProperty('text')){
					$e.val(v.text);
				}
			}
		},
		checkable:true,
		checked:false
	}]));
	
	var formAppearance = $formAppearance.form();
	
	
	
	this.validate = function(callback){
		
		var data = {
			splitInPanes: true,
			series:[],
			yAxis:[]
		},
		self=this,
		yAxisAvailableList = [],
		promises = [];
		
		// validate the yaxis
		$yaxis().each(function(){
			promises.push(
				$(this).data('form').validate().done(function(d){
					yAxisAvailableList.push(d);
				})
			);
		});
		
		// validate the series
		$series().each(function(){
			promises.push(
				$(this).data('form').validate().done(function(d){
					// is the yAxis used already in the list ?
					var inList = false;
					for(var i=0; i<data.yAxis.length; i++)
						if(data.yAxis[i].id === d.yAxis){
							inList = true;
							break;
						}
					if(!inList){
						// add the yaxis
						for(var i=0; i<yAxisAvailableList.length; i++)
							if(yAxisAvailableList[i].id === d.yAxis){
								data.yAxis.push(yAxisAvailableList[i]);
								break;
							}
					}
					data.series.push(d);
				})
			);
		});
		
		
		promises.push(
			formAppearance.validate().done(function(d){
				$.extend(data,d);
			})
		);
		
		$.when.apply($, promises).done(function() {
			if(typeof callback == 'function'){
				callback.call(self,data);
			}
		})
	};
	
	
	
	
	if(preset){
		
		if($.isArray(preset.yAxis))
			for(var i=0; i<preset.yAxis.length; i++)
				this.addyAxis(preset.yAxis[i]);
		
		if($.isArray(preset.series))
			for(var i=0; i<preset.series.length; i++)
				this.addSerie(preset.series[i]);
		
		// other
		formAppearance.setValue(preset);
	}
	
};


var GraphSimpleWizard = function(element, table) {
	
	$.AbstractPlugin.call(this,element);
	
	this.$element.addClass('SimpleGraphBuilder');
	
	var keys = table.keys();
	
	var $fields = $('<div>').appendTo(this.$element);
	for(var i=0; i<keys.length; i++){
		var $row = $('<div>').append('<label><input type="checkbox" data-value="'+encodeURIComponent(keys[i])+'"> '+keys[i]+'</label>').appendTo($fields);
	}
	
	this.$message = $('<div class="alert alert-danger" role="alert">').hide().appendTo(this.$element);
	
	this.validate = function(callback){
		this.$message.hide();
		
		// get the selected fields
		var selectedFields = [];
		this.$element.find('input[type="checkbox"]:checked').each(function(){
			selectedFields.push( decodeURIComponent($(this).attr('data-value')) );
		});
		
		
		if( selectedFields.length == 0 ){
			this.$message.html('Please, select at least one field').show();
			return;
		}
		
		var opt = Graph.defaultOptionsFromTable(table, selectedFields);
		
		if(typeof callback == 'function'){
			callback.call(this,opt);
		}
		
		return opt;
	};
	
	
}



var DataLoader = function(series, callback){
	
	series = series || [];
	
	var requests = [],
		map = [],
		deferreds = [],
		self = this;
	
	
	for(var i=0; i<series.length; i++){
		
		var serie = $.extend({
			// length must be a number :  if n > 0 it will return the n last values
			//                            if n < 0 it will return the n first values
			//                            if n == 0 it will return all the values
			length: 0,
			query: null
		},series[i]);
		
		// new request ? 
		var index = null;
		for(var j=0; j<requests.length; j++){
			var request = requests[j];
			if(request.tableId === serie.tableId && request.query == serie.query && serie.length == request.length){
				// use this request for getting the data of this serie too
				// extend the fields
				request.fields.push(serie.field);
				index = j;
				break;
			}
		}
		
		if(index===null){
			// create a new one !
			requests.push({
				tableId: serie.tableId,
				fields:[serie.field],
				length: serie.length, 
				query: serie.query,
				data:null,
				status: "wait"
			});
			index = requests.length - 1;
		}
		
		map.push(index);
		
	}
	
	
	for(var i=0; i<requests.length; i++){
		var request = requests[i],
			dfr = EThing.Table.select(request.tableId, {
				fields: ['date'].concat(request.fields),
				query: request.query,
				start: request.length==0 ? null : -request.length
			});
		
		deferreds.push(dfr);
	}
	
	
	$.when.apply($, deferreds).always(function(a,b,c) {
		
		var d = [], results = [];
		
		if(deferreds.length == 1)
			d.push(arguments[0]);
		else if(deferreds.length>1)
			for(var i=0; i<arguments.length; i++)
				d.push(arguments[i][0]);
		
		for(var i=0; i<requests.length; i++){
			var request = requests[i];
			if(d[i]!==null){
				request.data = d[i] || [];
				request.status = "done";
			}
			else
				request.status = "error";
		}
		
		for(var i=0; i<series.length; i++){
			var serie = series[i],
				request = requests[map[i]],
				field = serie.field,
				data = [];
			
			if(request.status == "done"){
				for(var j=0; j<request.data.length; j++){
					var point = request.data[j],
						val = parseFloat(point[field]);
					if(!isNaN(val))
						data.push([Date.parse(point['date']), val]);
				}
			}
			else
				data = null;
			
			results.push($.extend({},serie,{
				data: data
			}));
			
		}
		
		if(typeof callback == 'function')
			callback(results);
	});
	
	
	
	
};



/* register as a plugin in jQuery */
if (window.jQuery) {
	window.jQuery.addPlugin('Graph',Graph);
	window.jQuery.addPlugin('GraphSimpleWizard',GraphSimpleWizard);
	window.jQuery.addPlugin('GraphWizard',GraphWizard);
}



})();
 
/* @file: src\ui\deviceviewer.js */ 
(function(){

// necessary to work with ba-bbq
jQuery.browser = jQuery.browser || {};
(function () {
	jQuery.browser.msie = jQuery.browser.msie || false;
	jQuery.browser.version = jQuery.browser.version || 0;
	if (navigator.userAgent.match(/MSIE ([0-9]+)\./)) {
		jQuery.browser.msie = true;
		jQuery.browser.version = RegExp.$1;
	}
})();



var dependency = $.Dependency({
	base: '//cdn.rawgit.com/swagger-api/swagger-ui/v2.2.0/dist',
	url:[
		/*'css/reset.css',*/
		/* 'css/screen.css', */
		'lib/jquery.slideto.min.js',
		'lib/jquery.wiggle.min.js',
		'lib/jquery.ba-bbq.min.js',
		'lib/handlebars-4.0.5.js',
		'lib/js-yaml.min.js',
		'lib/lodash.min.js',
		{
			url: 'lib/highlight.9.1.0.pack.js',
			then: 'lib/highlight.9.1.0.pack_extended.js'
		},
		'lib/jsoneditor.min.js',
		'lib/marked.js'
	],
	then:{
		url:[
			'lib/backbone-min.js',
		],
		then: [
			'swagger-ui.min.js',
			'lib/swagger-oauth.js'
		]
	}
},function(){
	// some defaults :
	
	hljs.configure({
		highlightSizeThreshold: 5000
	});
	
	JSONEditor.defaults.options.theme = 'bootstrap3';
});


	
	
	




/**
* Simplify the swagger ui view
*/
function customize(instance){
	
	var $element = instance.$element,
		device = instance.getDevice();
	
	$('#swagger-ui-container > .info', $element).addClass('container');
	
	$('#swagger-ui-container > .info > .info_title', $element).append(
		'<a target="_blank" href="explore.html#!device:'+device.id()+'">[device: '+device.name()+']</a>'
	);
	
	
	
	$('tbody.operation-params>tr',$element).each(function(){
		var $tr = $(this), $tds = $tr.children('td');
		
		var name = $tds.eq(0).text(),
			description = $tds.eq(2).text(),
			$input = $tds.eq(1),
			required = $tds.eq(0).hasClass('required');
		
		if(required)
			$tr.addClass('required');
		
		$input.addClass('keep');
		
		$tr.prepend(
			'<td class="keep" data-type="name">'+name+'</td>',
			'<td class="keep markdown" data-type="description">'+description+'</td>'
		);
		
	});
	
	$('.operation>.content>form>table>tbody',$element).each(function(){
		
		var $tbody = $(this), classnames = $(this).attr('class');
		
		var $table = $tbody.closest('table'), $prev = $table.prev();
		if(!/(^| )operation-params($| )/i.test(classnames)){
			// hide
			$table.hide();
		}
		// also hide the title section
		if($prev.is('h1,h2,h3,h4,h5,h6'))
			$prev.hide();
		
	});
	
	$('.operation>.content>h4:contains("Implementation Notes")',$element).hide();
	
	$('.operation-params .parameter-content-type',$element).prev().filter('br').remove();
	
	$('input:not([type="submit"]):not([type="button"]), select, textarea',$element).filter(':not(.form-control)').addClass('form-control');
	
	$('button, input[type="button"], input[type="submit"]',$element).filter(':not(.btn)').addClass('btn btn-default');
	
	$('.response_throbber',$element).text('loading...');
}




function DeviceViewer(element,opt){
	
	var self = this;
	
	if(opt instanceof EThing.Device)
		opt = {
			device: opt
		};
	
	$.AbstractPlugin.call(this,element,opt);
	
	
	this.$element.addClass('swagger-section').html('<div class="loader">loading...</div>');
	
	$.when(
		this.getDevice().getDescriptor(),
		dependency.require()
	).done(function(){
		
		var spec = arguments[0][0];
		
		
		if(window.swaggerUi) delete window.swaggerUi;
		
		
		self.$element.empty().addClass('swagger-section').append(
			'<div id="message-bar" class="swagger-ui-wrap">&nbsp;</div>'+
			'<div id="swagger-ui-container" class="swagger-ui-wrap"></div>'
		);
		
		window.swaggerUi = new SwaggerUi({
			spec: spec,
			client: EThing.utils.ethingHTTPSwaggerClient,
			dom_id: "swagger-ui-container",
			supportedSubmitMethods: ['get', 'post', 'put', 'delete', 'patch'],
			validatorUrl: null, // disable validation
			onComplete: function(swaggerApi, swaggerUi){
				customize(self);
			},
			onFailure: function(data) {
				console.log("Unable to Load SwaggerUI");
			},
			docExpansion: "list",
			jsonEditor: true,
			defaultModelRendering: 'schema',
			showRequestHeaders: false
		});
		
		window.swaggerUi.load();
		
	});
	
}

DeviceViewer.prototype.getDevice = function(){
	return this.options.device;
}


/* register as a plugin in jQuery */
if (window.jQuery)
	window.jQuery.addPlugin('DeviceViewer',DeviceViewer);


	
dependency.done(function(){
	
	
	/**
	* Override this method to show an image from a blob content, compatible with ethingHTTPSwaggerClient.
	* Else it will load the image twice !
	*/
	SwaggerUi.Views.OperationView.prototype.showStatus = function(response) {
		var url, content;
		if (response.content === undefined) {
		  content = response.data;
		  url = response.url;
		} else {
		  content = response.content.data;
		  url = response.request.url;
		}
		var headers = response.headers;
		content = jQuery.trim(content);

		// if server is nice, and sends content-type back, we can use it
		var contentType = null;
		if (headers) {
		  contentType = headers['Content-Type'] || headers['content-type'];
		  if (contentType) {
			contentType = contentType.split(';')[0].trim();
		  }
		}
		$('.response_body', $(this.el)).removeClass('json');
		$('.response_body', $(this.el)).removeClass('xml');

		var supportsAudioPlayback = function(contentType){
		  var audioElement = document.createElement('audio');
		  return !!(audioElement.canPlayType && audioElement.canPlayType(contentType).replace(/no/, ''));
		};
		
		var supportsVideoPlayback = function(contentType){
		  var videoElement = document.createElement('video');
		  return !!(videoElement.canPlayType && videoElement.canPlayType(contentType).replace(/no/, ''));
		};

		var pre;
		var code;
		if (!content) {
		  code = $('<code />').text('no content');
		  pre = $('<pre class="json" />').append(code);

		  // JSON
		} else if (contentType === 'application/json' || /\+json$/.test(contentType)) {
		  var json = null;
		  try {
			json = JSON.stringify(JSON.parse(content), null, '  ');
		  } catch (_error) {
			json = 'can\'t parse JSON.  Raw result:\n\n' + content;
		  }
		  code = $('<code />').text(json);
		  pre = $('<pre class="json" />').append(code);

		  // XML
		} else if (contentType === 'application/xml' || /\+xml$/.test(contentType)) {
		  code = $('<code />').text(this.formatXml(content));
		  pre = $('<pre class="xml" />').append(code);

		  // HTML
		} else if (contentType === 'text/html') {
		  code = $('<code />').html(_.escape(content));
		  pre = $('<pre class="xml" />').append(code);

		  // Plain Text
		} else if (/text\/plain/.test(contentType)) {
		  code = $('<code />').text(content);
		  pre = $('<pre class="plain" />').append(code);


		  // Image
		} else if (/^image\//.test(contentType)) {
			
			if(response.data instanceof Blob){
				// build an image from the blob data
				var urlCreator = window.URL || window.webkitURL;
				var imageUrl = urlCreator.createObjectURL( response.data );
				
				var image = new Image();
				image.src = imageUrl;
				pre = image;
			}
			else {
				pre = $('<img>').attr('src', EThing.toApiUrl(url,true)); // include the access token as a query parameter
			}

		  // Audio
		} else if (/^audio\//.test(contentType) && supportsAudioPlayback(contentType)) {
		  pre = $('<audio controls>').append($('<source>').attr('src', EThing.toApiUrl(url,true)).attr('type', contentType));

		  // video
		} else if (/^video\//.test(contentType) && supportsVideoPlayback(contentType)) {
		  pre = $('<video controls>').append($('<source>').attr('src', EThing.toApiUrl(url,true)).attr('type', contentType));

		  // Download
		} else if (headers['Content-Disposition'] && (/attachment/).test(headers['Content-Disposition']) ||
			headers['content-disposition'] && (/attachment/).test(headers['content-disposition']) ||
			headers['Content-Description'] && (/File Transfer/).test(headers['Content-Description']) ||
			headers['content-description'] && (/File Transfer/).test(headers['content-description'])) {

		  if ('Blob' in window) {
			var type = contentType || 'text/html';
			var blob = new Blob([content], {type: type});
			var a = document.createElement('a');
			var href = window.URL.createObjectURL(blob);
			var fileName = response.url.substr(response.url.lastIndexOf('/') + 1);
			var download = [type, fileName, href].join(':');

			// Use filename from response header
			var disposition = headers['content-disposition'] || headers['Content-Disposition'];
			if(typeof disposition !== 'undefined') {
			  var responseFilename = /filename=([^;]*);?/.exec(disposition);
			  if(responseFilename !== null && responseFilename.length > 1) {
				download = responseFilename[1];
			  }
			}

			a.setAttribute('href', href);
			a.setAttribute('download', download);
			a.innerText = 'Download ' + fileName;

			pre = $('<div/>').append(a);
		  } else {
			pre = $('<pre class="json" />').append('Download headers detected but your browser does not support downloading binary via XHR (Blob).');
		  }

		  // Location header based redirect download
		} else if(headers.location || headers.Location) {
		  window.location = EThing.toApiUrl(response.url,true);

		  // Anything else (CORS)
		} else {
		  code = $('<code />').text(content);
		  pre = $('<pre class="json" />').append(code);
		}
		var response_body = pre;
		$('.request_url', $(this.el)).html('<pre></pre>');
		$('.request_url pre', $(this.el)).text(url);
		$('.response_code', $(this.el)).html('<pre>' + response.status + '</pre>');
		$('.response_body', $(this.el)).html(response_body);
		$('.response_headers', $(this.el)).html('<pre>' + _.escape(JSON.stringify(response.headers, null, '  ')).replace(/\n/g, '<br>') + '</pre>');
		$('.response', $(this.el)).slideDown();
		$('.response_hider', $(this.el)).show();
		$('.response_throbber', $(this.el)).hide();


		// adds curl output
		var curlCommand = this.model.asCurl(this.map, {responseContentType: contentType});
		curlCommand = curlCommand.replace('!', '&#33;');
		$( 'div.curl', $(this.el)).html('<pre>' + _.escape(curlCommand) + '</pre>');

		// only highlight the response if response is less than threshold, default state is highlight response
		var opts = this.options.swaggerOptions;

		if (opts.showRequestHeaders) {
		  var form = $('.sandbox', $(this.el)),
			  map = this.getInputMap(form),
			  requestHeaders = this.model.getHeaderParams(map);
		  delete requestHeaders['Content-Type'];
		  $('.request_headers', $(this.el)).html('<pre>' + _.escape(JSON.stringify(requestHeaders, null, '  ')).replace(/\n/g, '<br>') + '</pre>');
		}

		var response_body_el = $('.response_body', $(this.el))[0];
		// only highlight the response if response is less than threshold, default state is highlight response
		if (opts.highlightSizeThreshold && typeof response.data !== 'undefined' && response.data.length > opts.highlightSizeThreshold) {
		  return response_body_el;
		} else {
		  return hljs.highlightBlock(response_body_el);
		}
	};
	
	
});




})();
 
/* @file: src\ui\formmodal.js */ 
(function(){
	
	
	function extract(src,fields){
		var o = {}, isarray = true;
		if(!Array.isArray(fields)){
			isarray = false;
			fields = [fields];
		}
		for(var i=0; i<fields.length; i++){
			o[fields[i]] = src[fields[i]];
			delete src[fields[i]];
		}
		return isarray ? o : o[fields[0]];
	}
	
	
	function FormModal(opt,doneCallback){
		
		var options = $.extend(true,{
			title: null,
			item: null,
			size: null,
			validLabel: '+Apply',
			cancelLabel: 'Cancel'
		},opt);
		
		var modalOptions = $.extend(true,{
			buttons: {}
		},extract(options,['title','size']));
		
		
		// add buttons
		modalOptions.buttons[ extract(options,'validLabel') ] = function(){
			var $this = $(this);
			
			$this.modal('disable').form('validate')
				.done(function(props){
					if(typeof doneCallback == 'function'){
						var r = doneCallback.call(this,props);
						if(typeof r == 'undefined'){
							$this.modal('hide');
							return;
						}
						else if(r !== false){
							$.when(r)
								.done(function(v){
									// close the modal dialog only on success
									$this.modal('hide', v);
								})
								.fail(function(e){
									$this.modal('enable');
									$this.form().setError(typeof e.message == 'string' ? e.message : e);
								});
							return;
						}
					}
					$this.modal('enable');
				})
				.fail(function(){
					$this.modal('enable');
				});
			
			return false; // do not close the modal dialog
		};
		modalOptions.buttons[ extract(options,'cancelLabel') ] = null;
		
		
		return $('<div>')
			.form(options)
			.modal(modalOptions)
		
	}

	
	/* register as a plugin in jQuery */
	if (window.jQuery) {
		window.jQuery.FormModal = FormModal;
    }
	



})();
