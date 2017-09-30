(function (global) {
	
	var EThing = global.EThing;
	
	
	
	
	/**
	 * RFLinkGateway base class constructor.
	 * @protected
	 * @class The RFLinkGateway Device resource handle
	 * @memberof EThing.Device
	 * @extends EThing.Device
	 * @param {object} json
	 */
	EThing.Device.RFLinkGateway = function(json)
	{
		EThing.Device.call(this, json);
	}
	EThing.utils.inherits(EThing.Device.RFLinkGateway, EThing.Device);
	
	/**
	 * Returns the inclusion mode state .
	 * @memberof EThing.Device.RFLinkGateway
	 * @this {EThing.Device.RFLinkGateway}
	 * @returns {boolean}
	 */
	EThing.Device.RFLinkGateway.prototype.inclusion = function() {
	  return !!this._json.inclusion;
	}
	
	
	/**
	 * Returns the version number of the firmware.
	 * @memberof EThing.Device.RFLinkGateway
	 * @this {EThing.Device.RFLinkGateway}
	 * @returns {string}
	 */
	EThing.Device.RFLinkGateway.prototype.version = function() {
	  return this._json.version;
	}
	
	/**
	 * Returns the revision number of the firmware.
	 * @memberof EThing.Device.RFLinkGateway
	 * @this {EThing.Device.RFLinkGateway}
	 * @returns {string}
	 */
	EThing.Device.RFLinkGateway.prototype.revision = function() {
	  return this._json.revision;
	}
	
	/**
	 * Returns the build number of the firmware.
	 * @memberof EThing.Device.RFLinkGateway
	 * @this {EThing.Device.RFLinkGateway}
	 * @returns {string}
	 */
	EThing.Device.RFLinkGateway.prototype.build = function() {
	  return this._json.build;
	}
	
	/**
	 * Return true if a connection to the device is opened
	 * @memberof EThing.Device.RFLinkGateway
	 * @this {EThing.Device.RFLinkGateway}
	 * @returns {boolean}
	 */
	EThing.Device.RFLinkGateway.prototype.isConnected = function() {
	  return !!this._json.connected;
	}
	
	
	/**
	 * Constructs a RFLinkSerialGateway Device instance from an object decribing a RFLinkSerialGateway device. Should not be called directly. Use instead {@link EThing.list}.
	 * @protected
	 * @class The RFLinkGateway Device resource handle
	 * @memberof EThing.Device
	 * @extends EThing.Device
	 * @param {object} json
	 */
	EThing.Device.RFLinkSerialGateway = function(json)
	{
		EThing.Device.call(this, json);
	}
	EThing.utils.inherits(EThing.Device.RFLinkSerialGateway, EThing.Device.RFLinkGateway);
	
	/**
	 * Returns the Serail port of the gateway.
	 * @memberof EThing.Device.RFLinkSerialGateway
	 * @this {EThing.Device.RFLinkSerialGateway}
	 * @returns {string}
	 */
	EThing.Device.RFLinkSerialGateway.prototype.port = function() {
	  return this._json.port;
	}
	
	/**
	 * Returns the Serail baudrate of the gateway.
	 * @memberof EThing.Device.RFLinkSerialGateway
	 * @this {EThing.Device.RFLinkSerialGateway}
	 * @returns {string}
	 */
	EThing.Device.RFLinkSerialGateway.prototype.baudrate = function() {
	  return this._json.baudrate;
	}
	
	
	
	/**
	 * RFLinkSwitch base class constructor.
	 * @protected
	 * @class The RFLinkSwitch Device resource handle
	 * @memberof EThing.Device
	 * @extends EThing.Device
	 * @param {object} json
	 */
	EThing.Device.RFLinkSwitch = function(json)
	{
		EThing.Device.call(this, json);
	}
	EThing.utils.inherits(EThing.Device.RFLinkSwitch, EThing.Device);
	
	/**
	 * Returns the protocol used to communicate with this node.
	 * @memberof EThing.Device.RFLinkSwitch
	 * @this {EThing.Device.RFLinkSwitch}
	 * @returns {string}
	 */
	EThing.Device.RFLinkSwitch.prototype.protocol = function() {
	  return this._json.protocol;
	}
	
	/**
	 * Returns the nodeId of this node.
	 * @memberof EThing.Device.RFLinkSwitch
	 * @this {EThing.Device.RFLinkSwitch}
	 * @returns {string}
	 */
	EThing.Device.RFLinkSwitch.prototype.nodeId = function() {
	  return this._json.nodeId;
	}
	
	/**
	 * Returns the switchId of this node.
	 * @memberof EThing.Device.RFLinkSwitch
	 * @this {EThing.Device.RFLinkSwitch}
	 * @returns {string}
	 */
	EThing.Device.RFLinkSwitch.prototype.switchId = function() {
	  return this._json.switchId;
	}
	
	
	/**
	 * RFLinkThermometer base class constructor.
	 * @protected
	 * @class The RFLinkThermometer Device resource handle
	 * @memberof EThing.Device
	 * @extends EThing.Device
	 * @param {object} json
	 */
	EThing.Device.RFLinkThermometer = function(json)
	{
		EThing.Device.call(this, json);
	}
	EThing.utils.inherits(EThing.Device.RFLinkThermometer, EThing.Device);
	
	/**
	 * Returns the protocol used to communicate with this node.
	 * @memberof EThing.Device.RFLinkThermometer
	 * @this {EThing.Device.RFLinkThermometer}
	 * @returns {string}
	 */
	EThing.Device.RFLinkThermometer.prototype.protocol = function() {
	  return this._json.protocol;
	}
	
	/**
	 * Returns the nodeId of this node.
	 * @memberof EThing.Device.RFLinkThermometer
	 * @this {EThing.Device.RFLinkThermometer}
	 * @returns {string}
	 */
	EThing.Device.RFLinkThermometer.prototype.nodeId = function() {
	  return this._json.nodeId;
	}
	
	
	/**
	 * RFLinkWeatherStation base class constructor.
	 * @protected
	 * @class The RFLinkWeatherStation Device resource handle
	 * @memberof EThing.Device
	 * @extends EThing.Device
	 * @param {object} json
	 */
	EThing.Device.RFLinkWeatherStation = function(json)
	{
		EThing.Device.call(this, json);
	}
	EThing.utils.inherits(EThing.Device.RFLinkWeatherStation, EThing.Device);
	
	/**
	 * Returns the protocol used to communicate with this node.
	 * @memberof EThing.Device.RFLinkWeatherStation
	 * @this {EThing.Device.RFLinkWeatherStation}
	 * @returns {string}
	 */
	EThing.Device.RFLinkWeatherStation.prototype.protocol = function() {
	  return this._json.protocol;
	}
	
	/**
	 * Returns the nodeId of this node.
	 * @memberof EThing.Device.RFLinkWeatherStation
	 * @this {EThing.Device.RFLinkWeatherStation}
	 * @returns {string}
	 */
	EThing.Device.RFLinkWeatherStation.prototype.nodeId = function() {
	  return this._json.nodeId;
	}
	
	
	/**
	 * RFLinkMultimeter base class constructor.
	 * @protected
	 * @class The RFLinkMultimeter Device resource handle
	 * @memberof EThing.Device
	 * @extends EThing.Device
	 * @param {object} json
	 */
	EThing.Device.RFLinkMultimeter = function(json)
	{
		EThing.Device.call(this, json);
	}
	EThing.utils.inherits(EThing.Device.RFLinkMultimeter, EThing.Device);
	
	/**
	 * Returns the protocol used to communicate with this node.
	 * @memberof EThing.Device.RFLinkMultimeter
	 * @this {EThing.Device.RFLinkMultimeter}
	 * @returns {string}
	 */
	EThing.Device.RFLinkMultimeter.prototype.protocol = function() {
	  return this._json.protocol;
	}
	
	/**
	 * Returns the nodeId of this node.
	 * @memberof EThing.Device.RFLinkMultimeter
	 * @this {EThing.Device.RFLinkMultimeter}
	 * @returns {string}
	 */
	EThing.Device.RFLinkMultimeter.prototype.nodeId = function() {
	  return this._json.nodeId;
	}
	
	
	/**
	 * Creates a new RFLink gateway.
	 *
	 * @method EThing.Device.RFLinkSerialGateway.create
	 * @param {object} attributes
	 * @param {function(data,XHR,options)} [callback] it is executed once the request is complete whether in failure or success
	 * @returns {Deferred} a {@link http://api.jquery.com/category/deferred-object/|jQuery like Promise object}. {@link EThing.request|More ...} 
	 * @fires EThing#ething.device.created
	 * @example
	 * EThing.Device.RFLinkSerialGateway.create({
	 *   name: "foobar",
	 *   port: "/dev/ttyS0",
	 *   baudrate: 57600,
	 * }).done(function(resource){
	 *     console.log('the new RFLink gateway has been added');
	 * })
	 */
	EThing.Device.RFLinkSerialGateway.create = function(a,callback){
		
		a.type = 'RFLinkSerialGateway';
		
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
	 * Creates a new RFLink generic switch.
	 *
	 * @method EThing.Device.RFLinkSwitch.create
	 * @param {object} attributes
	 * @param {function(data,XHR,options)} [callback] it is executed once the request is complete whether in failure or success
	 * @returns {Deferred} a {@link http://api.jquery.com/category/deferred-object/|jQuery like Promise object}. {@link EThing.request|More ...} 
	 * @fires EThing#ething.device.created
	 * @example
	 * EThing.Device.RFLinkSwitch.create({
	 *   name: "foobar",
	 *   gateway: "4ge7r81",
	 *   protocol: "NewKaku",
	 *   nodeId: "008440e6",
	 *   switchId: "a"
	 * }).done(function(resource){
	 *     console.log('the new RFLink switch has been added');
	 * })
	 */
	EThing.Device.RFLinkSwitch.create = function(a,callback){
		
		a.type = 'RFLinkSwitch';
		
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
	 * Creates a new RFLink generic thermometer.
	 *
	 * @method EThing.Device.RFLinkThermometer.create
	 * @param {object} attributes
	 * @param {function(data,XHR,options)} [callback] it is executed once the request is complete whether in failure or success
	 * @returns {Deferred} a {@link http://api.jquery.com/category/deferred-object/|jQuery like Promise object}. {@link EThing.request|More ...} 
	 * @fires EThing#ething.device.created
	 * @example
	 * EThing.Device.RFLinkThermometer.create({
	 *   name: "foobar",
	 *   gateway: "4ge7r81",
	 *   protocol: "OregonV1",
	 *   nodeId: "000A"
	 * }).done(function(resource){
	 *     console.log('the new RFLink thermometer has been added');
	 * })
	 */
	EThing.Device.RFLinkThermometer.create = function(a,callback){
		
		a.type = 'RFLinkThermometer';
		
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
	 * Creates a new RFLink generic weather station.
	 *
	 * @method EThing.Device.RFLinkWeatherStation.create
	 * @param {object} attributes
	 * @param {function(data,XHR,options)} [callback] it is executed once the request is complete whether in failure or success
	 * @returns {Deferred} a {@link http://api.jquery.com/category/deferred-object/|jQuery like Promise object}. {@link EThing.request|More ...} 
	 * @fires EThing#ething.device.created
	 * @example
	 * EThing.Device.RFLinkWeatherStation.create({
	 *   name: "foobar",
	 *   gateway: "4ge7r81",
	 *   protocol: "Oregon Wind",
	 *   nodeId: "1a89"
	 * }).done(function(resource){
	 *     console.log('the new RFLink weather station has been added');
	 * })
	 */
	EThing.Device.RFLinkWeatherStation.create = function(a,callback){
		
		a.type = 'RFLinkWeatherStation';
		
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
	 * Creates a new RFLink generic multimeter.
	 *
	 * @method EThing.Device.RFLinkMultimeter.create
	 * @param {object} attributes
	 * @param {function(data,XHR,options)} [callback] it is executed once the request is complete whether in failure or success
	 * @returns {Deferred} a {@link http://api.jquery.com/category/deferred-object/|jQuery like Promise object}. {@link EThing.request|More ...} 
	 * @fires EThing#ething.device.created
	 * @example
	 * EThing.Device.RFLinkMultimeter.create({
	 *   name: "foobar",
	 *   gateway: "4ge7r81",
	 *   protocol: "Revolt",
	 *   nodeId: "3f8a"
	 * }).done(function(resource){
	 *     console.log('the new RFLink multimeter has been added');
	 * })
	 */
	EThing.Device.RFLinkMultimeter.create = function(a,callback){
		
		a.type = 'RFLinkMultimeter';
		
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