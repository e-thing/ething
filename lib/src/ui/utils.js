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
