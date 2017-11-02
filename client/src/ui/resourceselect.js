(function (root, factory) {
    if (typeof define === 'function' && define.amd) {
        // AMD. Register as an anonymous module.
        define(['jquery','form','ething','bootstrap-select','./browser','css!./resourceselect'], factory);
    } else {
        // Browser globals
        root.ResourceSelect = factory(root.jQuery,root.Form,root.EThing);
    }
}(this, function ($, Form, EThing) {
	
	
	function toId(value){
		return Array.isArray(value) ? value.map(function(v){
			return v instanceof EThing.Resource ? v.id() : v;
		}) : ((value instanceof EThing.Resource) ? value.id() : value);
	}
	
	// make a tree from a list of resources
	function makeTree(resources, cb){
		
		function getChildren(resource){
			return EThing.arbo.find(function(r){
				var createdBy = r.createdBy();
				return createdBy && createdBy.id === resource.id();
			});
		}
		
		function hasParent(resource){
			return !!resource.createdBy();
		}
		
		function inSelection(resource){
			var found = false;
			resources.forEach(function(r){
				if(r.id()===resource.id()){
					found = true;
					return false;
				}
			});
			return found;
		}
		
		var level = 0;
		
		function add(parentItem, resource){
			var item = {
				resource: resource,
				parent: parentItem.resource,
				children: [],
				active: inSelection(resource),
				level: level
			};
			
			level++;
			getChildren(resource).forEach(function(r){
				add(item, r);
			});
			level--;
			
			if(item.active || item.children.length){
				parentItem.children.push(item);
			}
			
			return item;
		}
		
		var root = {
			resource: null,
			children: []
		};
		
		EThing.arbo.find().forEach(function(r){
			if(!hasParent(r)){
				add(root, r); // recursive
			}
		});
		
		if(typeof cb === 'function'){
			
			function iterate(item){
				item.children.forEach(function(c){
					cb(c);
					iterate(c);
				});
			}
			
			iterate(root);
			
		}
		
		return root.children;
	}
	
	
	/*
	
	example :
	
	$('#mydiv').resourceSelect({
	  filter: function(resource){
		return resource instanceof EThing.Table;
	  }
	}, function(){
		// is executed when this widget is fully loaded. 
	});
	
	*/
	
	var ResourceSelect = function(element, opt){
		var self = this;
		
		this.$element = $(element);
		this.options = $.extend(true,{
			filter: null, // filter function(resource) -> true|false|"disabled"
			allowCreation: false, // enable resource creation, can be an array to limit the creation on certains types only, e.g. ['Table','File']
			multiple: false, // false | true | integer
			value: null, // array of resource or one resource (a resource is euther a string ID or a EThing.Resource instance)
			title: 'No resource'+(opt.multiple?'s':'')+' selected',
			categorise: true,
			readonly: false,
			treeView: false
		}, opt);
		
		this.$element.addClass('resource-select');
		
		this.$select = $('<select>');
		
		if(this.options.multiple){
			this.$select.attr('multiple','multiple');
			if(typeof this.options.multiple == 'number')
				this.$select.attr('data-max-options',this.options.multiple);
			this.$select.attr('data-selected-text-format','count');
		}
		
		if(this.options.readonly){
			this.$select.attr('disabled','disabled');
		}
			
		this.$element.html(this.$select);
		
		this.$select.selectpicker({
			title: this.options.title,
			showTick: true,
			header: false, //this.options.multiple ? 'Select resources' : 'Select a resource',
			liveSearch: true,
			liveSearchNormalize: true,
			liveSearchPlaceholder: 'filter',
			noneSelectedText: 'no resource selected',
			countSelectedText: '{0} resources selected',
			size: false
		});
		
		this.$select.on('changed.bs.select', function(e,clickedIndex, select){
			self.change();
		});
		
		if(this.options.allowCreation){
			
			var allowedType = Array.isArray(this.options.allowCreation) ? this.options.allowCreation : ['File','Table','App','Device'];
			var $create_type = $('<select class="form-control">');
			var $create_name = $('<input type="text" class="form-control" autocomplete="off" placeholder="name">');
			var $create_btn = $('<button class="btn btn-primary" type="button"><span class="glyphicon glyphicon-plus" aria-hidden="true"></span><span class="hidden-xs"> create</span></button>');
			
			allowedType.forEach(function(type){
				$create_type.append('<option>'+type+'</option>');
			});
			$create_btn.click(function(e){
				e.preventDefault();
				
				var name = ($create_name.val()||'').trim(),
					type = $create_type.val();
				if(name && type){
					EThing[type].create({name:name});
				}
				
				return false;
			});
			
			$create_type.click(function(e){
				e.preventDefault();
				return false;
			});
			
			$('<div class="bs-create input-group">').append(
				allowedType.length > 1 ? $create_type : null,
				$create_name,
				$('<span class="input-group-btn">').html($create_btn)
			).insertBefore( this.$select.closest('.bootstrap-select').children('div.dropdown-menu').children('ul') );
			
		}
		
		EThing.on('ething.arbo.changed',function(){
			self.update();
		});
		
		this.update();
		
		if(this.options.value){
			this.setValue(this.options.value);
		}
		
	}
	
	ResourceSelect.prototype.change = function(handler){
		if(typeof handler == 'function'){
			var self = this;
			this.$element.on('changed.rs', function(){
				handler.call(self);
			});
		} else {
			var e = $.Event( 'changed.rs', { instance: this, data: handler } );
			this.$element.trigger(e);
		}
		return this;
	}
	
	
	
	
	ResourceSelect.prototype.update = function(){
		var currentValue = this.value();
		
		// get the resources according to the filter
		var resources = EThing.arbo.find();
		
		// rebuild the select input
		var optgrp = {}, itemsNb = 0, self = this;
		this.$select.empty();
		
		var resourcesFiltered = [];
		var resourcesDisabled = [];
		
		for(var i=0; i<resources.length; i++){
			var resource = resources[i], d;
			if(!(resource instanceof EThing.Folder) && (!this.options.filter || (d = this.options.filter.call(this,resource)))){
				resourcesFiltered.push(resource);
				if(d=='disabled')
					resourcesDisabled.push(resource);
			}
		}
		
		if(this.options.categorise){
			resourcesFiltered.forEach(function(r){
				var cat = r.baseType();
				if(typeof optgrp[cat] == 'undefined'){
					optgrp[cat] = {
						'$elem' : $('<optgroup label="'+cat+'">').appendTo(this.$select),
						'resources': []
					};
				}
				optgrp[cat].resources.push(r);
			}, this);
		} else {
			optgrp['root'] = {
				'$elem' : this.$select,
				'resources': resourcesFiltered
			};
		}
		
		function makeView(r, dis, level){
			var tab = '';
			for(var i=0; i<level||0; i++) tab+='&nbsp;&nbsp;';
			var disabled = dis || resourcesDisabled.indexOf(r) !== -1;
			return '<option '+(disabled ? 'disabled' : '')+' data-content=\''+tab+ResourceSelect.resourceToSelectDataContent(r, self.options.treeView)+'\' value="'+r.id()+'">'+r.name()+'</option>';
		}
		
		for(var cat in optgrp){
			
			if(this.options.treeView){
				makeTree(optgrp[cat].resources, function(item){
					optgrp[cat].$elem.append(makeView(item.resource, !item.active, item.level));
				});
			} else {
				optgrp[cat].resources.forEach(function(r){
					optgrp[cat].$elem.append(makeView(r));
				});
			}
			
		}
		
		/*if(this.options.categorise && Object.keys(optgrp).length===1){
			this.$select.children().first().children().appendTo( this.$select.empty() );
		}*/
		
		this.$select.selectpicker('refresh');
		
		if(currentValue!==null) this.value(currentValue);
		
		this.$select.closest('.bootstrap-select').find('.bs-searchbox').toggle( resources.length > 40 );
		
		var $ddmenu = this.$select.closest('.bootstrap-select').children('.dropdown-menu');
		$ddmenu.children('.bs-empty').remove();
		if(resourcesFiltered.length===0){
			$ddmenu.append('<div class="bs-empty">empty !</div>');
		}
	}
	
	ResourceSelect.prototype.value = function(value){
		if(typeof value == 'undefined'){
			
			var multiple = this.options.multiple,
				val = this.$select.val(),
				ids = multiple ? val : [val],
				resources = [];
			
			(ids || []).forEach(function(id){
				resources.push( EThing.arbo.findOneById(id) );
			}, this);
			
			return multiple ? resources : (resources[0] || null);
		}
		else {
			this.$select.selectpicker('val', toId(value));
		}
	}
	
	ResourceSelect.resourceToSelectDataContent = function(resource, noExtra){
		var extra = '';
		if(!noExtra){
			var createdBy = resource.createdBy();
			if(createdBy){
				var createdByRess = EThing.arbo.findOneById(createdBy.id);
				if(createdByRess){
					var icon;
					if(createdByRess instanceof EThing.Device)
						icon = 'phone';
					else if(createdByRess instanceof EThing.App)
						icon = 'flash';
					else
						icon = 'asterisk';
					extra += ' <span class="createdBy"><span class="glyphicon glyphicon-'+icon+'" aria-hidden="true"></span> '+createdByRess.name()+'</span>';
				}
			}
		}
		return '<span class="resource-select-item">'+($.Browser ? $.Browser.generateSvgResourceIcon(resource, false) : '')+' <span>'+resource.name()+'</span>'+extra+'</span>';
	}
	
	
	
	
	
	
	/* register as a Form plugin */
	
	Form.ResourceSelect = function(options){
		
		Form.CustomInput.call(this,$.extend({
			input: function(){
				var $input = $('<div class="f-resourceselect">').resourceSelect(options), self = this;
				
				$input.resourceSelect('change', function(){
					self.update();
				});
				
				return $input;
			},
			get: function($input){
				return toId($input.resourceSelect('value'));
			},
			set: function($input,v){
				$input.resourceSelect('value', v);
			},
			value: null
		}, options));
	}
	Form.ResourceSelect.prototype = Object.create(Form.CustomInput.prototype);
	
	Form.ResourceSelect.prototype.setValue = function(value){
		return Form.CustomInput.prototype.setValue.call(this,toId(value));
	}
	
	
	
	
	
	
	/* register as a plugin in jQuery */
	$.ResourceSelect = ResourceSelect;
	
	$.fn.resourceSelect = function(){
		var args = [].slice.call(arguments);
		
		if (this[0]) { // this[0] is the renderTo div
			
			var instance = $(this[0]).data('resourceSelect');
			
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
			instance = new ResourceSelect(this[0],args[0],args[1],args[2],args[3],args[4],args[5],args[6]);
			$(this[0]).data('resourceSelect',instance);
			
			return this;
		}
	};
	
	
	return ResourceSelect;

	
	
}));
