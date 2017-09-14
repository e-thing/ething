(function (root, factory) {
    if (typeof define === 'function' && define.amd) {
        // AMD. Register as an anonymous module.
        define(['jquery', 'css!bootstrap-toggle-flat'], factory);
    } else {
        // Browser globals
        root.Form = factory(root.jQuery);
    }
}(this, function ($) {
	
	
	/* optional dependencies :
	
	titatoggle
	typeahead
	selectpicker
	datetimepicker
	
	*/
	
	
	
	// Dependency resolution, adapted from https://gist.github.com/1232505/f16308bc14966c8d003c2686b1c258ec41303c1f
	/*
	var graph = {
		html: ['foo'], // means 'html' depends on 'foo'
		value: ['options', 'html'],
		foo: ['options'],
		bar: ['options', 'html'],
		options: [],
		css: ['value'],
		elements: ['css', 'html', 'options']
	};
	
	output :
		options
		foo
		html
		value
		bar
		css
		elements
	*/
	function dep_resolve(graph) {
	  var sorted  = [], // sorted list of IDs ( returned value )
		  visited = {}; // hash: id of already visited node => true

	  // 2. topological sort
	  Object.keys(graph).forEach(function visit(name, ancestors) {
		if (!Array.isArray(ancestors)) ancestors = [];
		ancestors.push(name);
		visited[name] = true;

		graph[name].forEach(function(dep) {
			if (ancestors.indexOf(dep) >= 0)  // if already in ancestors, a closed chain exists.
				throw new Error('Circular dependency "' +  dep + '" is required by "' + name + '": ' + ancestors.join(' -> '));

			// if already exists, do nothing
			if (visited[dep]) return;
			visit(dep, ancestors.slice(0)); // recursive call
		});

		if(sorted.indexOf(name)<0) sorted.push(name);
	  });

	  return sorted;
	}
	
	
	
	// recursive 
	function attach(item){
		item.isAttached = true;
		
		for(var i=0; i<item.children_.length; i++)
			attach(item.children_[i]);
		
		if(typeof item.onattach == 'function')
			item.onattach.call(item);
		
		if(typeof item.options.onattach == 'function')
			item.options.onattach.call(item);
	}
	
	function detach(item){
		item.isAttached = false;
		
		if(typeof item.ondetach == 'function')
			item.ondetach.call(item);
		
		for(var i=0; i<item.children_.length; i++)
			detach(item.children_[i]);
	}
	
	
	
	
	function inherits(extended, parent){
		extended.prototype = Object.create(parent.prototype);
	};
	
	
	function tree(item){
		function tree_(item){
			var lines = [];
			
			lines.push(item.name);
			
			for(var i=0; i<item.children_.length; i++){
				tree_(item.children_[i]).forEach(function(line){
					lines.push('  '+line);
				});
			}
			
			return lines;
		}
		
		tree_(item).forEach(function(line){
			console.log(line);
		});
	}
	
	Form.toItem = function(arg){
		
		if(arg instanceof Form.Item){
			return arg;
		}
		else {
			switch(typeof arg){
				case 'string':
					return new Form.Text({
						value: arg
					});
				case 'number':
					return new Form.Number({
						value: arg
					});
				case 'boolean':
					return new Form.Checkbox({
						value: arg
					});
				case 'object':
					if(Array.isArray(arg)){
						var items = [];
						for(var i=0; i<arg.length; i++){
							var item = Form.toItem(arg[i]);
							if(!item) return false;
							items.push({
								item: item
							});
						}
						return new Form.ArrayLayout({
							items: items
						});
					}
					else if($.isPlainObject(arg)){
						var items = [], keys = Object.keys(arg);
						for(var i=0; i<keys.length; i++){
							var item = Form.toItem(arg[keys[i]]);
							if(!item) return false;
							items.push({
								name: keys[i],
								item: item
							});
						}
						return new Form.FormLayout({
							items: items
						});
					}
					else if(arg === null){
						return new Form.NullItem();
					}
					break;
			}
		}
		
		return false;
	}
	
	
	Form.fromValue = function(value){
		var typeof_ = typeof value, item = false;
		
		switch(typeof_){
			case 'string':
				item = new Form.Text();
				break;
			case 'number':
				item = new Form.Number();
				break;
			case 'boolean':
				item = new Form.Checkbox();
				break;
			case 'object':
				if(Array.isArray(value))
					item = new Form.ArrayLayout({
						editable: true
					});
				else if($.isPlainObject(value))
					item = new Form.FormLayout({
						editable: true
					});
				break;
		}
		if(item)
			item.value(value);
		
		return item;
	}
	
	Form.fromType = function(type){
		var item = false;
		
		switch(type){
			case 'string':
			case 'text':
				item = new Form.Text();
				break;
			case 'number':
			case 'integer':
				item = new Form.Number();
				if(type=='integer') item.addValidator(Form.validator.Integer);
				break;
			case 'boolean':
				item = new Form.Checkbox();
				break;
			case 'object':
				item = new Form.FormLayout({
					editable: true
				});
				break;
			case 'array':
				item = new Form.ArrayLayout({
					editable: true
				});
				break;
		}
		
		return item;
	}
	
	
	
	
	/*
	 item base class
	*/
	Form.Item = function(opt){
		this.options = $.extend({
			validators: null,
			format: {
				'in': null, // function (<incoming value>) -> <internal value>
				'out': null // function (<internal value>) -> <returned value>
			}
		},opt);
		
		this.validators = (this.validators || []).concat( Array.isArray(this.options.validators) ? this.options.validators : [this.options.validators] );
		
		this.name = this.options.name || this.name || 'Item_'+String(Math.round(Math.random()*10000));
		
		// for the relationship
		this.parent_ = this.parent_ || null;
		this.children_ = this.children_ || [];
		
		if(this.options.parent) 
			this.setParent(this.options.parent);
		
		
		this.$view = this.createView() || $('<div>');
		this.$view.addClass('f-item');
		this.$view.data('item',this);
		
		this.create();
		
		if(typeof this.options.value == 'undefined' || !this.value(this.options.value))
			this.update();
		
		if(typeof this.options.onload == 'function')
			this.options.onload.call(this);
		
	}
	
	
	Form.Item.prototype.destroy = function(){
		this.setParent(null);
		
		var e = $.Event( 'destroy.form', { item: this } );
		e.stopPropagation(); //Prevents the event from bubbling up the parents
		this.trigger(e);
		
		// remove the dom element
		this.$view.remove();
	};
	
	Form.Item.prototype.addValidator = function(validator){
		if(typeof validator == 'function')
			this.validators.push(validator);
	}
	
	// error
	Form.Item.prototype.hasError = function(){
		return !!this.getErrors().length;
	};
	Form.Item.prototype.getErrors = function(){return [];}; // to be implemented
	
	
	
	// to be implemented :
	Form.Item.prototype.create = function(){};
	Form.Item.prototype.update = function(){}; // update this item according to its view
	Form.Item.prototype.setValue = function(value){
		
		// validate the incoming value
		var result = this.validate(value);
		
		if(result instanceof Error){
			// the validation fail !
			// no change
			//console.error('validation fail : ', result.message, ', with value : ', value);
			return false;
		}
		
		return true;
	}
	Form.Item.prototype.getValue = function(){};
	
	Form.Item.prototype.value = function(value){
		if(typeof value == 'undefined'){
			// getter
			var val = this.getValue();
			if(typeof this.options.format['out'] == 'function'){
				// clone the value first
				if(typeof val === 'object' && val!==null)
					val = $.extend(true,Array.isArray(val) ? [] : {},val);
				return this.options.format['out'].call(this, val);
					
			} else
				return val;
		}
		else {
			// setter
			if (typeof this.options.format['in'] == 'function'){
				try {
					// clone the value first
					if(typeof value === 'object' && value!==null)
						value = $.extend(true,Array.isArray(value) ? [] : {},value);
					value = this.options.format['in'].call(this,value);
				} catch (e){
					return false;
				}
			}
			return this.setValue(value);
		}
	};
	
	Form.Item.prototype.validate = function(value){
		try {
			for(var i=0; i<this.validators.length; i++)
				if(typeof this.validators[i] == 'function')
					if(this.validators[i].call(this,value)===false)
						throw 'invalid value';
		} catch(e){
			if(!(e instanceof Error)) e = new Error(e);
			e.item = this;
			return e;
		}
		return true;
	}
	
	
	// relationship methods
	Form.Item.prototype.setParent = function(parent){
		// remove any previous relationship
		if(this.parent_){
			for(var i=0; i<this.parent_.children_.length; i++){
				if(this.parent_.children_[i]===this){
					this.parent_.children_.splice(i, 1);
					i--;
				}
			}
		}
		// make the relationship
		this.parent_ = parent;
		if(parent) {
			if(typeof parent.children_ == 'undefined') parent.children_ = [];
			parent.children_.push(this);
			
			if(parent.isAttached)
				attach(this);
		}
		else {
			// this item has been detached from a Form instance
			detach(this);
		}
	};
	Form.Item.prototype.parent = function(){
		return this.parent_;
	};
	Form.Item.prototype.children = function(){
		return this.children_;
	};
	Form.Item.prototype.iterate = function(handler){
		this.findItems().forEach(function(item){
			handler.call(item);
		});
	};
	Form.Item.prototype.findItem = function(name){
		if(this.name === name)
			return this;
		if(this.children_)
			for(var i=0; i<this.children_.length; i++){
				var f = this.children_[i].findItem(name);
				if(typeof f != 'undefined')
					return f;
			}
	};
	Form.Item.prototype.findItems = function(filter){
		var items = [];
		if(typeof filter != 'function' || filter.call(this))
			items.push(this);
		if(this.children_)
			for(var i=0; i<this.children_.length; i++){
				items = items.concat(this.children_[i].findItems(filter));
			}
		return items;
	};
	// return the root form object
	Form.Item.prototype.form = function(){
		var p = this.parent(), f = this;
		while(p){
			f = p;
			p = p.parent();
		}
		return f;
	};
	
	// events, use the jQuery event engine with this context
	['on','off','one','trigger'].forEach(function(method){
		Form.Item.prototype[method] = function(){
			if(this.$view){
				var context = this;
				var args = Array.prototype.slice.call(arguments).map(function(arg, index){
					return (typeof arg == 'function') ? function(){
							arg.apply(context,Array.prototype.slice.call(arguments));
						} : arg;
				});
				this.$view[method].apply(this.$view,args);
			}
			return this;
		}
	});
	
	Form.Item.prototype.change = function(handler){
		if(typeof handler == 'function')
			this.on('changed.form', handler);
		else {
			var e = $.Event( 'changed.form', { item: this, data: handler } );
			this.trigger(e);
		}
		return this;
	}
	
	// for debugging
	Form.Item.prototype.tree = function(){
		tree(this);
	}
	
	// VIEW
	Form.Item.prototype.createView = function(){} // build the view, must return a jQuery element.
	Form.Item.prototype.updateView = function(){ // update the view according to the model value.
		this.$view.toggleClass('f-has-error',this.hasError());
	}
	
	
	Form.Constant = function(value){
		Form.Item.call(this, {
			'value': value
		});
	};
	inherits(Form.Constant,Form.Item);
	
	Form.Constant.prototype.createView = function(){
		return $('<div class="f-constant">').hide();
	}
	
	Form.Constant.prototype.getValue = function(){
		return this.options.value;
	}
	
	
	Form.NullItem = function(){
		Form.Item.call(this);
	};
	inherits(Form.NullItem,Form.Item);
	
	Form.NullItem.prototype.createView = function(){
		return $('<div class="f-null">').hide();
	}
	
	Form.NullItem.prototype.getValue = function(){
		return null;
	}
	
	
	Form.Label = function(content){
		this.content = content || '';
		Form.Item.call(this);
	};
	inherits(Form.Label,Form.Item);
	
	Form.Label.prototype.createView = function(){
		return $('<div class="f-label">').html(this.content);
	}
	
	Form.Label.prototype.setValue = function(value){
		if(!Form.Item.prototype.setValue.call(this,value)) return false;
		this.content = value;
		this.$view.html(this.content);
		return true;
	}
	
	
	/*
	 Layout that contain exactly one item
	*/
	Form.Wrapper = function(options){
		if(options instanceof Form.Item)
			options = {
				item: options
			};
		
		this.item = options.item;
		if(!this.item) throw 'no item set';
		this.item.setParent(this);
		
		Form.Item.call(this, options);
	};
	inherits(Form.Wrapper,Form.Item);
	
	Form.Wrapper.prototype.setValue = function(value){
		if(!Form.Item.prototype.setValue.call(this,value)) return false;
		return this.item.value(value);
	};
	Form.Wrapper.prototype.getValue = function(){
		return this.item.value();
	};
	
	Form.Wrapper.prototype.getErrors = function(){
		return this.item.getErrors();
	};
	
	Form.Wrapper.prototype.createView = function(){
		var $view = $('<div class="f-wrapper">');
		
		$view.append(
			this.item.$view
		);
		
		return $view;
	}
	
	
	
	
	
	/*
	 layout base class
	 
	 new Form.Layout({
		items: [ {
				item: #Form.Item instance
				?key: ?value
			} , ... ]
		?key: ?option
	});
	 
	*/
	
	Form.Layout = function(options, defaultLayoutItemOptions){
		var self = this;
		
		this.defaultLayoutItemOptions = defaultLayoutItemOptions;
		
		this.layoutItems = [];
		
		
		Form.Item.call(this, $.extend({
			maxItems: null,
			items: []
		},options));
		
	}
	inherits(Form.Layout,Form.Item);
	
	Form.Layout.prototype.create = function(){
		
		for(var i=0; i<this.options.items.length; i++){
			this.addItem(this.options.items[i]);
		}
		
	}
	
	Form.Layout.prototype.update = function(triggerChange){
		
		var error = undefined;
		
		if(this.validators.length){
			var value = this.getValue();
			var result = this.validate(value);
		
			if(result instanceof Error) {
				// the validation fail !
				error = result;
			}
		}
		
		var change = error !== this.error;
		
		this.error = error;
		
		this.updateView(arguments[1], arguments[2], arguments[3]); // update the view to print the change
		
		if(change || triggerChange){
			// trigger the events
			this.change();
		}
	}
	
	Form.Layout.prototype.getErrors = function(){
		var errors = [];
		if(this.error)
			errors.push(this.error);
		for(var i=0; i<this.layoutItems.length; i++){
			var item = this.layoutItems[i].item;
			errors = errors.concat(item.getErrors());
		}
		return errors;
	}
	
	/*
	Form.Layout.prototype.addItem( {
		item: #Form.Item instance
		?key: ?value
	} );
	
	or
	
	Form.Layout.prototype.addItem( #Form.Item instance );
	*/
	Form.Layout.prototype.addItem = function(layoutItem, index){
		var self = this;
		
		if(typeof this.options.maxItems == 'number' && this.layoutItems.length >= this.options.maxItems)
			return false;
		
		if(layoutItem instanceof Form.Item){
			layoutItem = {
				item: layoutItem
			};
		}
		else if(!$.isPlainObject(layoutItem)) return false;
		
		layoutItem = typeof this.defaultLayoutItemOptions == 'function' ? this.defaultLayoutItemOptions.call(this, layoutItem) : $.extend(true,{},this.defaultLayoutItemOptions || {},layoutItem);
		
		layoutItem.item = Form.toItem(layoutItem.item);
		
		if(!(layoutItem.item instanceof Form.Item)) return false;
		
		if(typeof index === 'number' && index >=0 && index<this.layoutItems.length)
			this.layoutItems.splice(index, 0, layoutItem);
		else {
			index = this.layoutItems.length;
			this.layoutItems.push(layoutItem);
		}
		
		layoutItem.item.setParent(this);
		
		
		// update this error state each time a child error state changed
		layoutItem.item.change(function(){self.update();});
		
		this.update(true, 'addItem', layoutItem, index);
		
		return layoutItem;
	};
	
	/*
	Form.Layout.prototype.removeItem( index );
	
	or
	
	Form.Layout.prototype.removeItem( #Form.Item instance );
	*/
	Form.Layout.prototype.removeItem = function(index){
		if(typeof index == 'number' && index >= 0 && index < this.layoutItems.length){
			var itemToBeRemoved = this.layoutItems.splice(index, 1)[0];
			itemToBeRemoved.item.destroy();
			this.update(true, 'removeItem', itemToBeRemoved);
		}
		else if(index instanceof Form.Item){
			this.removeItem(this.indexOf(index));
		}
	};
	Form.Layout.prototype.clear = function(){
		while(this.layoutItems.length>0){
			this.removeItem(0);
		}
	};
	Form.Layout.prototype.length = function(){
		return this.layoutItems.length;
	};
	Form.Layout.prototype.isEmpty = function(){
		return this.length() == 0;
	};
	Form.Layout.prototype.indexOf = function(item){
		for(var i=0; i<this.layoutItems.length; i++){
			if(typeof item == 'function'){
				if(item.call(this, this.layoutItems[i]))
					return i;
			} else if(this.layoutItems[i].item === item){
				return i;
			}
		}
		return -1
	};
	
	
	
	
	
	// form builder
	function Form(element,item,value,onload){
		
		var self = this;
		
		if(typeof onload == 'undefined' && typeof value == 'function'){
			onload = value;
			value = undefined;
		}
		
		this.name = 'form';
		
		this.element = element;
		$(this.element).text('loading ...');
		
		// make it async is asked
		$.when(item,value).done(function(item, value){
			
			Form.Wrapper.call(self, {
				item : Form.toItem(item)
			});
			
			if(typeof value != 'undefined')
				self.value(value);
			
			if(typeof onload == 'function')
				onload.call(self);
			
			attach(self);
			
			//tree(self);
			
		}).fail(function(){
			$(this.element).text('error');
		});
		
	};
	inherits(Form,Form.Wrapper);
	
	Form.prototype.root = function(){
		return this.item;
	}
	
	Form.prototype.createView = function(){
		var $view = $(this.element).empty().addClass('f-form');
		
		$view.append(
			this.item.$view
		);
		
		return $view;
	}
	
	Form.prototype.submit = function(success, error){
		var dfr = $.Deferred();
		
		// update all the items
		this.iterate(function(){
			this.update();
		});
		
		var errors = this.getErrors();
		
		console.log(errors);
		
		if(errors.length){
			dfr.rejectWith(this, [errors]);
		}
		else {
			dfr.resolveWith(this, [this.value()]);
		}
		
		return dfr.promise().done(success).fail(error);
	}
	
	
	
	
	
	
	/*
	 input base class
	 
	 new Form.ValueItem({
		?key: ?option
	 });
	 
	*/
	Form.Input = function(options){
	
		this.value_ = undefined;
		
		Form.Item.call(this, options);
		
		
	}
	inherits(Form.Input,Form.Item);
	
	
	function uniq(a) {
		var temp = {};
		for (var i = 0; i < a.length; i++)
			temp[a[i]] = true;
		var r = [];
		for (var k in temp)
			r.push(k);
		return r;
	}
	
	function isEqual(x, y) {
		'use strict';

		if (x === null || x === undefined || y === null || y === undefined) { return x === y; }
		// after this just checking type of one would be enough
		if (x.constructor !== y.constructor) { return false; }
		// if they are functions, they should exactly refer to same one (because of closures)
		if (x instanceof Function) { return x === y; }
		// if they are regexps, they should exactly refer to same one (it is hard to better equality check on current ES)
		if (x instanceof RegExp) { return x === y; }
		if (x === y || x.valueOf() === y.valueOf()) { return true; }
		if (Array.isArray(x) && x.length !== y.length) { return false; }

		// if they are dates, they must had equal valueOf
		if (x instanceof Date) { return false; }

		// if they are strictly equal, they both need to be object at least
		if (!(x instanceof Object)) { return false; }
		if (!(y instanceof Object)) { return false; }

		// recursive object equality check
		var p = Object.keys(x);
		return Object.keys(y).every(function (i) { return p.indexOf(i) !== -1; }) &&
			p.every(function (i) { return isEqual(x[i], y[i]); });
	}
	
	Form.Input.prototype.setValue = function(value, forceUpdate){
		
		if(!Form.Item.prototype.setValue.call(this,value)) return false;
		
		var valueChanged = forceUpdate===true || !isEqual(value, this.value_); // value !== this.value_;
		
		this.value_ = value;
		
		
		// trigger the event
		if(valueChanged){
			// update the view
			
			if(this.updateView()!==false)
				this.change();
		}
		
		return true;
	}
	
	Form.Input.prototype.getValue = function(){
		return this.value_ instanceof Error ? undefined : this.value_;
	}
	
	Form.Input.prototype.getErrors = function(){
		return this.value_ instanceof Error ? [this.value_] : [];
	}
	
	Form.Input.prototype.setError = function(e){
		if(e) this.value_ = e;
		if(this.updateView()!==false)
			this.change();
	}
	
	Form.Input.prototype.update = function(forceTriggerChange){ // update the model value from the view, must be called by the view, each time the view changed !
		
		var newValue = this.getViewValue();
		
		// validate first the new value
		var result = this.validate(newValue);
		
		if(result instanceof Error) {
			// the validation fail !
			// put the Model value into an error state
			newValue = result;
		}
		
		var updateView = (newValue instanceof Error) || (this.value_ instanceof Error); // update the view only to update error state
		var valueChanged = !isEqual(newValue, this.value_); //newValue !== this.value_;
		
		this.value_ = newValue;
		
		if(updateView){
			this.updateView('updateError'); // update the view to print the error
		}
		
		// trigger the event
		if(valueChanged || forceTriggerChange===true){
			this.change();
		}
		
		return;
	}
	
	
	// VIEW : to be implemented
	Form.Input.prototype.getViewValue = function(){} // retrieve the view value
	
	
	Form.Input.prototype.focus = function(){
		if(this.$view){
			this.$view.find('input, textarea, select').first().focus();
		}
	}	
	
	
	
	/**
	* ArrayLayout
	*
	* return an array as a value
	*
	* options:
	*  items : [<Form.Item>]
	*  instanciator : function() -> <Form.Item> or an array of types among ['text','number','boolean','array','object']
	*  editable: <boolean>
	*
	*/
	Form.ArrayLayout = function(opt){
		
		this.validators = [function(value){
			if(!Array.isArray(value)) throw 'not an array';
			
			if(typeof this.options.minItems == 'number'){
				if(value.length < this.options.minItems)
					throw 'The number of items must be greater than or equal to '+this.options.minItems;
			}
			if(typeof this.options.maxItems == 'number'){
				if(value.length > this.options.maxItems)
					throw 'The number of items must be lower than or equal to '+this.options.maxItems;
			}
		}];
		
		Form.Layout.call(this, $.extend(true,{
			items:[],
			editable: false,
			instanciator: null,
			emptyMessage: 'empty !',
			minItems: null, // minimum items allowed, only available if editable=true
			maxItems: null // maximum items allowed, only available if editable=true
		},opt));
		
	}
	inherits(Form.ArrayLayout,Form.Layout);
	
	Form.ArrayLayout.prototype.setValue = function(arrayOfValues){
		if(!Array.isArray(arrayOfValues)) return false;
		
		if(this.options.editable){
			
			if(!Form.Item.prototype.setValue.call(this,arrayOfValues)) return false;
			
			// build the form from the values
			this.clear();
			var ok = true;
			for(var i=0; i<arrayOfValues.length && (typeof this.options.maxItems != 'number' || i<this.options.maxItems); i++){
				if(typeof this.options.instanciator == 'function'){
					var layoutItem = this.addItem();
					if(!layoutItem || !layoutItem.item.value(arrayOfValues[i]))
						ok = false;
				}
				else if(!this.addItem(Form.fromValue(arrayOfValues[i])))
					ok = false;
			}
			
			return ok;
		}
		else {
			
			var ok = true;
			for(var i=0; i<arrayOfValues.length && i<this.layoutItems.length; i++){
				if(!this.layoutItems[i].item.value(arrayOfValues[i]))
					ok = false;
			}
			return ok;
		}
	};
	
	// return an array of values.
	Form.ArrayLayout.prototype.getValue = function(){
		var arrayOfValues = [];
		for(var i=0; i<this.layoutItems.length; i++){
			var val = this.layoutItems[i].item.value();
			arrayOfValues.push(val);
		}
		return arrayOfValues;
	};
	
	Form.ArrayLayout.prototype.addItem = function(item, index){
		if(typeof item == 'undefined'){
			if(typeof this.options.instanciator == 'function')
				item = this.options.instanciator.call(this);
			else {
				console.error('no instanciator function set !');
				return false;
			}
		}
		
		return Form.Layout.prototype.addItem.call(this,item,index);
	};
	
	Form.ArrayLayout.prototype.createView = function(){
		var $view = $('<div>').addClass('f-arraylayout');
		
		this.$content = $('<div>').appendTo($view);
		
		this.$content.html($('<div class="f-arraylayout-empty-msg">').html(this.options.emptyMessage));
		
		if(this.options.editable){
			var self = this,
				$add = $('<button type="button" class="btn btn-default"><span class="glyphicon glyphicon-plus" aria-hidden="true"></span> add</button>'),
				$dropdown = null,
				$type = null;
			
			if(typeof self.options.instanciator != 'function'){
				
				$dropdown = $('<ul class="dropdown-menu">');
				$type = $(' <button type="button" class="btn btn-default dropdown-toggle" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false"><span>type</span> <span class="caret"></span></button>');
				
				var allowedTypes = Array.isArray(self.options.instanciator) ? self.options.instanciator : ['text','number','boolean','array','object'];
				allowedTypes.forEach(function(type){
					$dropdown.append('<li><a href="#">'+type+'</a></li>');
				},this);
				
				$dropdown.on('click', 'li a', function(e){
					e.preventDefault();
					$type.children('span:first-child').text($(this).text());
				});
				$dropdown.find('li > a').first().click();
				
			}
			
			$add.click(function(){
				if(typeof self.options.instanciator == 'function'){
					item = self.options.instanciator.call(self);
				}
				else {
					item = Form.fromType( $type.children('span:first-child').text() );
				}
				if(item)
					self.addItem(item);
			});
			
			$view.append(
				$('<div class="f-arraylayout-edit-tb btn-group btn-group-sm">').append(
					$type || $dropdown ? $('<div class="btn-group">').append($type,$dropdown) : null,
					$add
				),' ',
				$('<div class="alert alert-danger" role="alert" style="display: inline-block;">').hide()
			);
			
		}
		
		return $view;
	}
	
	Form.ArrayLayout.prototype.updateView = function(reason, layoutItem, index){
		Form.Layout.prototype.updateView.call(this);
		
		var self = this;
		
		
		if(reason == "addItem"){
			
			this.$content.children('.f-arraylayout-empty-msg').remove();
			
			layoutItem.$wrapper = $('<div class="f-array-item">');
			
			var $delete = $('<button type="button" class="btn btn-default btn-xs f-array-item-remove-btn"><span class="glyphicon glyphicon-trash" aria-hidden="true"></span></button>').click(function(){
				self.removeItem(layoutItem.item);
			});
			
			var $h = layoutItem.$wrapper.append(
				layoutItem.item.$view,
				this.options.editable ? $('<div class="f-array-item-edit">').html(
					$('<div class="btn-group">').append($delete)
				) : null
			);
			
			if(index===0){
				this.$content.prepend($h);
			} else if(index>0) {
				this.$content.children().eq(index-1).after($h);
			} else {
				this.$content.append($h);
			}
			
		}
		else if(reason == "removeItem"){
			layoutItem.$wrapper.remove();
			
			if(!this.layoutItems.length)
				this.$content.html($('<div class="f-arraylayout-empty-msg">').html(this.options.emptyMessage));
		}
		
		// disable the add button if the maxItems limit is reached
		if(this.options.editable && typeof this.options.maxItems == 'number'){
			this.$view.children('.f-arraylayout-edit-tb').find('button').prop('disabled', this.layoutItems.length >= this.options.maxItems);
		}
		
		if(this.options.editable && typeof this.options.minItems == 'number'){
			this.layoutItems.forEach(function(layoutItem){
				layoutItem.$wrapper.children('.f-array-item-edit').find('button.f-array-item-remove-btn').toggle(this.layoutItems.length > this.options.minItems);
			}, this);
			
			if(this.layoutItems.length<this.options.minItems){
				this.$view.children('.alert').text('minimum items number is '+this.options.minItems).show();
			} else {
				this.$view.children('.alert').hide();
			}
		}
		
		
	}
	
	
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
		
		var options = $.extend(true,{
			inline: false,
			disabledValue: null,
			skipOnDisabled: false,
			skipOnHidden: true,
			emptyMessage: 'empty !',
			items: [],
			editable: false,
			instanciator: null, // function (field) -> Item
			maxItems: null
		},opt);
		
		if(opt.hasOwnProperty('disabledValue'))
			options.disabledValue = opt.disabledValue;
		
		Form.Layout.call(this, options, function(layoutItem){
			var self = this;
			layoutItem = $.extend(true,{},Form.FormLayout.defaults,layoutItem);
			
			if(!layoutItem.name && layoutItem.label) layoutItem.name = layoutItem.label;
			
			return layoutItem;
		});
		
	}
	inherits(Form.FormLayout,Form.Layout);
	
	
	
	Form.FormLayout.prototype.getErrors = function(){
		var errors = [];
		if(this.error)
			errors.push(this.error);
		for(var i=0; i<this.layoutItems.length; i++){
			var layoutItem = this.layoutItems[i];
			
			if(layoutItem.disabled)
				continue;
			if(layoutItem.hidden && this.options.skipOnHidden)
				continue;
			if(layoutItem.skip)
				continue;
			
			errors = errors.concat(layoutItem.item.getErrors());
		}
		return errors;
	}
	
	Form.FormLayout.prototype.createView = function(){
		var $view = $('<div>').addClass('f-formlayout');
		
		if(this.options.inline)
			$view.addClass('form-inline');
		
		this.$content = $('<div>').appendTo($view);
		
		this.$content.html($('<div class="f-formlayout-empty-msg">').html(this.options.emptyMessage));
		
		if(this.options.editable){
			var self = this,
				$add = $('<button type="button" class="btn btn-default"><span class="glyphicon glyphicon-plus" aria-hidden="true"></span> add field</button>'),
				$field = $('<input type="text" class="form-control" placeholder="field">'),
				$dropdown = null,
				$type = null;
			
			if(typeof self.options.instanciator != 'function'){
				$dropdown = $('<ul class="dropdown-menu dropdown-menu-right">');
				$type = $(' <button type="button" class="btn btn-default dropdown-toggle" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false"><span>type</span> <span class="caret"></span></button>');
			
				['text','number','boolean','array','object'].forEach(function(type){
					$dropdown.append('<li><a href="#">'+type+'</a></li>');
				},this);
				
				$dropdown.on('click', 'li a', function(e){
					e.preventDefault();
					$type.children('span:first-child').text($(this).text());
				});
				$dropdown.find('li > a').first().click();
			}
			
			$add.click(function(){
				var field = $field.val(), item = null;
				if(field){
					if(typeof self.options.instanciator == 'function'){
						item = self.options.instanciator.call(self,field);
					}
					else {
						item = Form.fromType( $type.children('span:first-child').text() );
					}
					if(item instanceof Form.Item)
						item = {
							item: item,
							removable: true
						}
					if($.isPlainObject(item))
						self.addItem($.extend({
							name: field
						},item));
				}
			});
			
			$view.append(
				$('<div class="f-formlayout-edit-tb input-group input-group-sm">').append($field, $('<span class="input-group-btn">').append($type,$dropdown,$add))
			);
		}
		
		return $view;
	}
	
	Form.FormLayout.prototype.updateView = function(reason, layoutItem, index){
		Form.Layout.prototype.updateView.call(this);
		
		var self = this;
		
		if(reason == "addItem"){
			
			this.$content.children('.f-formlayout-empty-msg').remove();
			
			var label = layoutItem.label === false ? false : (layoutItem.label || layoutItem.name),
				$wrapper = $('<div class="form-group f-formlayout-item">'),
				$checkbox = null, $remove = null,
				self = this;
			
			if(layoutItem.name){
				$wrapper.attr('data-name', layoutItem.name);
			}
			
			if(layoutItem.class){
				$wrapper.addClass(layoutItem.class);
			}
			
			if(layoutItem.checkable){
				
				$checkbox = $('<div class="checkbox checkbox-slider--c"><label><input type="checkbox"><span></span></label></div>');
				
				layoutItem.$checkbox = $checkbox.find('input').change(function() {
					var state = $(this).prop('checked');
					self.toggle(layoutItem.name,state);
				});
				
			}
			
			if(this.options.editable && layoutItem.removable){
				
				$remove = $('<button class="btn btn-default btn-xs" type="submit"><span class="glyphicon glyphicon-trash" aria-hidden="true"></span></button>').click(function() {
					self.removeItem(layoutItem.item);
				});
				
			}
			
			// description
			var description = layoutItem.description;
			if(typeof description == 'function')
				description = description.call(this);
			layoutItem.$description = description && description!='' ? $('<p class="f-description">').html(description) : null;
			
			
			var $item = layoutItem.item.$view;
			if(this.options.inline)
				$item.css('display','inline-block');
			
			layoutItem.$wrapper = $wrapper.append(
				label ? $('<label>').html(label) : null,
				$checkbox,
				$remove,
				layoutItem.$description,
				$item
			);
			
			if(layoutItem.hidden)
				$wrapper.hide();
			
			if(index===0){
				this.$content.prepend( $wrapper, ' ' );
			} else if(index>0) {
				this.$content.children().eq(index-1).after($wrapper, ' ');
			} else {
				this.$content.append( $wrapper, ' ' );
			}
			
			
			if(layoutItem.checkable){
				layoutItem.$checkbox.prop('checked',layoutItem.checked).change();
			}
			
		}
		else if(reason == "removeItem"){
			
			layoutItem.$wrapper.remove();
			
			if(!this.layoutItems.length)
				this.$content.html($('<div class="f-formlayout-empty-msg">').html(this.options.emptyMessage));
		}
		
		// disable the add button if the maxItems limit is reached
		if(this.options.editable && typeof this.options.maxItems == 'number'){
			this.$view.children('.f-formlayout-edit-tb').find('button').prop('disabled', this.layoutItems.length >= this.options.maxItems);
		}
	}
	
	
	
	Form.FormLayout.defaults = {
		label: null,
		name: null,
		description: null,  // {String | Function} description of the field
		checkable: false, // set this field checkable, if not check, the return value will be null
		checked: false, // set the initial state of a checkable field
		skip: false, // if set, will be ignored in the validation object
		hidden: false, // if this field is hidden or not
		toggle: function(layoutItem,state){
			[layoutItem.item.$view, layoutItem.$description].forEach(function($e){
				if(!$e) return;
				state ? $e.slideDown(200,function(){
					$(this).show();
				}) : $e.slideUp(200,function(){
					$(this).hide();
				}) // default behaviour is to hide/show the input
			})
		},
		removable: false, // if set AND this item is editable, this field can be removed
		dependencies: null, // { field : function(currentlayoutItem, dependentLayoutItem){ this => current FormLayout } }
		class: null // some class to be added to the item
	}
	
	Form.FormLayout.prototype.addItem = function(item, index){
		if(typeof item == 'string'){
			if(typeof this.options.instanciator == 'function')
				item = this.options.instanciator.call(this, item);
			else {
				console.error('no instanciator function set !');
				return false;
			}
		}
		
		var layoutItem = Form.Layout.prototype.addItem.call(this,item, index);
		
		// manage dependencies
		var deps = layoutItem.dependencies || {};
		Object.keys(deps).forEach(function(k){
			
			var pli = this.getLayoutItemByName(k);
			if(pli){
				
				var self = this;
				var depfn = function(){
					var visible = deps[k].call(self, layoutItem, pli);
					if(typeof visible == 'boolean')
						self.setVisible(layoutItem.name, visible);
				};
				
				pli.item.change(depfn).change();
				
				layoutItem.item.one('destroy.form', function(){
					// remove dependency
					pli.item.off('changed.form', depfn);
				})
			}
			
		}, this);
		// does an item depends on it ?
		this.layoutItems.forEach(function(li){
			var lid = li.dependencies || {};
			
			Object.keys(lid).forEach(function(k){
				if(k===layoutItem.name){
					// yes
					var self = this;
					var depfn = function(){
						var visible = lid[k].call(self, li, layoutItem);
						if(typeof visible == 'boolean')
							self.setVisible(li.name, visible);
					};
					
					layoutItem.item.change(depfn).change();
					
					li.item.one('destroy.form', function(){
						layoutItem.item.off('changed.form', depfn);
					});
				}
			}, this);
		}, this);
		
		return layoutItem;
	};
	
	Form.FormLayout.prototype.removeItem = function(index){
		
		if(typeof index != 'number')
			index = this.indexOf(index);
		
		return Form.Layout.prototype.removeItem.call(this, index);
	};
	
	Form.FormLayout.prototype.replaceItemWith = function(index, item){
		
		if(typeof index != 'number')
			index = this.indexOf(index);
		
		this.removeItem(index);
		return this.addItem(item, index);
	};
	
	Form.FormLayout.prototype.indexOf = function(item){
		
		if(typeof item == 'string'){
			var li = this.getLayoutItemByName(item);
			if(li) item = li.item;
		}
		
		return Form.Layout.prototype.indexOf.call(this, item);
	};
	
	Form.FormLayout.prototype.getLayoutItemByName = function(name){
		for(var i=0; i<this.layoutItems.length; i++){
			if(this.layoutItems[i].name === name)
				return this.layoutItems[i];
		}
	}
	
	Form.FormLayout.prototype.toggle = function(nameOrIndex,state){
		if(nameOrIndex instanceof Form.Item)
			nameOrIndex = this.indexOf(nameOrIndex);
		var layoutItem = (typeof nameOrIndex == 'number') ? this.layoutItems[nameOrIndex] : this.getLayoutItemByName(nameOrIndex);
		if(layoutItem){
			state = !!state;
			if(layoutItem.checkable && (typeof layoutItem.disabled == 'undefined' || layoutItem.disabled == state)){
				layoutItem.disabled = !state;
				layoutItem.toggle.call(this,layoutItem,state);
				layoutItem.$checkbox.prop('checked',state).change();
				this.change();
			}
		}
		return this;
	};
	Form.FormLayout.prototype.setVisible = function(nameOrIndex,visible){
		if(nameOrIndex instanceof Form.Item)
			nameOrIndex = this.indexOf(nameOrIndex);
		var layoutItem = (typeof nameOrIndex == 'number') ? this.layoutItems[nameOrIndex] : this.getLayoutItemByName(nameOrIndex);
		if(layoutItem){
			visible = !!visible;
			if(typeof layoutItem.hidden == 'undefined' || layoutItem.hidden == visible){
				layoutItem.hidden = !visible;
				layoutItem.$wrapper.toggle(visible);
				this.change();
			}
		}
		return this;
	};
	
	Form.FormLayout.prototype.setValue = function(values){
		
		if(!$.isPlainObject(values)) return false;
		
		if(!Form.Item.prototype.setValue.call(this,values)) return false;
		
		var keys = Object.keys(values), ok = true, skip = [];
		
		if(this.options.editable){
			// remove all the items (ie: clean the form)
			for(var i=this.layoutItems.length-1; i>=0; i--)
				if(this.layoutItems[i].removable)
					this.removeItem(i);
				
			// add the items that are not present
			for(var i=0; i<keys.length; i++){
				var key = keys[i],
					layoutItem = this.getLayoutItemByName(key);
				if(!layoutItem){
					// this field does not exist ! create it !
					if(typeof this.options.instanciator == 'function'){
						layoutItem = this.addItem(key);
						if(!layoutItem)
							ok = false;
					}
					else {
						skip.push(key);
						if(!this.addItem({
							name: key,
							item: Form.fromValue(values[key]),
							removable: true
						}))
							ok = false;
					}
				}
			}
		}
		
		// dependencies resolution : 
		var dep_graph = {};
		for(var i=0; i<keys.length; i++){
			var key = keys[i];
			if(skip.indexOf(key)!==-1) continue;
			var layoutItem = this.getLayoutItemByName(key);
			if(layoutItem){
				dep_graph[key] = Object.keys( layoutItem.dependencies || {} );
			}
		}
		var dep_keys = dep_resolve(dep_graph);
		
		for(var i=0; i<dep_keys.length; i++){
			var key = dep_keys[i],
				layoutItem = this.getLayoutItemByName(key);
			if(layoutItem){
				
				// execute dependencies functions
				var deps = layoutItem.dependencies || {};
				Object.keys( deps ).forEach(function(k){
					deps[k].call(this, layoutItem, this.getLayoutItemByName(k));
				}, this);
				
				layoutItem.item.value(values[key]) ?
					this.toggle(key,true) : // enable the item
					ok = false;
			}
		}
		
		return ok;
	};
	
	Form.FormLayout.prototype.getValue = function(){
		var values = {};
		for(var i=0; i<this.layoutItems.length; i++){
			var layoutItem = this.layoutItems[i];
			
			if(layoutItem.disabled && this.options.skipOnDisabled)
				continue;
			if(layoutItem.hidden && this.options.skipOnHidden)
				continue;
			if(layoutItem.skip)
				continue;
			
			var val = layoutItem.disabled ? (layoutItem.hasOwnProperty('disabledValue') ? layoutItem.disabledValue : this.options.disabledValue) : layoutItem.item.value();
			
			values[layoutItem.name] = val;
		}
		return values;
	};
	
	
	
	
	
	
	
	/*
	* TabsLayout
	* 
	* options:
	*  items : [{name: <string>, item: <Form.Item>}]
	*/
	Form.TabsLayout = function(opt){
		
		Form.Layout.call(this, $.extend(true,{
			items: []
		},opt));
		
		
	}
	inherits(Form.TabsLayout,Form.Layout);
	
	Form.TabsLayout.prototype.createView = function(){
		var $view = $('<div>').addClass('f-tabslayout');
		
		this.$navTabs = $('<ul class="nav nav-tabs" role="tablist">');
		this.$tabPanes = $('<div class="tab-content">');
		
		$view.append(
			this.$navTabs,
			this.$tabPanes
		);
		
		return $view;
	}
	
	Form.TabsLayout.prototype.updateView = function(reason, layoutItem){
		Form.Layout.prototype.updateView.call(this);
		
		var self = this;
		
		if(reason == "addItem"){
			
			var id = String(Math.round(Math.random()*1000000));
			
			layoutItem.$navTab = $('<li role="presentation"><a href="#'+id+'" role="tab" data-toggle="tab">'+(layoutItem.name)+'</a></li>');
			layoutItem.$tabPane = $('<div role="tabpanel" class="tab-pane" id="'+id+'">').append(layoutItem.item.$view);
			
			layoutItem.item.change(function(){
				layoutItem.$navTab.toggleClass('f-has-error', this.hasError());
			}).change();
			
			if(this.$navTabs.children('li').length == 0){
				layoutItem.$navTab.addClass('active');
				layoutItem.$tabPane.addClass('active');
			}
			
			this.$navTabs.append(layoutItem.$navTab);
			this.$tabPanes.append(layoutItem.$tabPane);
			
		}
		else if(reason == "removeItem"){
			layoutItem.$navTab.remove();
			layoutItem.$tabPane.remove();
		}
		
	}
	
	Form.TabsLayout.prototype.getLayoutItemByName = function(name){
		for(var i=0; i<this.layoutItems.length; i++){
			if(this.layoutItems[i].name === name)
				return this.layoutItems[i];
		}
	}
	
	Form.TabsLayout.prototype.setValue = function(values){
		if(!$.isPlainObject(values)) return false;
		if(!Form.Item.prototype.setValue.call(this,values)) return false;
		
		var ok = true;
		var keys = Object.keys(values);
		for(var i=0; i<keys.length; i++){
			var key = keys[i],
				layoutItem = this.getLayoutItemByName(key);
			if(layoutItem){
				if(!layoutItem.item.value(values[key]))
					ok = false;
			}
		}
		return ok;
	};
	
	Form.TabsLayout.prototype.getValue = function(){
		var values = {};
		
		for(var i=0; i<this.layoutItems.length; i++){
			values[this.layoutItems[i].name] = this.layoutItems[i].item.value();
		}
		
		return values;
	};
	
	
	Form.TabsLayout.Format = {
		Merge : {
			'in': function(value){
				var in_ = {};
				for(var i=0; i<this.layoutItems.length; i++){
					var v = {};
					this.layoutItems[i].fields.forEach(function(field){
						if(value.hasOwnProperty(field))
							v[field] = value[field];
					});
					in_[this.layoutItems[i].name] = v;
				}
				return in_;
			},
			'out': function(value){
				var out_ = {};
				for(var i in value){
					$.extend(out_, value[i]);
				}
				return out_;
			}
		}
	};
	
	
	/*
	* Panels
	* 
	* options:
	*  items : [{name: <string>, item: <Form.Item>}]
	*  label: <string>
	*  value: <string>
	*/
	Form.Panels = function(opt){
		var self = this;
		
		var options = $.extend(true,{
			items: []
		},opt);
		
		this._selected = 0;
		
		Form.Layout.call(this,options);
		
	}
	inherits(Form.Panels,Form.Layout);
	
	Form.Panels.prototype.createView = function(){
		var $view = $('<div>').addClass('f-panels');
		
		this.$content = $('<div>');
				
		$view.append(
			this.$content
		);
		
		return $view;
	}
	
	Form.Panels.prototype.updateView = function(reason, layoutItem){
		Form.Layout.prototype.updateView.call(this);
		
		if(reason == "addItem"){		
			this.$content.append( layoutItem.item.$view );
		}
		
		for(var i=0; i<this.layoutItems.length; i++){
			this.layoutItems[i].item.$view.toggle( this._selected === i );
		}
		
	}
	
	Form.Panels.prototype.getSelectedLayoutItem = function(){
		return this.layoutItems[this._selected];
	}
	Form.Panels.prototype.select = function(index){
		if(typeof index == 'undefined')
			return this._selected;
		else {
			this._selected = index;
			this.updateView();
		}
	}
	Form.Panels.prototype.setValue = function(value){
		if(!Form.Item.prototype.setValue.call(this,value)) return false;
		var layoutItem = this.getSelectedLayoutItem();
		return layoutItem ? layoutItem.value(value) : false;
	};
	Form.Panels.prototype.getValue = function(){
		var layoutItem = this.getSelectedLayoutItem();
		if(layoutItem)
			return layoutItem.value();
	};
	Form.Panels.prototype.getErrors = function(){
		var layoutItem = this.getSelectedLayoutItem();
		return layoutItem ? layoutItem.item.getErrors() : [];
	};
	
	
	/*
	* SelectPanels
	* 
	* options:
	*  items : [{name: <string>, item: <Form.Item> [, label: <string>][, category: <string>]}]
	*  label: <string>
	*  value: <string>
	*/
	Form.SelectPanels = function(opt){
		var self = this;
		
		var options = $.extend(true,{
			label: null,
			items: []
		},opt);
		
		// select
		this.select = new Form.Select({
			items: [],
			parent: this,
			onload: function(){
				this.change(function(e){
					e.stopPropagation();
					self.updateView();
					self.change();
					return false;
				});
			}
		});
		
		Form.Layout.call(this,options);
		
	}
	inherits(Form.SelectPanels,Form.Layout);
	
	Form.SelectPanels.prototype.createView = function(){
		var $view = $('<div>').addClass('f-selectpanels');
		
		this.$description = $('<p>');
		this.$content = $('<div>');
		
		var label = this.options.label===false ? false : (this.options.label || this.options.name);
		
		$view.append(
			$('<div class="form-group">').append(
				label ? ('<label>'+label+'</label>') : null,
				this.select.$view
			),
			this.$description,
			this.$content
		);
		
		return $view;
	}
	
	Form.SelectPanels.prototype.updateView = function(reason, layoutItem){
		Form.Layout.prototype.updateView.call(this);
		
		var self = this,
			selectedValue = this.select.getValue();
		
		if(reason == "addItem"){
			
			this.select.addOption(layoutItem.label || layoutItem.name, layoutItem.name || layoutItem.label, layoutItem.category);
			
			this.$content.append( layoutItem.item.$view );
			
		}
		else if(reason == "removeItem"){
			this.select.removeOption(layoutItem.name || layoutItem.label);
		}
		
		for(var i=0; i<this.layoutItems.length; i++){
			var selected = this.layoutItems[i].name === selectedValue;
			if(selected)
				this.$description.html(this.layoutItems[i].description || '');
			this.layoutItems[i].item.$view.toggle( selected );
		}
		
	}
	
	Form.SelectPanels.prototype.getLayoutItemByName = function(name){
		for(var i=0; i<this.layoutItems.length; i++){
			if(this.layoutItems[i].name === name)
				return this.layoutItems[i];
		}
	}
	
	Form.SelectPanels.prototype.getSelectedValue = function(){
		return this.select.getValue();
	}
	Form.SelectPanels.prototype.getSelectedLayoutItem = function(){
		return this.getLayoutItemByName(this.getSelectedValue());
	}
	Form.SelectPanels.prototype.setValue = function(v){
		if(!$.isPlainObject(v) || typeof v.type != 'string' || typeof v.value == 'undefined') return false;
		
		if(!Form.Item.prototype.setValue.call(this,v)) return false;
		
		if(this.select.setValue(v.type)){
			var layoutItem = this.getLayoutItemByName(v.type);
			if(layoutItem && layoutItem.item.value( v.value )){
				return true;
			}
		}
		return false;
	};
	Form.SelectPanels.prototype.getValue = function(){
		var selectedValue = this.getSelectedValue(),
			layoutItem = this.getLayoutItemByName(selectedValue);
		
		if(layoutItem){
			return {
				type: selectedValue,
				value: layoutItem.item.value()
			};
		};
	};
	Form.SelectPanels.prototype.getErrors = function(){
		var layoutItem = this.getSelectedLayoutItem();
		return layoutItem ? layoutItem.item.getErrors() : [];
	};
	
	Form.SelectPanels.prototype.setEnable = function(name, enable){
		this.select.setEnable(name, enable);
	};
	
	
	Form.SelectPanels.format = {
		Merge: {
			'in': function(value){
				var type = value.type;
				delete value.type;
				return {
					type: type,
					value: value
				};
			},
			'out': function(value){
				return $.extend({
					type: value.type
				}, value.value);
			}
		}
	};
	
	
	
	
	/*
	* FieldsEnabler
	* 
	* options:
	*  item : <Form.Item>
	*  label: <string>
	*  description: <string>
	*  state: <boolean>
	*/
	Form.FieldsEnabler = function(opt){
		var self = this;
		
		if(!$.isPlainObject(opt) || typeof opt.item == 'undefined')
			opt = {
				item: opt
			};
		
		opt.item = Form.toItem(opt.item);
		
		if(!opt.item) throw 'no item set';
		
		this.item = opt.item;
		this.item.setParent(this);
		
		this.cb = new Form.Checkbox({
			parent: this,
			value: opt.state,
			label: opt.label,
			onload: function(){
				this.change(function(e){
					e.stopPropagation();
					self.updateView();
					self.change();
					return false;
				});
			}
		});
		
		Form.Item.call(this,$.extend(true,{
			item: null,
			state: false,
			label: null,
			disabledValue: null
		},opt));
		
		this.cb.change();
		
	}
	inherits(Form.FieldsEnabler,Form.Item);
	
	Form.FieldsEnabler.prototype.toggle = function(state){
		if(typeof state == 'undefined')
			state = !this.cb.getValue();
		this.cb.setValue(state);
	};
	
	Form.FieldsEnabler.prototype.setValue = function(value){
		return this.item.value(value) && this.cb.setValue(true);
	};
	Form.FieldsEnabler.prototype.getValue = function(){
		if(this.cb.getValue())
			return this.item.value();
		else if(this.options.disabledValue)
			return typeof this.options.disabledValue == 'function' ? this.options.disabledValue.call(this) : this.options.disabledValue;
	};
	
	Form.FieldsEnabler.prototype.getErrors = function(){
		return this.cb.getValue() ? this.item.getErrors() : [];
	};
	
	Form.FieldsEnabler.prototype.createView = function(){
		var $view = $('<div class="f-fieldsenabler">');
		
		var description = this.options.description;
		if(typeof description == 'function')
			description = description.call(this);
		var $description = description && description!='' ? $('<p class="f-description">').html(description) : null;
		
		$view.append(
			$description,
			this.cb.$view,
			this.item.$view
		);
		
		return $view;
	}
	Form.FieldsEnabler.prototype.updateView = function(){
		Form.Item.prototype.updateView.call(this);
		
		this.cb.getValue() ? this.item.$view.slideDown(200,function(){
			$(this).show();
		}) : this.item.$view.slideUp(200,function(){
			$(this).hide();
		});
	}
	
	
	
	
	
	
	
	
	
	
	
	
	
	Form.Text = function(options){
		
		Form.Input.call(this, $.extend({
			value: '',
			suffix: null,
			prefix: null,
			readonly: false,
			comboboxValues: null
		},options));
		
	}
	inherits(Form.Text,Form.Input);
	
	Form.Text.prototype.createView = function(){
		var $view = $('<div class="f-text">'), self = this;
		
		this.$input = $('<input type="'+(this.options.password ? 'password' : 'text')+'" class="form-control">');
		this.$error_fb_ctrl = $('<span class="glyphicon glyphicon-remove form-control-feedback">');
		this.$error = $('<div class="alert alert-danger" role="alert">');
		
		if(typeof this.options.placeholder == 'string')
			this.$input.attr('placeholder', this.options.placeholder);
		if(this.options.readonly)
			this.$input.attr('disabled', 'disabled');
		if(this.options.focus)
			this.$input.attr('autofocus', 'autofocus');
		
		$view.append(
			this.options.suffix || this.options.prefix ? $('<div class="input-group">').append(this.options.prefix ? ('<span class="input-group-addon">'+this.options.prefix+'</span>') : null,this.$input,this.options.suffix ? ('<span class="input-group-addon">'+this.options.suffix+'</span>') : null) : this.$input,
			this.$error_fb_ctrl.hide(),
			this.$error.hide()
		);
		
		var timer = null;
		
		this.$input.change(function(){
			if(timer!==null){
				clearTimeout(timer);
				timer = null;
			}
			self.update();
		});
		
		setTimeout(function(){
			self.$input.keyup(function(){
				if(timer!==null)
					clearTimeout(timer);
				timer = setTimeout(function(){
					self.update();
				}, 250);
			});
		}, 1);
		
		this.setComboboxValues(this.options.comboboxValues);

		return $view;
	}
	
	Form.Text.prototype.setComboboxValues = function(items){
		
		if($.fn.typeahead){
			
			if($.isPlainObject(items)){
				var ni = [];
				Object.keys(items).forEach(function(k){
					ni.push({
						'name': items[k],
						'label': k
					});
				});
				items = ni;
			}
			
			this.$input.typeahead('destroy');
			this.$input.typeahead({
				source: items,
				showHintOnFocus: "all",
				items: 'all',
				highlighter: function(text, item){
					return typeof item.label == 'string' && item.label || text;
				}
			});
		}
		
	}
	
	Form.Text.prototype.updateView = function(reason){
		Form.Input.prototype.updateView.call(this);
		
		this.hasError() ? this.$error.html(this.getErrors()[0].message).show() : this.$error.hide();
		this.$view.toggleClass('has-error',this.hasError());
		this.$view.toggleClass('has-feedback',this.hasError());
		this.$error_fb_ctrl.toggle(this.hasError());
		
		if(!this.hasError() && reason !== 'updateError'){
			this.$input.val(this.value_ || '');
		}
	}
	
	Form.Text.prototype.getViewValue = function(){
		return this.$input.val() || '';
	}
	
	
	
	
	
	
	Form.Number = function(options){
		
		this.validators = [function(value){
			if(typeof value != 'number' || isNaN(value)) throw 'not a number';
			
			if(typeof this.options.minimum == 'number'){
				if(!this.options.exclusiveMinimum && value<this.options.minimum)
					throw 'The value must be greater than or equal to '+this.options.minimum;
				if(this.options.exclusiveMinimum && value<=this.options.minimum)
					throw 'The value must be greater than '+this.options.minimum;
			}
			if(typeof this.options.maximum == 'number'){		
				if(!this.options.exclusiveMaximum && value>this.options.maximum)
					throw 'The value must be lower than or equal to '+this.options.maximum;
				if(this.options.exclusiveMaximum && value>=this.options.maximum)
					throw 'The value must be lower than '+this.options.maximum;
			}
		}];
		
		Form.Input.call(this, $.extend({
			minimum: null,
			maximum: null,
			exclusiveMinimum: false,
			exclusiveMaximum: false,
			step: 1,
			value: 0
		},options));
		
	}
	inherits(Form.Number,Form.Input);
	
	Form.Number.prototype.createView = function(){
		var $view = $('<div class="f-number">'), self = this;
		
		this.$input = $('<input type="number" class="form-control">');
		this.$error_fb_ctrl = $('<span class="glyphicon glyphicon-remove form-control-feedback">');
		this.$error = $('<div class="alert alert-danger" role="alert">');
		
		if(typeof this.options.minimum == 'number')
			this.$input.attr('min',this.options.minimum);
		if(typeof this.options.maximum == 'number')
			this.$input.attr('max',this.options.maximum);
		if(typeof this.options.step == 'number')
			this.$input.attr('step',this.options.step);
		if(typeof this.options.placeholder == 'string')
			this.$input.attr('placeholder', this.options.placeholder);
		if(this.options.focus)
			this.$input.attr('autofocus', 'autofocus');
		
		$view.append(
			this.options.suffix || this.options.prefix ? $('<div class="input-group">').append(this.options.prefix ? ('<span class="input-group-addon">'+this.options.prefix+'</span>') : null,this.$input,this.options.suffix ? ('<span class="input-group-addon">'+this.options.suffix+'</span>') : null) : this.$input,
			this.$error_fb_ctrl.hide(),
			this.$error.hide()
		);
		
		this.$input.change(function(){
			self.update();
		});

		return $view;
	}
	
	Form.Number.prototype.updateView = function(reason){
		Form.Input.prototype.updateView.call(this);
		
		if(!this.hasError() && reason !== 'updateError')
			this.$input.val(this.value_);
		
		this.hasError() ? this.$error.html(this.getErrors()[0].message).show() : this.$error.hide();
		this.$view.toggleClass('has-error',this.hasError());
		this.$view.toggleClass('has-feedback',this.hasError());
		this.$error_fb_ctrl.toggle(this.hasError());
	}
	
	Form.Number.prototype.getViewValue = function(){
		return Number(this.$input.val());
	}
	
	
	
	Form.Select = function(opt){
		
		this.__index = 0;
		this._keys = [];
		this._values = [];
		this._index = [];
		
		var self = this;
		
		if(Array.isArray(opt) || ($.isPlainObject(opt) && typeof opt.items == 'undefined')){
			opt = {
				items: opt
			};
		}
		
		opt = opt || {
			items: []
		};
		
		var validators = [function(value){
			if(value !== null){
				var ok = false;
				(Array.isArray(value) && this.options.multiple ? value : [value]).forEach(function(valuetotest){
					this._values.forEach(function(v){
						if(isEqual(v, valuetotest)){
							ok = true;
							return false;
						}
					}, this);
					if(!ok) throw 'unknown value';
				}, this);
			}
		}];
		
		if(Array.isArray(opt.validators)) validators = validators.concat(opt.validators);
		
		opt.validators = validators;
		
		Form.Input.call(this, opt);
		
	}
	inherits(Form.Select,Form.Input);
	
	Form.Select.prototype.create = function(){
		this.setOptions(this.options.items);
	}
	
	Form.Select.prototype.addOption = function(label, value, category){
		
		var key = String(label), val = value, index = String(this.__index++);
		
		if(typeof val == 'undefined'){
			val = label;
		}
		
		this._keys.push(key);
		this._values.push(val);
		this._index.push(index);
		
		var $select = this.$input, first = !this.options.multiple && $select.find('option').length==0;
		var html = '<option '+(first?'selected':'')+' value="'+index+'" data-content=\''+key+'\'>'+key+'</option>';
		if(category){
			// find out if the category already exist
			var $cat = $select.find('optgroup[label="'+category+'"]');
			if(!$cat.length){
				$cat = $('<optgroup label="'+category+'">').appendTo($select);
			}
			$cat.append(html);
		} else {
			$select.append(html);
		}
		
		if($.fn.selectpicker){
			$select.selectpicker('refresh');
		}
		
		this.$input.change();
		return this;
	}
	
	Form.Select.prototype.setOptions = function(values){
		var currentValue = this.getValue();
		
		var keys = [], vals = [], index = [], categories = [];
		
		if(Array.isArray(values)){
			for(var i=0; i<values.length; i++){
				keys.push( String(values[i]) );
				vals.push(values[i]);
				categories.push(null);
			}
		} else if($.isPlainObject(values)){
			for(var i in values){
				if($.isPlainObject(values[i])){
					var category = String(i);
					for(var j in values[i]){
						keys.push( String(j) );
						vals.push(values[i][j]);
						categories.push(category);
					}
				} else {
					keys.push( String(i) );
					vals.push(values[i]);
					categories.push(null);
				}
			}
		}
		
		// construct the index
		for(var i=0; i<vals.length; i++){
			index.push(String(this.__index++)); // must be unique !
		}
		
		this._keys = keys;
		this._values = vals;
		this._index = index;
		
		// build the options
		this.$input.find('option,optgroup').remove();
		for(var i=0; i<vals.length; i++){
			
			var dataContent = "";
			
			if(/<[^>]+>/.test(keys[i]))
				dataContent = 'data-content=\''+keys[i]+'\'';
			
			var html = '<option value="'+index[i]+'" '+dataContent+'>'+keys[i]+'</option>',
				category = categories[i];
			
			if(category){
				// find out if the category already exist
				var $cat = this.$input.find('optgroup[label="'+category+'"]');
				if(!$cat.length){
					$cat = $('<optgroup label="'+category+'">').appendTo(this.$input);
				}
				$cat.append(html);
			} else {
				this.$input.append(html);
			}
			
		}
		
		if(!this.options.multiple)
			this.$input.find('option').first().attr('selected','selected');
		
		if($.fn.selectpicker){
			this.$input.selectpicker('refresh');
		}
		
		if(typeof currentValue == 'undefined' || currentValue === null || !this.setValue(currentValue, true))
			this.$input.change();
		
		return this;
	}
	
	Form.Select.prototype._getPos = function(value){
		// find the index of this value
		for(var i=0; i<this._values.length; i++){
			if(isEqual(value, this._values[i]))
				return i;
		}
		return null;
	}
	
	Form.Select.prototype.removeOption = function(value){
		// find the index of this value
		var pos = this._getPos(value);
		if(pos !== null){
			
			this.$input.find('option[value="'+this._index[pos]+'"]').remove();
			
			// remove any empty optgroup
			this.$input.find('optgroup:parent').remove();
			
			this._index.splice(pos,1);
			this._keys.splice(pos,1);
			this._values.splice(pos,1);
			
			if($.fn.selectpicker){
				this.$input.selectpicker('refresh');
			}
			
			if(isEqual(value, this.value_))
				this.setValue(null,true);
			else
				this.$input.change();
		}
		return this;
	}
	
	Form.Select.prototype.clear = function(){
		this._keys = [];
		this._values = [];
		this._index = [];
		
		this.$input.find('option, optgroup').remove();
		
		if($.fn.selectpicker){
			this.$input.selectpicker('refresh');
		}
		this.$input.change();
		return this;
	}
	
	Form.Select.prototype.createView = function(){
		var $view = $('<div class="f-select">'), self = this;
		
		this.$input = $('<select class="form-control">');
		this.$error = $('<div class="alert alert-danger" role="alert">');
		
		if(this.options.multiple)
			this.$input.attr('multiple','multiple');
		
		if(this.options.readonly)
			this.$input.attr('disabled','disabled');
		
		if(this.options.focus)
			this.$input.attr('autofocus', 'autofocus');
		
		$view.append(
			this.$input,
			this.$error.hide()
		);
		
		this.$input.change(function(){
			self.update();
		});
		
		if($.fn.selectpicker){
			self.$input.selectpicker({
				showTick: true
			});
		};

		return $view;
	}
	
	Form.Select.prototype.updateView = function(reason){
		Form.Input.prototype.updateView.call(this);
		
		if(!this.hasError() && reason !== 'updateError'){
			if(this.value_===null){
				this.$input.val(null);
			} else {
				var vv = Array.isArray(this.value_) ? this.value_ : [this.value_];
				var indexes = [];
				vv.forEach(function(v){
					var pos = this._getPos(v);
					if(pos!==null) indexes.push(this._index[pos]);
				}, this);
				this.$input.val(this.options.multiple ? indexes : indexes[0]);
			}
			
			if($.fn.selectpicker)
				this.$input.selectpicker('render');
		}
		
		this.hasError() ? this.$error.html(this.getErrors()[0].message).show() : this.$error.hide();
		this.$view.toggleClass('has-error',this.hasError());
	}
	
	Form.Select.prototype.getViewValue = function(){
		var indexes = this.$input.val();
		if(indexes===null) return null; // nothing selected !
		
		
		// get the value of the associated index
		if(!Array.isArray(indexes)) indexes = [indexes];
		var vv = [];
		indexes.forEach(function(index){
			for(var i=0; i<this._index.length; i++){
				if(this._index[i] == index){
					vv.push(this._values[i]);
					break;
				}
			}
		}, this);
		
		return this.options.multiple ? vv : vv[0];
	}
	Form.Select.prototype.setEnable = function(value, enable){
		var pos = this._getPos(value);
		if(pos !== null){
			var $opt = this.$input.find('option[value="'+this._index[pos]+'"]');
			!!enable ? $opt.removeAttr('disabled') : $opt.attr('disabled','disabled');
			
			if($.fn.selectpicker){
				this.$input.selectpicker('refresh');
			}
			
			if(isEqual(value, this.value_))
				this.setValue(null,true);
			else
				this.$input.change();
		}
		return this;
	}
	
	
	
	Form.Textarea = function(options){
		
		this.validators = [function(value){
			if(typeof value != 'string') throw 'not a string';
		}];
		
		Form.Input.call(this, $.extend({
			value: ''
		},options));
	}
	inherits(Form.Textarea,Form.Input);
	
	Form.Textarea.prototype.createView = function(){
		var $view = $('<div class="f-textarea">'), self = this;
		
		this.$input = $('<textarea class="form-control">');
		this.$error_fb_ctrl = $('<span class="glyphicon glyphicon-remove form-control-feedback">');
		this.$error = $('<div class="alert alert-danger" role="alert">');
		
		if(typeof this.options.placeholder == 'string')
			this.$input.attr('placeholder', this.options.placeholder);
		
		if(this.options.focus)
			this.$input.attr('autofocus', 'autofocus');
		
		$view.append(
			this.$input,
			this.$error_fb_ctrl.hide(),
			this.$error.hide()
		);
		
		this.$input.change(function(){
			self.update();
		});

		return $view;
	}
	
	Form.Textarea.prototype.updateView = function(reason){
		Form.Input.prototype.updateView.call(this);
		
		if(!this.hasError()  && reason !== 'updateError')
			this.$input.val(this.value_ || '');
		
		this.hasError() ? this.$error.html(this.getErrors()[0].message).show() : this.$error.hide();
		this.$view.toggleClass('has-error',this.hasError());
		this.$view.toggleClass('has-feedback',this.hasError());
		this.$error_fb_ctrl.toggle(this.hasError());
	}
	
	Form.Textarea.prototype.getViewValue = function(){
		return this.$input.val() || '';
	}
	
	
	
	Form.Checkbox = function(options){
		
		this.validators = [function(value){
			if(typeof value != 'boolean') throw 'not a boolean';
		}];
		
		Form.Input.call(this, $.extend({
			value: false
		},options));
		
	}
	inherits(Form.Checkbox,Form.Input);
	
	Form.Checkbox.prototype.createView = function(){
		var $view = $('<div class="f-checkbox checkbox checkbox-slider--c"><label><input type="checkbox"><span></span></label></div>'), self = this;
		
		this.$input = $view.find('input');
		
		if(this.options.focus)
			this.$input.attr('autofocus', 'autofocus');
		
		if(this.options.label){
			$view.find('label > span').html(this.options.label);
		}
		
		this.$input.change(function(){
			self.update();
		});

		return $view;
	}
	
	Form.Checkbox.prototype.updateView = function(reason){
		var self = this;
		Form.Input.prototype.updateView.call(this);
		if(!this.hasError()  && reason !== 'updateError'){
			this.$input.prop('checked',!!this.value_);
		}
		this.$view.toggleClass('has-error',this.hasError());
	}
	
	Form.Checkbox.prototype.getViewValue = function(){
		return !!this.$input.prop('checked');
	}
	
	
	Form.Color = function(options){
		
		this.validators = [function(value){
			if(typeof value != 'string' || !/^#[0-9a-f]{6}$/i.test(value)) throw 'not a color hexadecimal string';
		}];
		
		Form.Input.call(this, $.extend({
			value: '#000000'
		},options));
	}
	inherits(Form.Color,Form.Input);
	
	Form.Color.prototype.createView = function(){
		var $view = $('<div class="f-color">'), self = this;
		
		this.$input = $('<input type="color" class="form-control">');
		this.$error = $('<div class="alert alert-danger" role="alert">');
		
		if(this.options.focus)
			this.$input.attr('autofocus', 'autofocus');
		
		$view.append(
			this.$input,
			this.$error.hide()
		);
		
		this.$input.change(function(){
			self.update();
		});

		return $view;
	}
	
	Form.Color.prototype.updateView = function(reason){
		Form.Input.prototype.updateView.call(this);
		
		if(!this.hasError() && reason !== 'updateError')
			this.$input.val(this.value_ || '#000000');
		
		this.hasError() ? this.$error.html(this.getErrors()[0].message).show() : this.$error.hide();
	}
	
	Form.Color.prototype.getViewValue = function(){
		return this.$input.val() || '#000000';
	}
	
	
	
	Form.DateTime = function(options){
		
		this.validators = [function(value){
			if(typeof value != 'string' || !Form.DateTime.re_iso8601.test(value)) throw 'not a valid date (ISO8601)';
		}];
		
		Form.Input.call(this, $.extend({
			value: (new Date()).toISOString()// date of the day
		},options));
		
	}
	inherits(Form.DateTime,Form.Input);
	
	Form.DateTime.prototype.createView = function(){
		var $view = $('<div class="f-datetime">'), self = this;
		
		this.$input = $('<input type="datetime" class="form-control" placeholder="2016-04-22T06:00:00Z" />');
		this.$error = $('<div class="alert alert-danger" role="alert">');
		
		$view.append(
			this.$input,
			this.$error.hide()
		);
		
		this.$input.change(function(){
			self.update();
		});
		
		
		if($.fn.datetimepicker){
			var currentValue = self.$input.val();
			self.$input.remove();
			
			var $d = $('<div class="input-group date">'+
				'<input type="text" class="form-control" />'+
				'<span class="input-group-addon">'+
					'<span class="glyphicon glyphicon-calendar"></span>'+
				'</span>'+
			'</div>').prependTo($view);
			
			$d.datetimepicker({
				defaultDate: currentValue
			});
			$d.on('dp.change',function(){
				self.update();
			});
			
			self.$input = $d;
		};

		return $view;
	}
	
	Form.DateTime.prototype.updateView = function(reason){
		Form.Input.prototype.updateView.call(this);
		
		if(!this.hasError() && reason !== 'updateError')
			$.fn.datetimepicker ? this.$input.datetimepicker('date',this.value_ || null) : this.$input.val(this.value_ || null);
		
		this.hasError() ? this.$error.html(this.getErrors()[0].message).show() : this.$error.hide();
	}
	
	Form.DateTime.prototype.getViewValue = function(){
		if($.fn.datetimepicker){
			var d = this.$input.datetimepicker('date');
			return d ? d.format() : null;
		} else {
			return this.$input.val();
		}
	}
	
	Form.DateTime.re_iso8601 = /\d{4}-[01]\d-[0-3]\dT[0-2]\d:[0-5]\d:[0-5]\d(\.\d*)?([+-][0-2]\d:[0-5]\d|Z)/;
	
	
	
	
	Form.Duration = function(options){
		
		this.validators = [function(value){
			if(typeof value != 'number' || isNaN(value)) throw 'not a number';
			if(value<0) throw 'The value must be greater than or equal to 0';
		}];
		
		Form.Input.call(this, $.extend({
			minute: true, // show minute
			hour: true, // show hour
			day: true, // show day
			value: 0
		},options));
		
	}
	inherits(Form.Duration,Form.Input);
	
	Form.Duration.prototype.createView = function(){
		var $view = $('<div class="f-duration">'), self = this;
		
		this.$input = $('<div class="form-inline">');
		this.$error = $('<div class="alert alert-danger" role="alert">');
		
		function createInput(name){
			var uid = Math.random()*10000000,
				$input = $('<input class="form-control" id="'+uid+'" name="'+name+'" type="number" step="1" value="0" min="0">');
			
			$('<div class="form-group">').append(
				$input,
				'<label for="'+uid+'">'+name+'(s)</label>'
			).appendTo(self.$input);
			
			$input.change(function(){
				self.update();
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
		
		$view.append(
			this.$input,
			this.$error.hide()
		);

		return $view;
	}
	
	Form.Duration.prototype.updateView = function(reason){
		Form.Input.prototype.updateView.call(this);
		
		if(!this.hasError() && reason !== 'updateError'){
			
			var secondes = this.value_,
				day = Math.floor(secondes / 86400),
				hour = Math.floor((secondes - day * 86400) / 3600),
				minute = Math.floor((secondes-day*86400-hour*3600) / 60);
			
			this.$input.find('input[name="day"]').val(day);
			this.$input.find('input[name="hour"]').val(hour);
			this.$input.find('input[name="minute"]').val(minute);
		}
		
		this.hasError() ? this.$error.html(this.getErrors()[0].message).show() : this.$error.hide();
	}
	
	Form.Duration.prototype.getViewValue = function(){
		var seconds = 0;
		seconds += 86400 * parseInt(this.$input.find('input[name="day"]').val() || 0);
		seconds += 3600 * parseInt(this.$input.find('input[name="hour"]').val() || 0);
		seconds += 60 * parseInt(this.$input.find('input[name="minute"]').val() || 0);
		return seconds;
	}
	
	
	
	
	
	Form.File = function(options){
		
		this.validators = [function(value){
			if(typeof value != 'string' && value!==null) throw 'not a valid content';
		}];
		
		Form.Input.call(this, $.extend(true,{
			accept: null, // The accept attribute specifies the types of files that is accepted (ie : '.csv,.tsv,.tab,text/plain' )
			title: 'browse', // the title of the file dialog
			base64: true, // if false, return the value as a text string
			value: null
		}, options));
		
	}
	inherits(Form.File,Form.Input);
	
	Form.File.prototype.createView = function(){
		var $view = $('<div class="f-file">'), self = this;
		
		this.$fileSelector = $('<input type="file">').change(function(){
			var file = this.files && this.files[0] ? this.files[0] : null;
			
			if(file && FileReader){
				var fr = new FileReader();
				fr.onloadend = function(){
					var data = fr.result;
					if(self.options.base64){
						// transform the result into a base64 string
						var binary = '',
							bytes = new Uint8Array(data);
						for (var i = 0; i < bytes.byteLength; i++) {
							binary += String.fromCharCode( bytes[ i ] );
						}
						data = btoa(binary);
					}
					self.setViewValue(data, file.name);
					self.update();
				};
				self.options.base64 ? fr.readAsArrayBuffer(file) : fr.readAsText(file);
			}
			// else cancelled 
			
		});
		this.$removeBtn = $('<button class="btn btn-default btn-link btn-xs"><span class="glyphicon glyphicon-trash" aria-hidden="true"></span></button>').click(function(){
			self.setViewValue();
			self.update();
		});
		var $btn = $('<button class="btn btn-default">'+this.options.title+'</button>').click(function(){
			self.$fileSelector.click();
			return false;
		});
		
		this.$info = $('<span>');
		this.$error = $('<div class="alert alert-danger" role="alert">');
			
		if(this.options.accept)
			this.$fileSelector.attr('accept',this.options.accept);
		
		this.setViewValue();
		
		$view.append($btn, this.$removeBtn, ' ', this.$info, this.$error.hide());

		return $view;
	}
	
	Form.File.prototype.updateView = function(reason){
		Form.Input.prototype.updateView.call(this);
		
		if(!this.hasError() && reason !== 'updateError')
			this.setViewValue(this.value_);
		
		this.hasError() ? this.$error.html(this.getErrors()[0].message).show() : this.$error.hide();
	}
	
	Form.File.prototype.getViewValue = function(){
		return this.$fileSelector.data('data') || null;
	}
	
	// size to string
	function sizeToString(s){
		s = parseInt(s);
		if(isNaN(s)) return '-';
		var coef = 0.9;
		if (s > 1073741824 * coef)
			s = (Math.floor((s / 1000000000) * 100 ) / 100) + ' GB';
		else if (s > 1048576 * coef)
			s = (Math.floor((s / 1000000) * 100) / 100) + ' MB';
		else if (s > 1000 * coef)
			s = (Math.floor((s / 1024) * 100) / 100) + ' KB';
		else
			s = s + ' B';
		return s;
	}
	
	Form.File.prototype.setViewValue = function(value, filename){
		if(value){
			this.$removeBtn.show();
			this.$info.text((filename ? filename+' - ' : '') + sizeToString(this.options.base64 ? value.length*0.75 : value.length));
			this.$fileSelector.data('data', value);
			this.$fileSelector.data('filename', filename || null );
		}
		else {
			this.$removeBtn.hide();
			this.$info.text('no selection');
			this.$fileSelector.removeData('data');
			this.$fileSelector.removeData('filename');
		}
	}
	
	Form.File.prototype.getFile = function(){
		var input = this.$fileSelector[0];
		return input.files && input.files[0] ? input.files[0] : null;
	}
	
	
	
	
	Form.Image = function(options){
		
		this.validators = [function(value){
			if(typeof value != 'string' && value!==null) throw 'not a valid image content';
		}];
		
		Form.Input.call(this, $.extend(true,{
			accept: 'image/*', // The accept attribute specifies the types of files that is accepted (default : 'image/*' )
			imageTransform: null, // function(File) -> File|Blob|deferred
			value: null
		}, options));
		
	}
	inherits(Form.Image,Form.Input);
	
	// private
	function setFromFile(file){
		var self = this,
			imageTransform = self.options.imageTransform == 'function' ? self.options.imageTransform : function(v){return v;};
		$.when(imageTransform.call(self,file)).done(function(transformedBlob){
			var fr = new FileReader();
			fr.onloadend = function(){
				// transform the result into a base64 string
				var binary = '',
					bytes = new Uint8Array(fr.result);
				for (var i = 0; i < bytes.byteLength; i++) {
					binary += String.fromCharCode( bytes[ i ] );
				}
				var data = btoa(binary);
				self.setViewValue(data, file.name);
				self.update();
			};
			fr.readAsArrayBuffer(transformedBlob);
		});
	}
	
	Form.Image.prototype.setValue = function(value){
		
		if(value instanceof Blob){
			setFromFile.call(this, value);
			return true;
		}
		
		var is_url = false, self = this;
		try {
			Form.validator.Url(value);
			is_url = true;
		} catch(e){}
		
		if(is_url){
			
			var oReq = new XMLHttpRequest();
			oReq.open("GET", value, true);
			oReq.responseType = "blob";
			oReq.onload = function(oEvent) {
				self.setValue(oReq.response);
			};
			oReq.send();
			
			return true;
		}
		
		Form.Input.prototype.setValue.call(this, value);
	}
	
	Form.Image.prototype.createView = function(){
		var $view = $('<div class="f-image">'), self = this;
		
		this.$fileSelector = $('<input type="file">');
		this.$defaultImg = $('<div class="f-image-thumbnail-empty">empty</div>');
		this.$preview = $('<img>');
		this.$info = $('<div class="f-image-meta"></div>');
		this.$browseBtn = $('<button class="btn btn-primary btn-xs">Browse</button>');
		this.$removeBtn = $('<button class="btn btn-default btn-xs">Remove</button>');
		this.$error = $('<div class="alert alert-danger" role="alert">');
		
		this.$fileSelector.change(function(){
			var file = this.files && this.files[0] ? this.files[0] : null;
			
			if(file && FileReader){
				setFromFile.call(self, file);
			}
			// else cancelled 
			
		});
		
		this.$browseBtn.click(function(){
			self.$fileSelector.click();
			return false;
		});
		this.$removeBtn.click(function(){
			self.setViewValue();
			self.update();
		});
			
		if(this.options.accept)
			this.$fileSelector.attr('accept',this.options.accept);
		
		$view.append(
			this.$defaultImg,
			this.$preview,
			this.$info,
			$('<div class="f-image-btns">').append(this.$browseBtn,this.$removeBtn),
			this.$error.hide()
		);
		
		this.setViewValue();
		
		
		// drop feature
		var collection = $();
		$view.on('dragenter', function(e) {
		  if (collection.length === 0) {
			$view.addClass('f-image-drop');
			
		  }
		  collection = collection.add(e.target);
		});

		$view.on('dragleave drop', function(e) {
		  collection = collection.not(e.target);
		  if (collection.length === 0) {
			$view.removeClass('f-image-drop');
		  }
		});
		
		$view.on('dragover', function(e) {
			e.preventDefault(); // Cancel drop forbidding
			e.stopPropagation();
			return false;
		});
		
		$view.on('drop', function(e) {	
			if(e.originalEvent.dataTransfer){
				var dataTransfer = e.originalEvent.dataTransfer;
			   if(dataTransfer.files.length == 1) {
					// Stop the propagation of the event
					e.preventDefault();
					e.stopPropagation();
					
					// fetch FileList object
					var file = dataTransfer.files[0];

					if(/^image\//.test(file.type))
						setFromFile.call(self, file);
			   }
			}
			return false;
		});
		

		return $view;
	}
	
	Form.Image.prototype.updateView = function(reason){
		Form.Input.prototype.updateView.call(this);
		
		if(!this.hasError() && reason !== 'updateError')
			this.setViewValue(this.value_, null);
		
		this.hasError() ? this.$error.html(this.getErrors()[0].message).show() : this.$error.hide();
	}
	
	Form.Image.prototype.getViewValue = function(){
		return this.$fileSelector.data('data') || null;
	}
	
	Form.Image.prototype.setViewValue = function(value, filename){
		if(value){
			this.$preview.attr('src','data:image/png;base64,'+value).show();
			this.$defaultImg.hide();
			this.$removeBtn.show();
			this.$info.text((filename ? filename+' - ' : '') + sizeToString(value.length*0.75)).show();
			this.$fileSelector.data('data', value);
			this.$fileSelector.data('filename', filename || null );
		}
		else {
			this.$preview.attr('src','').hide();
			this.$defaultImg.show();
			this.$removeBtn.hide();
			this.$info.hide();
			this.$fileSelector.removeData('data');
			this.$fileSelector.removeData('filename');
		}
	}
	
	Form.Image.prototype.getFile = function(){
		var input = this.$fileSelector[0];
		return input.files && input.files[0] ? input.files[0] : null;
	}
	
	
	
	
	
	
	
	
	Form.CustomInput = function(options){
		
		Form.Input.call(this, $.extend(true,{
			input: null,
			get: null,
			set: null
		},options));
		
	}
	inherits(Form.CustomInput,Form.Input);
	
	Form.CustomInput.prototype.createView = function(){
	
		var $view = $('<div class="f-custominput">'), self = this;
		
		this.$input = this.options.input.call(this);
		this.$error = $('<div class="alert alert-danger" role="alert">');
		
		$view.append(
			this.$input,
			this.$error.hide()
		);

		return $view;
	}
	
	Form.CustomInput.prototype.updateView = function(reason){
		/*var hasError = this.value_ instanceof Error;
		this.$view.toggleClass('f-has-error',hasError);
		
		hasError ? this.$error.html(this.value_.message).show() : this.$error.hide();
		
		if(!hasError)
			return this.options.set.call(this,this.$input, this.value_);*/
		
		Form.Input.prototype.updateView.call(this);
		
		this.hasError() ? this.$error.html(this.getErrors()[0].message).show() : this.$error.hide();
		
		if(!this.hasError() && reason !== 'updateError')
			return this.options.set.call(this,this.$input, this.value_);
	}
	
	Form.CustomInput.prototype.getViewValue = function(){
		return this.options.get.call(this,this.$input);
	}
	
	/*Form.CustomInput.prototype.setValue = function(value){
		return Form.Input.prototype.setValue.call(this, value, true);
	}*/
	
	
	
	
	
	
	
	
	
	
	
	
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
			t = !(value === null || value === {} || typeof_ == 'undefined' || $.isEmptyObject(value));
		
		if(!t)
			throw 'The value must not be empty';
	}
	
	Form.validator.RegExp = function(regexp){
		return function(value){
			return (typeof value == 'string') ? regexp.test(value) : false;
		};
	}
	
	Form.validator.Integer = function(value){
		if(!( (typeof value == 'string' && /^[+-]?[0-9]+$/.test(value)) || (typeof value == 'number' && isFinite(value) && Math.floor(value) === value) ))
			throw 'The value must be an integer';
	}
	
	var url_re = new RegExp('^((https?:)?\\/\\/)?'+ // protocol
		'((([a-z\\d]([a-z\\d-]*[a-z\\d])*)\\.)+[a-z]{2,}|'+ // domain name
		'((\\d{1,3}\\.){3}\\d{1,3})|'+ // OR ip (v4) address
		'localhost)'+ // or localhost
		'(\\:\\d+)?(\\/[-a-z\\d%_.~+]*)*'+ // port and path
		'(\\?[;&a-z\\d%_.~+=-]*)?'+ // query string
		'(\\#[-a-z\\d_]*)?$','i'); // fragment locator
	
	Form.validator.Url = function(value){
		if(typeof value != 'string' || !url_re.test(value)) throw 'not a valid URL';
	}
	
	var mail_re = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
	
	Form.validator.Email = function(value){
		if(typeof value != 'string' || !mail_re.test(value)) throw 'not a valid email';
	}	
	
	
	
	/*
	*
	* JSON schema
	*
	*/
	
	
	Form.fromJsonSchema = function(schema, options){
		return schemaToItem(schema, options);
	}
	
	
	var schemaToItem = function(schema, options){
		
		var item = null;
		
		options = options || {};
		
		if(!$.isPlainObject(schema)){
			console.error(schema);
			throw 'the schema is not an object';
		}
		
		
		var type = typeof schema.type == 'undefined' ? autodetectType(schema) : schema.type;
		var isScalar = typeof type == 'string' && ['number','string','boolean','integer'].indexOf(type) !== -1;
		
		// special case : enum
		if(schema.enum){
			
			var enumItems = {};
			
			var arrIndex = 0, objIndex = 0;
			for(var i=0; i<schema.enum.length; i++){
				var key, value = schema.enum[i];
				
				// if type is given, limit the enum to the values with the correct type(s)
				if(Array.isArray(type)){
					if(type.indexOf(javascriptTypeToSchemaType(value)) === -1)
						continue;
				} else if(typeof type == 'string'){
					if(type !== javascriptTypeToSchemaType(value))
						continue;
				}
				
				switch(typeof value){
					case 'string':
					case 'number':
						key = String(value);
						break;
					case 'boolean':
						key = value ? 'true' : 'false';
						break;
					case 'object':
						if(value === null)
							key = 'null';
						else if(Array.isArray(value))
							key = 'array #'+(++arrIndex);
						else
							key = 'object #'+(++objIndex);
						break;
					default:
						console.error(value);
						throw 'invalid value in enum';
						break;
				}
				
				enumItems[key] = value;
			}
			
			options.items = enumItems;
			options.validators = [generateSchemaValidator(schema)];
			
			item = new Form.Select(options);
			
		}
		// special case : oneOf or anyOf
		else if((typeof schema.oneOf != 'undefined' || typeof schema.anyOf != 'undefined') && !isScalar ){
			
			var xxxOf = schema.oneOf || schema.anyOf;
			
			//let the user choose between the different schemas.
		
			var items = [];
			xxxOf.forEach(function(xxxOfSchema, index){
				items.push({
					name: 'schema #'+index,
					item: schemaToItem(xxxOfSchema)
				});
			});
			
			options.item = new Form.SelectPanels({
				items: items,
				format: {
					'out' : function(value){
						return value.value;
					},
					'in' : function(value){
						
						var type = null;
						
						// get the first item that validate the value
						// starting with the current
						var currentItem = this.getSelectedLayoutItem();
						if(currentItem && currentItem.validate(value) === true){
							type = currentItem.name;
						} else {
							for(var i=0; i<this.layoutItems.length; i++){
								if(this.layoutItems[i].item.validate(value) === true){
									type = this.layoutItems[i].name;
									break;
								}
							}
						}
						
						return {
							type: type,
							value: value
						};
					}
				}	
			});
			options.validators = [generateSchemaValidator(schema)];
			
			item = new Form.Wrapper(options);
			
		}
		else {
			
			
			if(Array.isArray(type)){
				item = multiTypedItem(schema, type, options); // type: ['string', 'number']
			}
			else if(typeof type == 'string'){
				
				options.validators = [generateSchemaValidator(schema)];
				
				switch(type){
					
					case 'number':
					case 'integer':
						
						if(typeof schema.minimum == 'number')
							options.minimum = schema.minimum;
						if(typeof schema.exclusiveMinimum != 'undefined')
							options.exclusiveMinimum = Boolean(schema.exclusiveMinimum);
						if(typeof schema.maximum == 'number')
							options.maximum = schema.maximum;
						if(typeof schema.exclusiveMaximum != 'undefined')
							options.exclusiveMaximum = Boolean(schema.exclusiveMaximum);
						
						item = new Form.Number(options);
						
						break;
						
					case 'string':
						
						if(schema.format === 'date-time'){
							item = new Form.DateTime(options);
						} else if(schema.format === 'email'){
							options.validators.push(Form.validator.Email);
							item = new Form.Text(options);
						} else if(schema.format === 'hostname'){
							options.validators.push(function(value){
								if(!/^(([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]*[a-zA-Z0-9])\.)*([A-Za-z0-9]|[A-Za-z0-9][A-Za-z0-9\-]*[A-Za-z0-9])$/i.test(value))
									throw 'invalid hostname';
							});
							item = new Form.Text(options);
						} else if(schema.format === 'ipv4'){
							options.validators.push(function(value){
								if(!/^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/.test(value))
									throw 'invalid ipv4';
							});
							item = new Form.Text(options);
						} else if(schema.format === 'ipv6'){
							options.validators.push(function(value){
								if(!/^((([0-9A-Fa-f]{1,4}:){7}[0-9A-Fa-f]{1,4})|(([0-9A-Fa-f]{1,4}:){6}:[0-9A-Fa-f]{1,4})|(([0-9A-Fa-f]{1,4}:){5}:([0-9A-Fa-f]{1,4}:)?[0-9A-Fa-f]{1,4})|(([0-9A-Fa-f]{1,4}:){4}:([0-9A-Fa-f]{1,4}:){0,2}[0-9A-Fa-f]{1,4})|(([0-9A-Fa-f]{1,4}:){3}:([0-9A-Fa-f]{1,4}:){0,3}[0-9A-Fa-f]{1,4})|(([0-9A-Fa-f]{1,4}:){2}:([0-9A-Fa-f]{1,4}:){0,4}[0-9A-Fa-f]{1,4})|(([0-9A-Fa-f]{1,4}:){6}((b((25[0-5])|(1d{2})|(2[0-4]d)|(d{1,2}))b).){3}(b((25[0-5])|(1d{2})|(2[0-4]d)|(d{1,2}))b))|(([0-9A-Fa-f]{1,4}:){0,5}:((b((25[0-5])|(1d{2})|(2[0-4]d)|(d{1,2}))b).){3}(b((25[0-5])|(1d{2})|(2[0-4]d)|(d{1,2}))b))|(::([0-9A-Fa-f]{1,4}:){0,5}((b((25[0-5])|(1d{2})|(2[0-4]d)|(d{1,2}))b).){3}(b((25[0-5])|(1d{2})|(2[0-4]d)|(d{1,2}))b))|([0-9A-Fa-f]{1,4}::([0-9A-Fa-f]{1,4}:){0,5}[0-9A-Fa-f]{1,4})|(::([0-9A-Fa-f]{1,4}:){0,6}[0-9A-Fa-f]{1,4})|(([0-9A-Fa-f]{1,4}:){1,7}:))$/.test(value))
									throw 'invalid ipv4';
							});
							item = new Form.Text(options);
						} else if(schema.format === 'uri'){
							options.validators.push(function(value){
								if(!/^(([^:\/?#]+):)?(\/\/([^\/?#]*))?([^?#]*)(\?([^#]*))?(#(.*))?/.test(value))
									throw 'invalid ipv4';
							});
							item = new Form.Text(options);
						} else if(schema.format === 'binary'){
							item = new Form.File(options);
						} else if(schema.format === 'text'){
							item = new Form.Textarea(options);
						} else {
							item = new Form.Text(options);
						}
						
						
						
						
						
						break;
						
					case 'boolean':
						
						options.items = {
							'true': true,
							'false':false
						};
						item = new Form.Select(options);
						
						break;
						
					case 'array':
						
						// cf: https://spacetelescope.github.io/understanding-json-schema/reference/array.html
						
						options.editable = true;
						
						var items = schema.items || {},
							additionalItems = typeof schema.additionalItems != 'undefined' ? schema.additionalItems : {},
							maxItems = schema.maxItems;
						
						if(typeof schema.allOf != 'undefined'){
							// extend the attributes
							schema.allOf.forEach(function(allOfSchema){
								if($.isPlainObject(allOfSchema.items) && $.isPlainObject(items))
									$.extend(true, items, allOfSchema.items);
								else if(Array.isArray(allOfSchema.items) && Array.isArray(items)){
									for(var i=0; i<allOfSchema.items.length; i++){
										if(i<items.length)
											$.extend(true, items[i], allOfSchema.items[i]);
										else
											items[i] = allOfSchema.items[i];
									}
								} else 
									items = allOfSchema.items;
								if(allOfSchema.additionalItems === false)
									additionalItems = false;
								else if($.isPlainObject(allOfSchema.additionalItems) && $.isPlainObject(additionalItems))
									$.extend(true, additionalItems, allOfSchema.additionalItems);
								if(typeof maxItems == 'undefined' || allOfSchema.maxItems<maxItems)
									maxItems = allOfSchema.maxItems;
							});
						}
						
						
						
						if($.isPlainObject(items)){
							// schema
							// additionalItems is meaningless
							options.instanciator = function(){
								return schemaToItem(items);
							};
							
						} else if(Array.isArray(items)){
							// array of schema
							
							var lis = [];
							items.forEach(function(schema){
								lis.push({
									item: schemaToItem(schema)
								});
							});
							options.items = lis;
							
							if(additionalItems === false){
								options.maxItems = items.length;
								options.editable = false;
							} else {
								options.instanciator = function(){
									var index = this.length();
									if(index < items.length){
										return schemaToItem(items[index]);
									} else {
										// extra element, use the additionalItems schema or {}
										return schemaToItem($.isPlainObject(additionalItems) ? additionalItems : {});
									}
								}
							}
							
							
						}
						
						
						if(typeof schema.maxItems == 'number'){
							options.maxItems = schema.maxItems;
						}
						
						item = new $.Form.ArrayLayout(options);
						
						break;
						
					case 'object':
						
						options.items = [];
						options.editable = true;
						options.skipOnDisabled = true;
						
						var required = schema.required || [],
							properties = schema.properties || {},
							additionalProperties = typeof schema.additionalProperties != 'undefined' ? schema.additionalProperties : {},
							patternProperties = $.isPlainObject(schema.patternProperties) ? schema.patternProperties : {};
						
						if(typeof schema.allOf != 'undefined'){
							// extend the attributes
							schema.allOf.forEach(function(allOfSchema){
								if(allOfSchema.required)
									required = required.concat(allOfSchema.required);
								if(allOfSchema.properties)
									$.extend(true, properties, allOfSchema.properties);
								if(allOfSchema.additionalProperties === false)
									additionalProperties = false;
								else if($.isPlainObject(allOfSchema.additionalProperties) && $.isPlainObject(additionalProperties))
									$.extend(true, additionalProperties, allOfSchema.additionalProperties);
								if(allOfSchema.patternProperties)
									$.extend(true, patternProperties, allOfSchema.patternProperties);
							});
						}
						
						required = uniq(required);
							
						for(var name in properties){
							options.items.push({
								name: name,
								item: schemaToItem(properties[name]),
								checkable: required.indexOf(name) === -1,
								description: $.isPlainObject(properties[name]) ? properties[name].description : null
							});
						}
						
						// add required parameters that are not in schema.properties
						required.forEach(function(name){
							if(typeof properties[name] == 'undefined')
								options.items.push({
									name: name,
									item: schemaToItem({}),
									checkable: false
								});
						});
						
						// aditional properties 
						if( additionalProperties === false && $.isEmptyObject(patternProperties) ){
							// limited to the properties defined in the 'properties' attribute
							options.editable = false;
						} else {
							
							options.instanciator = function(key){
								
								for(var re in patternProperties){
									if( (new RegExp(re)).test(key) ){
										return schemaToItem(patternProperties[re]);
									}
								}
								
								if(additionalProperties===false)
									return false; // not allowed
								
								return schemaToItem(additionalProperties===true ? {} : additionalProperties);
							};
							
						}
						
						item = new Form.FormLayout(options);
						
						break;
						
					default:
						
						throw 'invalid type '+type;
				}
			
			}
			else {
				
				// unable to find a type, may be anything : let the user decide
				item = multiTypedItem(schema, null, options); // type: ['string', 'number']
				
			}
		}
		
		if(typeof schema.default != 'undefined')
			item.value(schema.default);
		
		
		return item;
		
	}
	
	var javascriptTypeToSchemaType = function(value){
		var typeof_ = typeof value;
		if(typeof_ == 'undefined' || typeof_ == 'function'){ // invalid value
			return;
		}
		else if(typeof_ == 'object' && Array.isArray(value))
			typeof_ = 'array';
		return typeof_;
	}
	
	var multiTypedItem = function(schema, types, options){
		
		if(typeof types == 'string') types = [types];
		if(!types) types = ['boolean', 'object', 'string', 'number', 'array'];
		
		var items = [];
		types.forEach(function(type){
			items.push({
				name: type,
				item: schemaToItem($.extend({}, schema || {}, { type: type}))
			});
		});
		
		options = options || {};
		
		options.items = items;
		options.format = {
			'out' : function(value){
				return value.value;
			},
			'in' : function(value){
				var typeof_ = javascriptTypeToSchemaType(value);
				if(!typeof_){
					typeof_ = 'string';
					value = '';
				}
				return {
					type: typeof_,
					value: value
				};
			}
		};
		
		return new Form.SelectPanels(options);
	}
	
	var autodetectType = function(schema){
		
		if(typeof schema.type != 'undefined'){
			return schema.type;
		}
		if(typeof schema.properties != 'undefined' || typeof schema.maxProperties != 'undefined' || typeof schema.minProperties != 'undefined' || typeof schema.patternProperties != 'undefined' || typeof schema.additionalProperties != 'undefined' || typeof schema.dependencies != 'undefined' ){
			return 'object';
		}
		if(typeof schema.items != 'undefined' || typeof schema.additionalItems != 'undefined' || typeof schema.minItems != 'undefined' || typeof schema.maxItems != 'undefined' || typeof schema.uniqueItems != 'undefined' ){
			return 'array';
		}
		if(typeof schema.maxLength != 'undefined' || typeof schema.minLength != 'undefined' || typeof schema.pattern != 'undefined' ){
			return 'string';
		}
		if(typeof schema.multipleOf != 'undefined' || typeof schema.minimum != 'undefined' || typeof schema.maximum != 'undefined' ){
			return 'number';
		}
		
		if(Array.isArray(schema.enum)) {
			
			var types = [];
			schema.enum.forEach(function(enumItem){
				var type = javascriptTypeToSchemaType(enumItem);
				if(types.indexOf(type) === -1)
					types.push(type);
			});
			
			if(types.length==1){
				return types[0];
			} else {
				return types; // multi types detected !
			}
			
		}
		
		// try to find a type under the allOf, anyOf or oneOf
		var t = null;
		['allOf', 'anyOf', 'oneOf'].forEach(function(composeMode){
			if(Array.isArray(schema[composeMode])){
				var types = [];
				schema[composeMode].forEach(function(schema){
					var type = autodetectType(schema);
					if(typeof type != 'undefined' && types.indexOf(type) === -1)
						types.push(type);
				});
				if(types.length===1){
					t = types[0];
					return false;
				}
				if(types.length>1){
					t = types; // multi types detected !
					return false;
				}
			}
		});
		if(t!==null){
			return t;
		}
		
	}
	
	var generateSchemaValidator = function(schema, iterate){
		
		if(typeof iterate == 'undefined') iterate = true;
		
		// cf: https://spacetelescope.github.io/understanding-json-schema
		
		var validators = [];
		
		
		if(typeof schema.type == 'string' || Array.isArray(schema.type)){
			var allowedTypes = Array.isArray(schema.type) ? schema.type : [schema.type];
			validators.push(function(value){
				var type = javascriptTypeToSchemaType(value);
				if(type === 'number'){
					// special integer case
					if(allowedTypes.indexOf('integer') !== -1 && allowedTypes.indexOf('number') === -1){
						// must be a pure integer !
						if(!(isFinite(value) && Math.floor(value) === value))
							throw 'The value must be an integer';
						return;
					}
				}
				if(allowedTypes.indexOf(type) === -1)
					throw 'the value must be a '+allowedTypes.join(' or ');
			});
		}
		
		
		/*
		Number
		*/
		if(typeof schema.minimum == 'number'){
			validators.push(function(value){
				if(typeof value != 'number') return;
				if( schema.exclusiveMinimum ){
					if(value <= schema.minimum) throw 'the value must be greater than '+ schema.minimum
				} else {
					if(value < schema.minimum) throw 'the value must be greater than or equal to '+ schema.minimum
				}
			});
		}
		if(typeof schema.maximum == 'number'){
			validators.push(function(value){
				if(typeof value != 'number') return;
				if( schema.exclusiveMaximum ){
					if(value >= schema.maximum) throw 'the value must be lower than '+ schema.minimum
				} else {
					if(value > schema.maximum) throw 'the value must be lower than or equal to '+ schema.minimum
				}
			});
		}
		if(typeof schema.multipleOf == 'number' && schema.multipleOf !== 0){
			validators.push(function(value){
				if(typeof value != 'number') return;
				var r = value/schema.multipleOf;
				if(!( isFinite(r) && Math.floor(r) === r ))
					throw 'The value must be a multiple of '+schema.multipleOf;
			});
		}
		
		/*
		String
		*/
		if(schema.format === 'date-time'){
			validators.push(function(value){
				if(typeof value != 'string') return;
				if(Form.DateTime.re_iso8601.test(value)) throw 'not a valid date (ISO8601)';
			});
		}
		if(typeof schema.minLength == 'number'){
			validators.push(function(value){
				if(typeof value != 'string') return;
				if(value.length < schema.minLength)
					throw 'The length must be greater than or equal to '+schema.minLength;
			});
		}
		if(typeof schema.maxLength == 'number'){
			validators.push(function(value){
				if(typeof value != 'string') return;
				if(value.length > schema.maxLength)
					throw 'The length must be lower than or equal to '+schema.maxLength;
			});
		}
		if(typeof schema.pattern == 'string'){
			// is the pattern a valid regular expression ?
			var re = false;
			try {
				re = new RegExp(schema.pattern);
			} catch(e) {}
			if(re)
				validators.push(function(value){
					if(typeof value != 'string') return;
					if(!re.test(value))
						throw 'The value is invalid';
				});
		}
		
		/*
		Array
		*/
		
		
		if(Array.isArray(schema.items)){
			// array of schema
			
			if(schema.additionalItems === false){
				// no more than schema.items.length is allowed
				validators.push(function(value){
					if(!Array.isArray(value)) return;
					if(value.length>schema.items.length)
						throw 'additional items not allowed (max='+schema.items.length+')';
				});
			}
			
			if(iterate){
				// validate the children
				
				var itemsValidators = [], additionalItemsValidator = null;
				schema.items.forEach(function(schema){
					itemsValidators.push(generateSchemaValidator(schema, iterate));
				});
				if($.isPlainObject(schema.additionalItems)){
					additionalItemsValidator = generateSchemaValidator(schema.additionalItems, iterate);
				}
				validators.push(function(value){
					if(!Array.isArray(value)) return;
					for(var i=0; i<value.length; i++){
						try {
							if(i<schema.items.length){
								itemsValidators[i](value[i]);
							} else if( typeof additionalItemsValidator == 'function' ){
								additionalItemsValidator(value[i]);
							}
						} catch(e){
							throw 'Invalid item #'+i+': '+e;
						}
					}
				});
			
			}
			
		} else if($.isPlainObject(schema.items)){
			// schema
			// additionalItems is meaningless
			// all the items must match this schema
			if(iterate){
				var itemsValidator = generateSchemaValidator(schema.items, iterate);
				validators.push(function(value){
					if(!Array.isArray(value)) return;
					for(var i=0; i<value.length; i++){
						try {
							itemsValidator(value[i]);
						} catch(e){
							throw 'Invalid item #'+i+': '+e;
						}
					}
				});
			}
		}
		
		if(typeof schema.maxItems == 'number'){
			validators.push(function(value){
				if(!Array.isArray(value)) return;
				if(value.length > schema.maxItems)
					throw 'The number of items must be lower than or equal to '+schema.maxItems;
			});
		}
		if(typeof schema.minItems == 'number'){
			validators.push(function(value){
				if(!Array.isArray(value)) return;
				if(value.length < schema.minItems)
					throw 'The number of items must be greater than or equal to '+schema.minItems;
			});
		}
		if(typeof schema.uniqueItems === true){
			validators.push(function(value){
				if(!Array.isArray(value)) return;
				for(var i=0; i<value.length; i++){
					if(value.indexOf(value[i],i+1) != -1)
						throw 'All elements must be unique';
				}
			});
		}
		
		
		/*
		Object
		*/
		
		if(Array.isArray(schema.required) && schema.required.length){
			
			validators.push(function(value){
				if(!$.isPlainObject(value)) return;
				schema.required.forEach(function(name){
					if(typeof value[name] == 'undefined')
						throw 'property \''+name+'\' is required';
				});
			});
			
		}
		
		// properties 
		if(typeof schema.properties != 'undefined' || typeof schema.additionalProperties != 'undefined' || typeof schema.patternProperties != 'undefined'){
				
			var properties = $.isPlainObject(schema.properties) ? schema.properties : {};
			var patternProperties = $.isPlainObject(schema.patternProperties) ? schema.patternProperties : {};
			
			if(schema.additionalProperties===false){
				// no additional properties allowed
				
				validators.push(function(value){
					if(!$.isPlainObject(value)) return;
					Object.keys(value).forEach(function(name){
						
						if(typeof properties[name] == 'undefined'){
							// additional prop
							
							for(var re in patternProperties){
								if( (new RegExp(re)).test(name) ){
									return;
								}
							}
							
							throw 'additional property \''+name+'\' is not allowed';
						}
						
					});
				});
				
			}
			
			if(iterate){
				// validate the children
				
				var propertiesValidators = {};
				for(var name in properties){
					propertiesValidators[name] = generateSchemaValidator(properties[name], iterate);
				}
				var patternPropertiesValidators = {};
				for(var re in patternProperties){
					patternPropertiesValidators[re] = generateSchemaValidator(patternProperties[re], iterate);
				}
				var additionalPropertiesValidator = null;
				if($.isPlainObject(schema.additionalProperties))
					additionalPropertiesValidator = generateSchemaValidator(schema.additionalProperties, iterate);
				else if(schema.additionalProperties === false)
					additionalPropertiesValidator = false;
				
				
				validators.push(function(value){
					if(!$.isPlainObject(value)) return;
					Object.keys(value).forEach(function(name){
						try {
							if(typeof properties[name] == 'undefined'){
								// additional prop
								
								for(var re in patternProperties){
									if( (new RegExp(re)).test(name) ){
										patternPropertiesValidators[re](value[name]);
										return;
									}
								}
								
								if(typeof additionalPropertiesValidator == 'function'){
									additionalPropertiesValidator(value[name]);
								}
								
							} else {
								propertiesValidators[name](value[name]);
							}
						} catch(e){
							throw 'Invalid property \''+name+'\' : '+e;
						}
					});
				});
			
			}
			
		}
		
		
		if(typeof schema.maxProperties == 'number'){
			validators.push(function(value){
				if(!$.isPlainObject(value)) return;
				if(Object.keys(value).length > schema.maxProperties)
					throw 'The number of items must be lower than or equal to '+schema.maxProperties;
			});
		}
		if(typeof schema.minProperties == 'number'){
			validators.push(function(value){
				if(!$.isPlainObject(value)) return;
				if(Object.keys(value).length < schema.minProperties)
					throw 'The number of items must be greater than or equal to '+schema.minProperties;
			});
		}
		
		/*
		Generic
		*/
		if(Array.isArray(schema.enum)){
			validators.push(function(value){
				var pass = false;
				schema.enum.forEach(function(v){
					if(isEqual(v,value)){
						pass = true;
						return false;
					}
				});
				if(!pass)
					throw 'invalid value';
			});
		}
		
		
		/*
		Combining schemas
		*/
		if(Array.isArray(schema.allOf)){
			
			schema.allOf.forEach(function(schema){
				validators.push( generateSchemaValidator(schema, iterate) );
			});
			
		}
		if(Array.isArray(schema.anyOf)){
			
			var anyOfValidators = [];
			schema.anyOf.forEach(function(schema){
				anyOfValidators.push( generateSchemaValidator(schema, iterate) );
			});
			
			validators.push(function(value){
				var pass = false;
				anyOfValidators.forEach(function(validator){
					try {
						validator(value);
						pass = true;
						return false;
					} catch(e){}
				});
				if(!pass)
					throw 'invalid value';
			});
			
		}
		if(Array.isArray(schema.oneOf)){
			
			var oneOfValidators = [];
			schema.oneOf.forEach(function(schema){
				oneOfValidators.push( generateSchemaValidator(schema, iterate) );
			});
			
			validators.push(function(value){
				var pass = 0;
				oneOfValidators.forEach(function(validator){
					try {
						validator(value);
						pass++;
					} catch(e){}
				});
				if(pass!==1)
					throw 'invalid value';
			});
			
		}
		if($.isPlainObject(schema.not)){
			
			var notValidator = generateSchemaValidator(schema.not, iterate);
			
			validators.push(function(value){
				pass = false;
				try {
					notValidator(value);
				} catch(e){
					pass = true;
				}
				if(!pass)
					throw 'invalid value';
			});
			
		}
		
		return function(value){
			validators.forEach(function(validator){
				validator(value);
			});
		};
		
	}
	
	
	/* register as a plugin in jQuery */
	
	$.Form = Form;
	
	$.fn.form = function(){
		var args = [].slice.call(arguments);
		
		if (this[0]) { // this[0] is the renderTo div
			
			var instance = $(this[0]).data('form');
			
			if(instance){
				if(args.length){
					if(typeof args[0] == 'string'){
						// access the attribute or method
						var prop = instance[args.shift()];
						if(typeof prop == 'function'){
							var r = prop.apply(instance,args);
							return (r === instance) ? this : r; // make it chainable
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
			// /!\ NOTE : be sure to not emit any event in the constructor, or delay them using the setTimeout function !
			instance = new Form(this[0],args[0],args[1],args[2],args[3],args[4],args[5],args[6]);
			$(this[0]).data('form',instance);
			
			return this;
		}
	};
	
	
	return Form;

}));

