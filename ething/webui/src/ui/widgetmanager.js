(function (root, factory) {
    if (typeof define === 'function' && define.amd) {
        // AMD. Register as an anonymous module.
        define(['require', 'jquery', 'ui/meta', 'json!widget/generic/list.json', 'json!widget/resource/list.json'], factory);
    }
}(this, function (require, $, Meta, generic_list, resource_list) {
	
	
	
	var _generic_factories = [];
	var _resource_factories = [];
	
	
	
	function GenericFactory(name, factory){
		
		var self = {
			name: name,
			title: name,
			description: '',
			require: []
		};
		
		
		if(typeof factory === 'function'){
			factory = {
				instanciate: factory
			};
		}
		
		if(factory.title)
			self.title = factory.title;
		if(factory.description)
			self.description = factory.description;
		if(factory.require)
			self.require = factory.require;
		
		
		self.instanciate = function(options){
			return factory.instanciate.apply(factory, options);
		};
		
		if(factory.factory){
			self.configure = function(container, preset){
				var res = factory.factory.apply(factory, arguments);
				
				if(typeof res === 'function') return res;
				else return function(){return res;};
			};
		};
		
		return self;
	}
	
	
	function ResourceFactory(name, factory){
		
		var self = {
			name: name,
			title: name,
			description: ''
		};
		
		
		if(typeof factory === 'function'){
			factory = {
				instanciate: factory
			};
		}
		
		if(factory.title)
			self.title = factory.title;
		if(factory.description)
			self.description = factory.description;
		
		
		self.instanciate = function(resource){
			return factory.instanciate.call(factory, resource);
		};
		
		return self;
	}
	
	
	function ResourceFactoryProxy(resource, factory){
		
		return $.extend({}, factory, {
			resource: resource,
			
			instanciate: function(){
				return factory.instanciate.call(this, this.resource);
			}
		});
		
	}
	
	
	var WidgetManager = {
		
		load: function (callback){
			
			_generic_factories = [];
			_resource_factories = [];
			
			var generic_dfr = $.Deferred();
			var resource_dfr = $.Deferred();
			
			require(generic_list.map(function(cls){return 'widget/generic/'+cls;}), function(){
				for(var i=0; i<arguments.length; i++){
					_generic_factories.push(GenericFactory(generic_list[i], arguments[i]));
				}
				
				console.log('Generic widgets loaded: ' + generic_list.join(' '));
				
				generic_dfr.resolve();
			});
			
			require(resource_list.map(function(cls){return 'widget/resource/'+cls;}), function(){
				for(var i=0; i<arguments.length; i++){
					_resource_factories.push(ResourceFactory(resource_list[i], arguments[i]));
				}
				
				console.log('Resource widgets loaded: ' + resource_list.join(' '));
				
				resource_dfr.resolve();
			});
			
			return $.when(generic_dfr, resource_dfr).done(function(){
				if(typeof callback === 'function')
					callback.call(WidgetManager);
			});
			
		},
	
		generic: function(name){
			
			if(name){
				for(var i in _generic_factories){
					if(_generic_factories[i].name === name)
						return _generic_factories[i];
				}
				return;
			}
			
			return _generic_factories;
		},
		
		resource: function(resource){
			
			var metaWidget = Meta.get(resource, 'widget')(), factory = null;
			
			if(typeof metaWidget == 'string'){
				
				for(var i in _resource_factories){
					if(_resource_factories[i].name === metaWidget){
						factory = _resource_factories[i];
						break
					}
				}
				
			} else if(typeof metaWidget == 'function'){
				factory = metaWidget;
			}
			
			if(factory){
				return ResourceFactoryProxy(resource, factory);
			}
			
		}
		
	};
	
	
	
	return WidgetManager;
	

}));
