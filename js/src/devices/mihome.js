(function (global) {
	
	var EThing = global.EThing;
	
	
	
	
	/**
	 * MihomeGateway base class constructor.
	 * @protected
	 * @class The MihomeGateway Device resource handle
	 * @memberof EThing.Device
	 * @extends EThing.Device
	 * @param {object} json
	 */
	EThing.Device.MihomeGateway = function(json)
	{
		EThing.Device.call(this, json);
	}
	EThing.utils.inherits(EThing.Device.MihomeGateway, EThing.Device);
	
	/**
	 * Returns the IP address of the gateway.
	 * @memberof EThing.Device.MihomeGateway
	 * @this {EThing.Device.MihomeGateway}
	 * @returns {string}
	 */
	EThing.Device.MihomeGateway.prototype.ip = function() {
	  return this._json.ip;
	}
	
	/**
	 * Returns the port number of the gateway.
	 * @memberof EThing.Device.MihomeGateway
	 * @this {EThing.Device.MihomeGateway}
	 * @returns {number}
	 */
	EThing.Device.MihomeGateway.prototype.port = function() {
	  return this._json.port;
	}
	
	/**
	 * Returns the uniq sid of the gateway.
	 * @memberof EThing.Device.MihomeGateway
	 * @this {EThing.Device.MihomeGateway}
	 * @returns {string}
	 */
	EThing.Device.MihomeGateway.prototype.sid = function() {
	  return this._json.sid;
	}
	
	/**
	 * Returns the password of the gateway.
	 * @memberof EThing.Device.MihomeGateway
	 * @this {EThing.Device.MihomeGateway}
	 * @returns {string}
	 */
	EThing.Device.MihomeGateway.prototype.password = function() {
	  return this._json.password;
	}
	
	/**
	 * Return true if a connection to the device is opened
	 * @memberof EThing.Device.MihomeGateway
	 * @this {EThing.Device.MihomeGateway}
	 * @returns {boolean}
	 */
	EThing.Device.MihomeGateway.prototype.isConnected = function() {
	  return !!this._json.connected;
	}
	
	
	
	/**
	 * MihomeDevice base class constructor.
	 * @protected
	 * @class The MihomeDevice Device resource handle
	 * @memberof EThing.Device
	 * @extends EThing.Device
	 * @param {object} json
	 */
	EThing.Device.MihomeDevice = function(json)
	{
		EThing.Device.call(this, json);
	}
	EThing.utils.inherits(EThing.Device.MihomeDevice, EThing.Device);
	
	/**
	 * Returns the uniq sid of the gateway.
	 * @memberof EThing.Device.MihomeDevice
	 * @this {EThing.Device.MihomeDevice}
	 * @returns {string}
	 */
	EThing.Device.MihomeDevice.prototype.sid = function() {
	  return this._json.sid;
	}
	
	/**
	 * Return true if a connection to the device is opened
	 * @memberof EThing.Device.MihomeDevice
	 * @this {EThing.Device.MihomeDevice}
	 * @returns {boolean}
	 */
	EThing.Device.MihomeDevice.prototype.isConnected = function() {
	  return !!this._json.connected;
	}
	
	
	
	
	/**
	 * Creates a new Mihome ethernet gateway.
	 *
	 * @method EThing.Device.MihomeGateway.create
	 * @param {object} attributes
	 * @param {function(data,XHR,options)} [callback] it is executed once the request is complete whether in failure or success
	 * @returns {Deferred} a {@link http://api.jquery.com/category/deferred-object/|jQuery like Promise object}. {@link EThing.request|More ...} 
	 * @fires EThing#ething.device.created
	 * @example
	 * EThing.Device.MihomeGateway.create({
	 *   name: "foobar",
	 *   ip: "192.168.1.25",
	 *   sid: "286c078XXXXX",
	 *   password: "passhere"
	 * }).done(function(resource){
	 *     console.log('the new Mihome gateway has been added');
	 * })
	 */
	EThing.Device.MihomeGateway.create = function(a,callback){
		
		a.type = 'MihomeGateway';
		
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
	
	
	
	
	
	/**
	 * Mihome temperatire/humidity[/pressure] Sensor class constructor.
	 * @protected
	 * @class The Misensor Device resource handle
	 * @memberof EThing.Device
	 * @extends EThing.Device
	 * @param {object} json
	 */
	EThing.Device.MihomeSensorHT = function(json)
	{
		EThing.Device.MihomeDevice.call(this, json);
	}
	EThing.utils.inherits(EThing.Device.MihomeSensorHT, EThing.Device.MihomeDevice);
	
	
	
	
})(this);