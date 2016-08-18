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
		
		if($.isFunction(options.set) && options.value!==null)
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
		
		var items = {};
		if(Array.isArray(opt.items))
			for(var i=0; i<opt.items.length; i++)
				items[ opt.items[i] ] = opt.items[i];
		else if($.isPlainObject(opt.items))
			items = $.extend({},opt.items);
		
		var onChange = opt.onChange;
		
		delete opt.items;
		delete opt.onChange;
		
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
			}
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
