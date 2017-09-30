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
	 * @returns {object|null}
	 */
	EThing.Device.MQTT.prototype.auth = function() {
	  return this._json.auth || null;
	}
	
	/**
	 * Return true if a connection to the device is opened
	 * @memberof EThing.Device.MQTT
	 * @this {EThing.Device.MQTT}
	 * @returns {boolean}
	 */
	EThing.Device.MQTT.prototype.isConnected = function() {
	  return !!this._json.connected;
	}
	
	
	/**
	 * Set the subscribed topics of this device.
	 * @memberof EThing.Device.MQTT
	 * @this {EThing.Device.MQTT}
	 * @param {String|Array} [subs] the list of the subscribed topics.
	 * @param {function(data,XHR,options)} [callback] it is executed once the request is complete whether in failure or success
	 * @returns {EThing.Device.MQTT} The instance on which this method was called.
	 */
	EThing.Device.MQTT.prototype.setSubscription = function(subs,callback) {
	  if(typeof spec == 'string')
		spec = JSON.parse(subs);
	  return this.set({
		subscription: subs
	  },callback);
	}

	/**
	 * Get the subscribed topics of this device.
	 * @memberof EThing.Device.MQTT
	 * @this {EThing.Device.MQTT}
	 * @param {function(data,XHR,options)} [callback] it is executed once the request is complete whether in failure or success
	 * @returns {EThing.Device.MQTT} The instance on which this method was called.
	 */
	EThing.Device.MQTT.prototype.getSubscription = function(callback) {
	  return EThing.Device.MQTT.getSubscription(this, callback);
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
			'converter': EThing.resourceConverter
		},callback).done(function(r){
			EThing.trigger('ething.device.created',[r]);
		});
		
	};
	
	
	EThing.Device.MQTT.getSubscription = function(dev, callback){
		var context;
		
		if(dev instanceof EThing.Device.MQTT){
			context = dev;
			dev = dev.id();
		}
		else if(!EThing.utils.isId(dev))
			throw "First argument must be a Device object or a Device id !";
		
		return EThing.request({
			'url': '/devices/' + dev + '/subscription',
			'dataType': 'json',
			'context': context,
			'converter': function(subs){
				if(context instanceof EThing.Device.MQTT){
					// attach this specification to the device
					context.subscription = subs;
				}
				return subs;
			}
		},callback);
		
	};
	
	
})(this);