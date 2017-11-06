(function (global) {
	
	var EThing = global.EThing;
	
	
	
	
	/**
	 * BleaGateway base class constructor.
	 * @protected
	 * @class The BleaGateway Device resource handle
	 * @memberof EThing.Device
	 * @extends EThing.Device
	 * @param {object} json
	 */
	EThing.Device.BleaGateway = function(json)
	{
		EThing.Device.call(this, json);
	}
	EThing.utils.inherits(EThing.Device.BleaGateway, EThing.Device);
	
	/**
	 * Returns the inclusion mode state .
	 * @memberof EThing.Device.BleaGateway
	 * @this {EThing.Device.BleaGateway}
	 * @returns {boolean}
	 */
	EThing.Device.BleaGateway.prototype.inclusion = function() {
	  return !!this._json.inclusion;
	}
	
	/**
	 * Return true if a connection to the device is opened
	 * @memberof EThing.Device.BleaGateway
	 * @this {EThing.Device.BleaGateway}
	 * @returns {boolean}
	 */
	EThing.Device.BleaGateway.prototype.isConnected = function() {
	  return !!this._json.connected;
	}
	
	
	/**
	 * Constructs a BleaEthernetGateway Device instance from an object decribing a BleaEthernetGateway device. Should not be called directly. Use instead {@link EThing.list}.
	 * @protected
	 * @class The BleaGateway Device resource handle
	 * @memberof EThing.Device
	 * @extends EThing.Device
	 * @param {object} json
	 */
	EThing.Device.BleaEthernetGateway = function(json)
	{
		EThing.Device.call(this, json);
	}
	EThing.utils.inherits(EThing.Device.BleaEthernetGateway, EThing.Device.BleaGateway);
	
	/**
	 * Returns the hostname of the gateway.
	 * @memberof EThing.Device.BleaEthernetGateway
	 * @this {EThing.Device.BleaEthernetGateway}
	 * @returns {string}
	 */
	EThing.Device.BleaEthernetGateway.prototype.host = function() {
	  return this._json.host;
	}
	
	/**
	 * Returns the port number of the gateway.
	 * @memberof EThing.Device.BleaEthernetGateway
	 * @this {EThing.Device.BleaEthernetGateway}
	 * @returns {number}
	 */
	EThing.Device.BleaEthernetGateway.prototype.port = function() {
	  return this._json.port;
	}
	
	
	/**
	 * Constructs a BleaLocalGateway Device instance from an object decribing a BleaLocalGateway device. Should not be called directly. Use instead {@link EThing.list}.
	 * @protected
	 * @class The BleaGateway Device resource handle
	 * @memberof EThing.Device
	 * @extends EThing.Device
	 * @param {object} json
	 */
	EThing.Device.BleaLocalGateway = function(json)
	{
		EThing.Device.call(this, json);
	}
	EThing.utils.inherits(EThing.Device.BleaLocalGateway, EThing.Device.BleaGateway);
	
	/**
	 * Returns the name of the bluetooth device. Usually hci0.
	 * @memberof EThing.Device.BleaLocalGateway
	 * @this {EThing.Device.BleaLocalGateway}
	 * @returns {string}
	 */
	EThing.Device.BleaLocalGateway.prototype.device = function() {
	  return this._json.device;
	}
	
	
	
	/**
	 * BleaDevice base class constructor.
	 * @protected
	 * @class The BleaDevice Device resource handle
	 * @memberof EThing.Device
	 * @extends EThing.Device
	 * @param {object} json
	 */
	EThing.Device.BleaDevice = function(json)
	{
		EThing.Device.call(this, json);
	}
	EThing.utils.inherits(EThing.Device.BleaDevice, EThing.Device);
	
	/**
	 * Returns the mac address of this device.
	 * @memberof EThing.Device.BleaDevice
	 * @this {EThing.Device.BleaDevice}
	 * @returns {string}
	 */
	EThing.Device.BleaDevice.prototype.mac = function() {
	  return this._json.mac;
	}
	
	/**
	 * Returns the rssi of this device.
	 * @memberof EThing.Device.BleaDevice
	 * @this {EThing.Device.BleaDevice}
	 * @returns {number}
	 */
	EThing.Device.BleaDevice.prototype.rssi = function() {
	  return this._json.rssi;
	}
	
	/**
	 * Returns the id of the last gateway that has seen this device.
	 * @memberof EThing.Device.BleaDevice
	 * @this {EThing.Device.BleaDevice}
	 * @returns {string}
	 */
	EThing.Device.BleaDevice.prototype.gateway = function() {
	  return this._json.gateway;
	}
	
	
	
	
	/**
	 * Creates a new Blea ethernet gateway.
	 *
	 * @method EThing.Device.BleaEthernetGateway.create
	 * @param {object} attributes
	 * @param {function(data,XHR,options)} [callback] it is executed once the request is complete whether in failure or success
	 * @returns {Deferred} a {@link http://api.jquery.com/category/deferred-object/|jQuery like Promise object}. {@link EThing.request|More ...} 
	 * @fires EThing#ething.device.created
	 * @example
	 * EThing.Device.BleaEthernetGateway.create({
	 *   name: "foobar",
	 *   host: "localhost",
	 *   port: 5005,
	 * }).done(function(resource){
	 *     console.log('the new Blea gateway has been added');
	 * })
	 */
	EThing.Device.BleaEthernetGateway.create = function(a,callback){
		
		a.type = 'BleaEthernetGateway';
		
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
	 * Creates a new Blea local gateway.
	 *
	 * @method EThing.Device.BleaLocalGateway.create
	 * @param {object} attributes
	 * @param {function(data,XHR,options)} [callback] it is executed once the request is complete whether in failure or success
	 * @returns {Deferred} a {@link http://api.jquery.com/category/deferred-object/|jQuery like Promise object}. {@link EThing.request|More ...} 
	 * @fires EThing#ething.device.created
	 * @example
	 * EThing.Device.BleaLocalGateway.create({
	 *   name: "foobar",
	 *   device: "hci0"
	 * }).done(function(resource){
	 *     console.log('the new Blea gateway has been added');
	 * })
	 */
	EThing.Device.BleaLocalGateway.create = function(a,callback){
		
		a.type = 'BleaLocalGateway';
		
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
	 * Miflora base class constructor.
	 * @protected
	 * @class The Miflora Device resource handle
	 * @memberof EThing.Device
	 * @extends EThing.Device
	 * @param {object} json
	 */
	EThing.Device.Miflora = function(json)
	{
		EThing.BleaDevice.call(this, json);
	}
	EThing.utils.inherits(EThing.Device.Miflora, EThing.Device.BleaDevice);
	
	
	
	
})(this);