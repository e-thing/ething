(function (global) {
	
	var EThing = global.EThing;
	
	
	
	
	/**
	 * Constructs a SSH Device instance from an object decribing a SSH device. Should not be called directly. Use instead {@link EThing.list}.
	 * @protected
	 * @class The SSH Device resource handle
	 * @memberof EThing.Device
	 * @extends EThing.Device
	 * @param {object} json
	 */
	EThing.Device.SSH = function(json)
	{
		EThing.Device.call(this, json);
	}
	EThing.utils.inherits(EThing.Device.SSH, EThing.Device);
	
	
	/**
	 * 
	 * @memberof EThing.Device.SSH
	 * @this {EThing.Device.SSH}
	 * @returns {string}
	 */
	EThing.Device.SSH.prototype.host = function() {
	  return this._json.host;
	}
	
	/**
	 * 
	 * @memberof EThing.Device.SSH
	 * @this {EThing.Device.SSH}
	 * @returns {number}
	 */
	EThing.Device.SSH.prototype.port = function() {
	  return this._json.port;
	}
	
	/**
	 * 
	 * @memberof EThing.Device.SSH
	 * @this {EThing.Device.SSH}
	 * @returns {object}
	 */
	EThing.Device.SSH.prototype.auth = function() {
	  return this._json.auth || null;
	}
	
	/**
	 * Return false if the device is not reachable.
	 * @memberof EThing.Device.SSH
	 * @this {EThing.Device.SSH}
	 * @returns {boolean}
	 */
	EThing.Device.SSH.prototype.isReachable = function() {
	  return !!this._json.reachable;
	}
	
	

	
	/**
	 * Creates a new SSH device
	 *
	 * @method EThing.Device.SSH.create
	 * @param {object} attributes
	 * @param {function(data,XHR,options)} [callback] it is executed once the request is complete whether in failure or success
	 * @returns {Deferred} a {@link http://api.jquery.com/category/deferred-object/|jQuery like Promise object}. {@link EThing.request|More ...} 
	 * @fires EThing#ething.device.created
	 * @example
	 * EThing.Device.SSH.create({
	 *   host: "localhost",
	 *   auth: {
	 *     user: "foo",
	 *     password: "bar"
	 *   }
	 * }).done(function(resource){
	 *     console.log('the new SSH device has been created');
	 * })
	 */
	EThing.Device.SSH.create = function(a,callback){
		
		a.type = 'SSH';
		
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
	
	
	
})(this);