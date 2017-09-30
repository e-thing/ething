(function (global) {
	
	var EThing = global.EThing;
	
	
	
	
	/**
	 * Constructs a Denon Device instance from an object decribing a Denon device (Marantz M-CR611). Should not be called directly. Use instead {@link EThing.list}.
	 * @protected
	 * @class The Denon Device resource handle
	 * @memberof EThing.Device
	 * @extends EThing.Device
	 * @param {object} json
	 */
	EThing.Device.Denon = function(json)
	{
		EThing.Device.call(this, json);
	}
	EThing.utils.inherits(EThing.Device.Denon, EThing.Device);
	
	
	/**
	 * Return the host.
	 * @memberof EThing.Device.Denon
	 * @this {EThing.Device.Denon}
	 * @returns {string}
	 */
	EThing.Device.Denon.prototype.host = function() {
	  return this._json.host;
	}
	
	/**
	 * Return false if the device is not reachable.
	 * @memberof EThing.Device.Denon
	 * @this {EThing.Device.Denon}
	 * @returns {boolean}
	 */
	EThing.Device.Denon.prototype.isReachable = function() {
	  return !!this._json.reachable;
	}
	
	
	
	/**
	 * Creates a new Denon device
	 *
	 * @method EThing.Device.Denon.create
	 * @param {object} attributes
	 * @param {function(data,XHR,options)} [callback] it is executed once the request is complete whether in failure or success
	 * @returns {Deferred} a {@link http://api.jquery.com/category/deferred-object/|jQuery like Promise object}. {@link EThing.request|More ...} 
	 * @fires EThing#ething.device.created
	 * @example
	 * EThing.Device.Denon.create({
	 *   name: "Music",
	 *   host: "192.168.1.45"
	 * }).done(function(resource){
	 *     console.log('the new device has been created');
	 * })
	 */
	EThing.Device.Denon.create = function(a,callback){
		
		a.type = 'Denon';
		
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