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
	 * RFLinkNode base class constructor.
	 * @protected
	 * @class The RFLinkNode Device resource handle
	 * @memberof EThing.Device
	 * @extends EThing.Device
	 * @param {object} json
	 */
	EThing.Device.RFLinkNode = function(json)
	{
		EThing.Device.call(this, json);
	}
	EThing.utils.inherits(EThing.Device.RFLinkNode, EThing.Device);
	
	/**
	 * Returns the protocol used to communicate with this node.
	 * @memberof EThing.Device.RFLinkNode
	 * @this {EThing.Device.RFLinkNode}
	 * @returns {string}
	 */
	EThing.Device.RFLinkNode.prototype.protocol = function() {
	  return this._json.protocol;
	}
	
	/**
	 * Returns the nodeId of this node.
	 * @memberof EThing.Device.RFLinkNode
	 * @this {EThing.Device.RFLinkNode}
	 * @returns {string}
	 */
	EThing.Device.RFLinkNode.prototype.nodeId = function() {
	  return this._json.nodeId;
	}
	
	/**
	 * Returns the switchId of this node (only available for switch/door/motion nodes).
	 * @memberof EThing.Device.RFLinkNode
	 * @this {EThing.Device.RFLinkNode}
	 * @returns {string}
	 */
	EThing.Device.RFLinkNode.prototype.switchId = function() {
	  return this._json.switchId;
	}
	
	/**
	 * Returns the subType of this node.
	 * @memberof EThing.Device.RFLinkNode
	 * @this {EThing.Device.RFLinkNode}
	 * @returns {string}
	 */
	EThing.Device.RFLinkNode.prototype.subType = function() {
	  return this._json.subType;
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
	 * Creates a new RFLink node. The kinf of node is defined by the mandatory subType attribute.
	 *
	 * @method EThing.Device.RFLinkNode.create
	 * @param {object} attributes
	 * @param {function(data,XHR,options)} [callback] it is executed once the request is complete whether in failure or success
	 * @returns {Deferred} a {@link http://api.jquery.com/category/deferred-object/|jQuery like Promise object}. {@link EThing.request|More ...} 
	 * @fires EThing#ething.device.created
	 * @example
	 * EThing.Device.RFLinkNode.create({
	 *   name: "foobar",
	 *   gateway: "4ge7r81",
	 *   subType: "switch", // switch | door | motion | thermometer | weatherStation | multimeter
	 *   protocol: "NewKaku",
	 *   nodeId: "008440e6",
	 *   switchId: "a" // nedded for switch | door | motion
	 * }).done(function(resource){
	 *     console.log('the new RFLink switch has been added');
	 * })
	 */
	EThing.Device.RFLinkNode.create = function(a,callback){
		
		a.type = 'RFLinkNode';
		
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