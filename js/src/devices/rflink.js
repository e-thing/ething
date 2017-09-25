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
	  return !!this._json.protocol;
	}
	
	/**
	 * Returns the nodeId of this node.
	 * @memberof EThing.Device.RFLinkSwitch
	 * @this {EThing.Device.RFLinkSwitch}
	 * @returns {string}
	 */
	EThing.Device.RFLinkSwitch.prototype.nodeId = function() {
	  return !!this._json.nodeId;
	}
	
	/**
	 * Returns the switchId of this node.
	 * @memberof EThing.Device.RFLinkSwitch
	 * @this {EThing.Device.RFLinkSwitch}
	 * @returns {string}
	 */
	EThing.Device.RFLinkSwitch.prototype.switchId = function() {
	  return !!this._json.switchId;
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
			'converter': resourceConverter
		},callback).done(function(r){
			EThing.trigger('ething.device.created',[r]);
		});
		
	};
	
	
})(this);