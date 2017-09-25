(function (root, factory) {
    if (typeof define === 'function' && define.amd) {
        // AMD. Register as an anonymous module.
        define(['jquery', 'ething', 'json!widget/devices/map.json'], factory);
    }
}(this, function ($, EThing, DevMap) {
	
	
	var WidgetCollection = (function(){
		
		var cachedWidgetPluginObject = {};
		
		var map = DevMap;
		
		return {
			
			types: {
				'device' : 'device',
				'generic': {
					'chart': 'generic/chart',
					'gauge': 'generic/gauge',
					'label': 'generic/label',
					'image': 'generic/image',
					'button': 'generic/button',
					'stream': 'generic/stream',
					'video': 'generic/video',
					'slider': 'generic/slider'
				},
				'miscellaneous': {
					'clock': 'miscellaneous/clock'
				}
			},
			
			load: function(name){
				var dfr = $.Deferred();
				
				if(cachedWidgetPluginObject.hasOwnProperty(name)){
					$
						.when(cachedWidgetPluginObject[name])
						.done(function(plugin){
							dfr.resolve(plugin);
						})
						.fail(function(e){
							dfr.reject(e);
						});
				}
				else {
					// load the widget async
					cachedWidgetPluginObject[name] = dfr;
					require(['widget/'+name], function(plugin){
						
						if(!$.isPlainObject(plugin)){
							dfr.reject('invalid widget plugin "'+name+'"');
							return;
						}
						
						$.extend(true,plugin,{
							type: name
						});
						
						cachedWidgetPluginObject[name] = plugin;
						dfr.resolve(plugin);
						
					}, function(){
						dfr.reject('widget plugin "'+name+'" not found');
					});
				}
				
				return dfr.promise().fail(function(err){
					console.error(err);
				});
			},
			
			getWidgetNameFromDevice: function(device){
				
				var widgetName = null;
				
				if(typeof device == 'string') device = EThing.arbo.findOneById(device);
				
				DevMap.forEach(function(el){
					
					var pass = true;
					
					Object.keys(el).filter(function(k){
						return k!=='widget';
					}).forEach(function(k){
						if(!(typeof device[k] === 'function' && device[k]()===el[k])){
							pass = false;
							return false;
						}
					});
					
					if(pass){
						widgetName = el.widget;
						return false;
					}
					
				});
				
				return widgetName ? 'devices/'+widgetName : null;
			},
			
			loadFromDevice: function(device){
				
				var widgetName = this.getWidgetNameFromDevice(device);
				
				if(widgetName){
					return this.load(widgetName);
				} else {
					return $.Deferred().reject('no widget found for device type '+device.type()).promise();
				}
				
				
			},
			
			instanciate: function(name, options, device){
				
				var dfr = name ? this.load(name) : $.Deferred().reject('no widget found for device type '+device.type()).promise();
				
				return dfr.then(function(plugin){
					
					var dfr = $.Deferred();
					var args = [options || {}];
					
					if(device)
						args.unshift(device);
					
					// load the dependencies ...
					if(Array.isArray(plugin.require) && plugin.require.length){
						require(plugin.require, function(){
							args = args.concat(Array.prototype.slice.call(arguments));
							try {
								var widget = plugin.instanciate.apply(plugin, args);
							} catch(err){
								dfr.reject(err);
								return;
							}
							$.when(widget).done(function(widget){
								dfr.resolve(widget, name);
							}).fail(function(err){
								dfr.reject(err);
							});
						}, function(){
							dfr.reject('dependency error');
						});
					} else {
						// no dependencies
						try {
							var widget = plugin.instanciate.apply(plugin, args);
						} catch(err){
							dfr.reject(err);
							return;
						}
						$.when(widget).done(function(widget){
							dfr.resolve(widget, name);
						}).fail(function(err){
							dfr.reject(err);
						});
					}
					
					return dfr;
					
				});
				
			},
			
			instanciateDeviceWidget: function(device, options) {
				var self = this;
				var widgetName = this.getWidgetNameFromDevice(device);
				
				return self.instanciate(widgetName, options, device);
				
			}
			
		};
		
	})();
	
	
	
	return WidgetCollection;
	

}));
