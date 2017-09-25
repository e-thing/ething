(function (global) {
	
	var EThing = global.EThing;
	
	
	
	
	/**
	 * Constructs a RTSP Device instance from an object decribing a RTSP device (typpicaly an IP camera). Should not be called directly. Use instead {@link EThing.list}.
	 * @protected
	 * @class The RTSP Device resource handle
	 * @memberof EThing.Device
	 * @extends EThing.Device
	 * @param {object} json
	 */
	EThing.Device.RTSP = function(json)
	{
		EThing.Device.call(this, json);
	}
	EThing.utils.inherits(EThing.Device.RTSP, EThing.Device);
	
	
	/**
	 * 
	 * @memberof EThing.Device.RTSP
	 * @this {EThing.Device.RTSP}
	 * @returns {string}
	 */
	EThing.Device.RTSP.prototype.url = function() {
	  return this._json.url;
	}
	
	/**
	 * 
	 * @memberof EThing.Device.RTSP
	 * @this {EThing.Device.RTSP}
	 * @returns {string}
	 */
	EThing.Device.RTSP.prototype.transport = function() {
	  return this._json.transport;
	}
	
	
	
	
	/**
	 * Creates a new RTSP device
	 *
	 * @method EThing.Device.RTSP.create
	 * @param {object} attributes
	 * @param {function(data,XHR,options)} [callback] it is executed once the request is complete whether in failure or success
	 * @returns {Deferred} a {@link http://api.jquery.com/category/deferred-object/|jQuery like Promise object}. {@link EThing.request|More ...} 
	 * @fires EThing#ething.device.created
	 * @example
	 * EThing.Device.RTSP.create({
	 *   name: "foobar",
	 *   url: "rtsp://123.45.67.89/stream"
	 * }).done(function(resource){
	 *     console.log('the new device has been created');
	 * })
	 */
	EThing.Device.RTSP.create = function(a,callback){
		
		a.type = 'RTSP';
		
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