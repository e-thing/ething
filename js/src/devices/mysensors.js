(function (global) {
	
	var EThing = global.EThing;
	
	
	
	/**
	 * MySensorsGateway base class constructor.
	 * @protected
	 * @class The MySensorsGateway Device resource handle
	 * @memberof EThing.Device
	 * @extends EThing.Device
	 * @param {object} json
	 */
	EThing.Device.MySensorsGateway = function(json)
	{
		EThing.Device.call(this, json);
	}
	EThing.utils.inherits(EThing.Device.MySensorsGateway, EThing.Device);
	
	
	/**
	 * 
	 * @memberof EThing.Device.MySensorsGateway
	 * @this {EThing.Device.MySensorsGateway}
	 * @returns {boolean}
	 */
	EThing.Device.MySensorsGateway.prototype.isMetric = function() {
	  return this._json.isMetric;
	}
	
	/**
	 * 
	 * @memberof EThing.Device.MySensorsGateway
	 * @this {EThing.Device.MySensorsGateway}
	 * @returns {string}
	 */
	EThing.Device.MySensorsGateway.prototype.libVersion = function() {
	  return this._json.libVersion;
	}
	
	/**
	 * Return true if a connection to the device is opened
	 * @memberof EThing.Device.MySensorsGateway
	 * @this {EThing.Device.MySensorsGateway}
	 * @returns {boolean}
	 */
	EThing.Device.MySensorsGateway.prototype.isConnected = function() {
	  return !!this._json.connected;
	}
	
	
	/**
	 * Constructs a MySensorsEthernetGateway Device instance from an object decribing a MySensorsEthernetGateway device. Should not be called directly. Use instead {@link EThing.list}.
	 * @protected
	 * @class The MySensorsEthernetGateway Device resource handle
	 * @memberof EThing.Device
	 * @extends EThing.Device
	 * @param {object} json
	 */
	EThing.Device.MySensorsEthernetGateway = function(json)
	{
		EThing.Device.call(this, json);
	}
	EThing.utils.inherits(EThing.Device.MySensorsEthernetGateway, EThing.Device.MySensorsGateway);
	
	/**
	 * Returns the IP address of the gateway.
	 * @memberof EThing.Device.MySensorsEthernetGateway
	 * @this {EThing.Device.MySensorsEthernetGateway}
	 * @returns {string}
	 */
	EThing.Device.MySensorsEthernetGateway.prototype.address = function() {
	  return this._json.address;
	}
	
	/**
	 * Constructs a MySensorsSerialGateway Device instance from an object decribing a MySensorsSerialGateway device. Should not be called directly. Use instead {@link EThing.list}.
	 * @protected
	 * @class The MySensorsGateway Device resource handle
	 * @memberof EThing.Device
	 * @extends EThing.Device
	 * @param {object} json
	 */
	EThing.Device.MySensorsSerialGateway = function(json)
	{
		EThing.Device.call(this, json);
	}
	EThing.utils.inherits(EThing.Device.MySensorsSerialGateway, EThing.Device.MySensorsGateway);
	
	/**
	 * Returns the Serail port of the gateway.
	 * @memberof EThing.Device.MySensorsSerialGateway
	 * @this {EThing.Device.MySensorsSerialGateway}
	 * @returns {string}
	 */
	EThing.Device.MySensorsSerialGateway.prototype.port = function() {
	  return this._json.port;
	}
	
	/**
	 * Returns the Serail baudrate of the gateway.
	 * @memberof EThing.Device.MySensorsSerialGateway
	 * @this {EThing.Device.MySensorsSerialGateway}
	 * @returns {string}
	 */
	EThing.Device.MySensorsSerialGateway.prototype.baudrate = function() {
	  return this._json.baudrate;
	}
	
	
	
	
	/**
	 * Constructs a MySensorsNode Device instance from an object decribing a MySensorsNode device. Should not be called directly. Use instead {@link EThing.list}.
	 * @protected
	 * @class The MySensorsNode Device resource handle
	 * @memberof EThing.Device
	 * @extends EThing.Device
	 * @param {object} json
	 */
	EThing.Device.MySensorsNode = function(json)
	{
		EThing.Device.call(this, json);
	}
	EThing.utils.inherits(EThing.Device.MySensorsNode, EThing.Device);
	
	/**
	 * 
	 * @memberof EThing.Device.MySensorsNode
	 * @this {EThing.Device.MySensorsNode}
	 * @returns {string}
	 */
	EThing.Device.MySensorsNode.prototype.nodeId = function() {
	  return this._json.nodeId;
	}
	
	/**
	 * 
	 * @memberof EThing.Device.MySensorsNode
	 * @this {EThing.Device.MySensorsNode}
	 * @returns {string}
	 */
	EThing.Device.MySensorsNode.prototype.sketchName = function() {
	  return this._json.sketchName;
	}
	
	/**
	 * 
	 * @memberof EThing.Device.MySensorsNode
	 * @this {EThing.Device.MySensorsNode}
	 * @returns {string}
	 */
	EThing.Device.MySensorsNode.prototype.sketchVersion = function() {
	  return this._json.sketchVersion;
	}
	
	/**
	 * 
	 * @memberof EThing.Device.MySensorsNode
	 * @this {EThing.Device.MySensorsNode}
	 * @returns {string}
	 */
	EThing.Device.MySensorsNode.prototype.smartSleep = function() {
	  return this._json.smartSleep;
	}
	
	
	
	
	
	/**
	 * Constructs a MySensorsSensor Device instance from an object decribing a MySensorsSensor device. Should not be called directly. Use instead {@link EThing.list}.
	 * @protected
	 * @class The MySensorsSensor Device resource handle
	 * @memberof EThing.Device
	 * @extends EThing.Device
	 * @param {object} json
	 */
	EThing.Device.MySensorsSensor = function(json)
	{
		EThing.Device.call(this, json);
	}
	EThing.utils.inherits(EThing.Device.MySensorsSensor, EThing.Device);
	
	/**
	 * 
	 * @memberof EThing.Device.MySensorsSensor
	 * @this {EThing.Device.MySensorsSensor}
	 * @returns {string}
	 */
	EThing.Device.MySensorsSensor.prototype.sensorId = function() {
	  return this._json.sensorId;
	}
	
	/**
	 * 
	 * @memberof EThing.Device.MySensorsSensor
	 * @this {EThing.Device.MySensorsSensor}
	 * @returns {string}
	 */
	EThing.Device.MySensorsSensor.prototype.sensorType = function() {
	  return this._json.sensorType;
	}
	
	/**
	 * 
	 * @memberof EThing.Device.MySensorsSensor
	 * @this {EThing.Device.MySensorsSensor}
	 * @returns {string}
	 */
	EThing.Device.MySensorsSensor.prototype.val = function(valueType) {
	  return this._json.data.hasOwnProperty(valueType) ? this._json.data[valueType] : null;
	}
	
	
	/**
	 * 
	 * @memberof EThing.Device.MySensorsSensor
	 * @this {EThing.Device.MySensorsSensor}
	 * @returns {string}
	 */
	EThing.Device.MySensorsSensor.prototype.setValue = function(valueType, value, callback) {
		var data = {};
		data[valueType] = value;
		return this.setData(data,callback);
	}
	
	
	
	
	
	/**
	 * Creates a new MySensors gateway.
	 *
	 * @method EThing.Device.MySensorsEthernetGateway.create
	 * @param {object} attributes
	 * @param {function(data,XHR,options)} [callback] it is executed once the request is complete whether in failure or success
	 * @returns {Deferred} a {@link http://api.jquery.com/category/deferred-object/|jQuery like Promise object}. {@link EThing.request|More ...} 
	 * @fires EThing#ething.device.created
	 * @example
	 * EThing.Device.MySensorsEthernetGateway.create({
	 *   name: "foobar",
	 *   address: "123.45.67.89"
	 * }).done(function(resource){
	 *     console.log('the new MySensors gateway has been added');
	 * })
	 */
	EThing.Device.MySensorsEthernetGateway.create = function(a,callback){
		
		a.type = 'MySensorsEthernetGateway';
		
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
	 * Creates a new MySensors gateway.
	 *
	 * @method EThing.Device.MySensorsSerialGateway.create
	 * @param {object} attributes
	 * @param {function(data,XHR,options)} [callback] it is executed once the request is complete whether in failure or success
	 * @returns {Deferred} a {@link http://api.jquery.com/category/deferred-object/|jQuery like Promise object}. {@link EThing.request|More ...} 
	 * @fires EThing#ething.device.created
	 * @example
	 * EThing.Device.MySensorsSerialGateway.create({
	 *   name: "foobar",
	 *   port: "/dev/ttyS0",
	 *   baudrate: 115200,
	 * }).done(function(resource){
	 *     console.log('the new MySensors gateway has been added');
	 * })
	 */
	EThing.Device.MySensorsSerialGateway.create = function(a,callback){
		
		a.type = 'MySensorsSerialGateway';
		
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
	 * Add a new MySensors node to an existing MySensors gateway.
	 *
	 * @method EThing.Device.MySensorsNode.create
	 * @param {object} attributes
	 * @param {function(data,XHR,options)} [callback] it is executed once the request is complete whether in failure or success
	 * @returns {Deferred} a {@link http://api.jquery.com/category/deferred-object/|jQuery like Promise object}. {@link EThing.request|More ...} 
	 * @fires EThing#ething.device.created
	 * @example
	 * EThing.Device.MySensorsNode.create({
	 *   name: "node45",
	 *   nodeId: 45,
	 *   gateway: "4ge7r81"
	 * }).done(function(resource){
	 *     // success
	 * })
	 */
	EThing.Device.MySensorsNode.create = function(a,callback){
		
		a.type = 'MySensorsNode';
		
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
	 * Add a new MySensors sensor to an existing MySensors node.
	 *
	 * @method EThing.Device.MySensorsSensor.create
	 * @param {object} attributes
	 * @param {function(data,XHR,options)} [callback] it is executed once the request is complete whether in failure or success
	 * @returns {Deferred} a {@link http://api.jquery.com/category/deferred-object/|jQuery like Promise object}. {@link EThing.request|More ...} 
	 * @fires EThing#ething.device.created
	 * @example
	 * EThing.Device.MySensorsSensor.create({
	 *   name: "sensor5",
	 *   sensorId: 5,
	 *   node: "h1e7r81"
	 * }).done(function(resource){
	 *     // success
	 * })
	 */
	EThing.Device.MySensorsSensor.create = function(a,callback){
		
		a.type = 'MySensorsSensor';
		
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