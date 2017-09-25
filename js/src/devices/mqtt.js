(function (global) {
	
	var EThing = global.EThing;
	
	
	
	
	/**
	 * Constructs a MQTT Device instance from an object decribing a MQTT device. Should not be called directly. Use instead {@link EThing.list}.
	 * @protected
	 * @class The MQTT Device resource handle
	 * @memberof EThing.Device
	 * @extends EThing.Device
	 * @param {object} json
	 */
	EThing.Device.MQTT = function(json)
	{
		EThing.Device.call(this, json);
	}
	EThing.utils.inherits(EThing.Device.MQTT, EThing.Device);
	
	
	/**
	 * 
	 * @memberof EThing.Device.MQTT
	 * @this {EThing.Device.MQTT}
	 * @returns {string}
	 */
	EThing.Device.MQTT.prototype.host = function() {
	  return this._json.host;
	}
	
	/**
	 * 
	 * @memberof EThing.Device.MQTT
	 * @this {EThing.Device.MQTT}
	 * @returns {number}
	 */
	EThing.Device.MQTT.prototype.port = function() {
	  return this._json.port;
	}
	
	/**
	 * 
	 * @memberof EThing.Device.MQTT
	 * @this {EThing.Device.MQTT}
	 * @returns {string}
	 */
	EThing.Device.MQTT.prototype.topic = function() {
	  return this._json.topic;
	}
	
	/**
	 * 
	 * @memberof EThing.Device.MQTT
	 * @this {EThing.Device.MQTT}
	 * @returns {object|null}
	 */
	EThing.Device.MQTT.prototype.auth = function() {
	  return this._json.auth || null;
	}
	
	
	
	

	
	/**
	 * Creates a new MQTT device
	 *
	 * @method EThing.Device.MQTT.create
	 * @param {object} attributes
	 * @param {function(data,XHR,options)} [callback] it is executed once the request is complete whether in failure or success
	 * @returns {Deferred} a {@link http://api.jquery.com/category/deferred-object/|jQuery like Promise object}. {@link EThing.request|More ...} 
	 * @fires EThing#ething.device.created
	 * @example
	 * EThing.Device.MQTT.create({
	 *   host: "localhost",
	 *   topic: "outdoor/thermometer"
	 * }).done(function(resource){
	 *     console.log('the new device has been created');
	 * })
	 */
	EThing.Device.MQTT.create = function(a,callback){
		
		a.type = 'MQTT';
		
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