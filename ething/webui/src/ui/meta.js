(function (root, factory) {
	
    if (typeof define === 'function' && define.amd) {
        // AMD. Register as an anonymous module.
        define(['require', 'jquery', 'ething', 'json!meta/list.json'], factory);
    }
}(this, function (require, $, EThing, meta_classes) {
	
	var Meta = {};
	
	Meta.reg = {};
	
	var propertiesList = [];
	
	function loadMeta(callback){
		Meta.reg = {};
		
		require(meta_classes.map(function(cls){return 'meta/'+cls;}), function(){
			for(var i=0; i<arguments.length; i++){
				Meta.reg[meta_classes[i]] = arguments[i];
			}
			
			propertiesList = Object.keys(get(Object.keys(Meta.reg), ['properties']));
			
			console.log('Meta loaded: ' + meta_classes.join(' '));
			
			if(typeof callback === 'function')
				callback.call(Meta);
		});
		
	}
	
	function merge(a, b, keys, propertiesKeys){
		for(var i in b){
			if (keys){
				if(typeof keys === 'function'){
					if(!keys(i)) continue;
				} else {
					if(keys.indexOf(i)===-1) continue;
				}
			}
			
			if(typeof b[i] === 'object' && b[i] !== null){
				
				if(!a.hasOwnProperty(i) || typeof a[i] !== 'object' || a[i] === null){
					a[i] = {};
				}
				
				merge(a[i], b[i], i=='properties' ? propertiesKeys : null);
				
			} else {
				if(!a.hasOwnProperty(i))
					a[i] = b[i];
			}
			
		}
	}
	
	
	function compile(classes, keys, propertiesKeys){
		if(!Array.isArray(classes))
			classes = [classes]
		else
			classes = [].concat(classes) // copy
		
		var obj = {}, cls, obji, processed = [], mro = [];
		
		for(var i=0; i<classes.length; i++){
			
			cls = classes[i]
			
			if(processed.indexOf(cls) !== -1) continue;
			
			if(Meta.reg.hasOwnProperty(cls)){
				
				mro.push(cls);
				
				obji = Meta.reg[cls]
				
				merge(obj, obji, keys, propertiesKeys)
				
				if(obji.bases){
					var j=0;
					obji.bases.forEach(function(b){
						if(classes.indexOf(b)===-1){
							classes.splice(i+1+j, 0, b);
							j++;
						}
					});
					//[].splice.apply(classes, [i+1, 0].concat(obji.bases))
				}
				
			}/* else {
				console.warn('the class '+cls+' is not found!')
			}*/
			
			processed.push(cls);
		}
		
		merge(obj, {
			icon: null,
			bases: [],
			properties: {},
			widget: null,
			creatable: true,
			description: '',
			path: null,
			name: classes.length ? classes[0] : null,
			dep: mro
		}, keys, propertiesKeys)
		
		if(obj.properties){
			$.each(obj.properties, function(name, property){
				merge(property, {
					label:name,
					get:function(resource){
						var value = undefined;
						var accessor = resource[name];
						if(typeof accessor !== "undefined"){
							value = (typeof accessor == 'function') ? accessor.call(resource) : accessor;
						} else {
							if(resource.hasAttr(name)){
								value = resource.attr(name);
							}
						}
						return value;
					},
					editable:null,
					default: undefined,
					isOptional: false,
					category: null,
					formatter: function(v){
						return v;
					},
					description: '',
					value: function(){
						if(this.resource){
							var value = this.get(this.resource);
							if(value === undefined){
								value = this.default();
							}
							return value;
						}
					},
					formattedValue: function(){
						return this.formatter(this.value());
					}
				})
			})
		}
		
		return obj
	}
	
	function issubclass(cls, base){
		
		if(cls instanceof EThing.Resource)
			cls = cls.type()
		
		if(base instanceof EThing.Resource)
			base = base.type()
		
		if(Meta.reg.hasOwnProperty(cls)){
			var bases = Meta.reg[cls].bases || [];
			
			for(var i in bases){
				if(base === bases[i] || issubclass(bases[i], base)){
					return true;
				}
			}
			
		}
		
		return false;
	}
	
	function call(attr, self, args){
		if(typeof attr === 'function')
			return Array.isArray(args) ? attr.apply(self, args) : attr.call(self, args);
		else
			return attr
	}
	
	function createContext(resourceOrClasses){
		var context = {
			meta: Meta,
			resource: null,
			types: [],
			type: null
		};
		
		if(resourceOrClasses instanceof EThing.Resource){
			context.resource = resourceOrClasses;
			context.types = [].concat(resourceOrClasses.types());
			
			if(resourceOrClasses instanceof EThing.Device){
				var base = context.types.pop();
				context.types = context.types.concat(resourceOrClasses.interfaces(), base);
				//context.types = [].concat(resourceOrClasses.interfaces(), context.types);
			}
		} else if(resourceOrClasses) {
			context.types = resourceOrClasses;
		}
		
		if(context.types.length)
			context.type = context.types[0];
		
		return context;
	}
	
	function contextify(obj, context){
		
		for(var i in obj){
			value = obj[i];
			if (typeof value === 'function'){
				obj[i] = $.proxy(value, context);
			} else if(i == 'properties') {
				
				$.each(value, function(name, value){
					contextify(value, $.extend({
						parent: obj,
						name: name
					}, context));
				});
				
			} else {
				obj[i] = (function(value){
					return function(){
						return value;
					};
				})(value);
			}
		}
		
		$.extend(context, obj)
		
		return obj;
	}
	
	function get(resourceOrClasses, keys, propertiesKeys){
		var context = createContext(resourceOrClasses);
		var returnOne = false;
		
		if(typeof keys == 'string'){
			returnOne = keys;
			keys = [keys];
		}
		
		var obj = compile(context.types, keys, propertiesKeys);
		
		contextify(obj, context);
		
		return returnOne ? obj[returnOne] : obj;
	}
	
	function getResourceProperties(resourceOrClasses, keys){
		return get(resourceOrClasses, ['properties'], keys).properties;
	}
	
	function getResourceForm(resourceOrClasses, keys){
		
		var dfrs = [];
		
		$.each(getResourceProperties(resourceOrClasses, keys), function(name, property) {
			
			var formItemDfr = property.editable() || null;
			
			dfrs.push(
				$.when(formItemDfr).then(function(formItem){
					if(formItem instanceof $.Form.Item){
						formItem.name = name;
						
						var value = undefined, hasValue = false;
						
						if(resourceOrClasses instanceof EThing.Resource){
							value = property.value(resourceOrClasses);
							if(value !== undefined && value!==null){
								console.log(name,value)
								hasValue = true;
								formItem.value(value);
							}
						}
						
						return {
							label: property.label(),
							name: name,
							checkable: !!property.isOptional(),
							checked: hasValue,
							item: formItem,
							description: property.description()
						};
						
					}
				})
			);
			
		});
		
		return $.when.apply($, dfrs).then(function(){
			
			var formItems = dfrs.length===1 ? [arguments[0]] : Array.prototype.slice.call(arguments);
			var out = [];
			formItems.forEach(function(formItem){
				if(formItem) out.push(formItem);
			})
			
			return out;
		});
	}
	
	
	return $.extend(Meta, {
		load: loadMeta,
		get: get,
		getResourceProperties: getResourceProperties,
		getResourceForm: getResourceForm,
		propertiesList: propertiesList,
		issubclass: issubclass
	});
	
	
}))