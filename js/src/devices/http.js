(function (global) {
	
	var EThing = global.EThing;
	
	
	/**
	 * Constructs a Http Device instance from an object decribing a http device. Should not be called directly. Use instead {@link EThing.list}.
	 * @protected
	 * @class The Http Device resource handle
	 * @memberof EThing.Device
	 * @extends EThing.Device
	 * @param {object} json
	 */
	EThing.Device.Http = function(json)
	{
		EThing.Device.call(this, json);
	}
	EThing.utils.inherits(EThing.Device.Http, EThing.Device);
	
	
	/**
	 * 
	 * @memberof EThing.Device.Http
	 * @this {EThing.Device.Http}
	 * @returns {string}
	 */
	EThing.Device.Http.prototype.url = function() {
	  return this._json.url;
	}
	
	/**
	 * 
	 * @memberof EThing.Device.Http
	 * @this {EThing.Device.Http}
	 * @returns {object|null}
	 */
	EThing.Device.Http.prototype.auth = function() {
	  return this._json.auth;
	}
	
	/**
	 * Return the scope of this device.
	 * @memberof EThing.Device.Http
	 * @this {EThing.Device.Http}
	 * @returns {string}
	 */
	EThing.Device.Http.prototype.scope = function() {
	  return (typeof this._json.scope == 'string') ? this._json.scope : '';
	}
	
	/**
	 * Return false if the device is not reachable.
	 * @memberof EThing.Device.Http
	 * @this {EThing.Device.Http}
	 * @returns {boolean}
	 */
	EThing.Device.Http.prototype.isReachable = function() {
	  return !!this._json.reachable;
	}
	
	/**
	 * Make a HTTP request on this device. __Only available if an URL is set__, see {@link EThing.Device#create}
	 * The options are the same as the ones used in {@link EThing.request}.
	 * @memberof EThing.Device.Http
	 * @this {EThing.Device.Http}
	 * @param {string|object} options or an URL
	 * @returns {EThing.Device.Http} The instance on which this method was called.
	 * @example
	 * // simple GET request
	 * device.request('/foo').done(function(data){
     *   // success, handle the data here
     * });
	 *
	 * // POST request
	 * device.request({
	 *   url: '/bar',
	 *   method: 'POST',
	 *   data: 'some content here ...',
	 *   contentType: 'text/plain'
	 * })
	 * .done(function(data){
	 *   // success, handle the data here
	 * })
	 * .fail(function(error){
	 *   console.log("an error occurs : "+error.message);
	 * });
	 */
	EThing.Device.Http.prototype.request = function(settings){
		var args = [].slice.call(arguments);
		return this.deferred(function(){
			args.unshift(this);
			return EThing.Device.Http.request.apply(EThing, args);
		});
	}
	EThing.Device.Http.prototype.ajax = EThing.Device.Http.prototype.request;
	
	
	EThing.Device.Http.prototype.getResourceUrl = function(url,auth){
		return EThing.Device.Http.getResourceUrl(this,url,auth);
	}
	
	
	
	
	/**
	 * Set the swagger API specification of this device.
	 * @memberof EThing.Device.Http
	 * @this {EThing.Device.Http}
	 * @param {String|Object} [spec] the swagger API specification.
	 * @param {function(data,XHR,options)} [callback] it is executed once the request is complete whether in failure or success
	 * @returns {EThing.Device.Http} The instance on which this method was called.
	 */
	EThing.Device.Http.prototype.setSpecification = function(spec,callback) {
	  if(typeof spec == 'string')
		spec = JSON.parse(spec);
	  return this.set({
		specification: spec
	  },callback);
	}

	/**
	 * Get the swagger API specification of this device.
	 * @memberof EThing.Device.Http
	 * @this {EThing.Device.Http}
	 * @param {function(data,XHR,options)} [callback] it is executed once the request is complete whether in failure or success
	 * @returns {EThing.Device.Http} The instance on which this method was called.
	 */
	EThing.Device.Http.prototype.getSpecification = function(callback) {
	  return EThing.Device.Http.getSpecification(this, callback);
	}




	
	
	/**
	 * Creates a new HttpDevice
	 *
	 * @method EThing.Device.Http.create
	 * @param {object} attributes
	 * @param {function(data,XHR,options)} [callback] it is executed once the request is complete whether in failure or success
	 * @returns {Deferred} a {@link http://api.jquery.com/category/deferred-object/|jQuery like Promise object}. {@link EThing.request|More ...} 
	 * @fires EThing#ething.device.created
	 * @example
	 * EThing.Device.Http.create({
	 *   name: "foobar",
	 *   url: "123.45.67.89"
	 * }).done(function(resource){
	 *     console.log('the new device can be accessed through : ' + resource.url());
	 * })
	 */
	EThing.Device.Http.create = function(a,callback){
		
		a.type = 'Http';
		
		return EThing.request({
			'url': '/devices',
			'dataType': 'json',
			'method': 'POST',
			'contentType': "application/json; charset=utf-8",
			'data': a,
			'converter': EThing.resourceConverter
		},callback).done(function(r){
			EThing.trigger('ething.device.created',[r]);
		});
		
	};
	
	
	EThing.Device.Http.getResourceUrl = function(device,url,auth){
		if(device instanceof EThing.Device.Http){
			device = device.id();
		}
		
		var o = 'devices/' + device + '/request';
		if( typeof url == 'string'){
			if(!/^\//.test(url))
				url = '/'+url;
			o += url;
		}
		return EThing.toApiUrl(o,auth);
	}
	
	
	/*
	device[, settings ]
	*/
	EThing.Device.Http.ajax = EThing.Device.Http.request = function(a,b){
		
		var devId, context;
		
		if(a instanceof EThing.Device.Http){
			context = a;
			devId = a.id();
		}
		else if(isResourceId(a))
			devId = a;
		else {
			throw "First argument must be a Device object or a Device id !";
			return;
		}
		
		var settings = {
			'url': null,
			'context': context
		};
		
		if(typeof b == 'string')
			settings['url'] =  b;
		else
			extend(settings,b);
		
		settings['url'] = EThing.Device.Http.getResourceUrl(devId, settings['url']);
			
		return EThing.request(settings);
		
	};
	
	
	EThing.Device.Http.getSpecification = function(dev, callback){
		var context;
		
		if(dev instanceof EThing.Device.Http){
			context = dev;
			dev = dev.id();
		}
		else if(!EThing.utils.isId(dev))
			throw "First argument must be a Device object or a Device id !";
		
		return EThing.request({
			'url': '/devices/' + dev + '/specification',
			'dataType': 'json',
			'context': context,
			'converter': function(spec){
				if(context instanceof EThing.Device.Http){
					// attach this specification to the device
					context.swaggerSpecification = spec;
				}
				return spec;
			}
		},callback);
		
	};


	
	
})(this);