(function (global) {
	
	var EThing = global.EThing;
	
	
	
	/**
	 * Constructs a Yeelight Device instance from an object decribing a Yeelight device. Base class of all Yeelight devices.
	 * @protected
	 * @class The Yeelight Device resource handle
	 * @memberof EThing.Device
	 * @extends EThing.Device
	 * @param {object} json
	 */
	EThing.Device.Yeelight = function(json)
	{
		EThing.Device.call(this, json);
	}
	EThing.utils.inherits(EThing.Device.Yeelight, EThing.Device);
	
	
	/**
	 * 
	 * @memberof EThing.Device.Yeelight
	 * @this {EThing.Device.Yeelight}
	 * @returns {string}
	 */
	EThing.Device.Yeelight.prototype.host = function() {
	  return this._json.host;
	}
	
	/**
	 * Constructs a YeelightBulbRGBW Device instance from an object decribing a Yeelight LED bulb (color) device. Should not be called directly. Use instead {@link EThing.list}.
	 * @protected
	 * @class The YeelightBulbRGBW Device resource handle
	 * @memberof EThing.Device
	 * @extends EThing.Device
	 * @param {object} json
	 */
	EThing.Device.YeelightBulbRGBW = function(json)
	{
		EThing.Device.Yeelight.call(this, json);
	}
	EThing.utils.inherits(EThing.Device.YeelightBulbRGBW, EThing.Device.Yeelight);
	
	
	
	
	
	/**
	 * Creates a new YeelightBulbRGBW device
	 *
	 * @method EThing.Device.YeelightBulbRGBW.create
	 * @param {object} attributes
	 * @param {function(data,XHR,options)} [callback] it is executed once the request is complete whether in failure or success
	 * @returns {Deferred} a {@link http://api.jquery.com/category/deferred-object/|jQuery like Promise object}. {@link EThing.request|More ...} 
	 * @fires EThing#ething.device.created
	 * @example
	 * EThing.Device.YeelightBulbRGBW.create({
	 *   host: "192.168.1.125",
	 * }).done(function(resource){
	 *     console.log('the new device has been created');
	 * })
	 */
	EThing.Device.YeelightBulbRGBW.create = function(a,callback){
		
		a.type = 'YeelightBulbRGBW';
		
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