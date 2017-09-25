(function (global) {
	
	var EThing = global.EThing;
	
	
	
	
	
	/* private constructor */
	/* base class of device */
	EThing.Device = function(json)
	{
		EThing.Resource.call(this, json);
		
		(this._json.operations || []).forEach(function(operationId){
			if(typeof this[operationId] == 'undefined'){
				var self = this;
				
				this[operationId] = function(data, binary, callback){
					var args = [].slice.call(arguments);
					return this.deferred(function(){
						args.unshift(operationId);
						args.unshift(this);
						return EThing.Device.execute.apply(EThing, args);
					});
				};
				
				this[operationId].getApi = function(callback){
					return EThing.Device.getApi(self, operationId, callback);
				};
				
				this[operationId].executeUrl = function(data){
					return self.executeUrl(operationId, data);
				};
			}
		}, this);
	}
	EThing.utils.inherits(EThing.Device, EThing.Resource);
	
	
	/**
	 * 
	 * @memberof EThing.Device
	 * @this {EThing.Device}
	 * @returns {object|null} Return either an object containing information about the location (coordinates, place, room ...) or null if no location is defined for this device.
	 */
	EThing.Device.prototype.location = function() {
	  return this._json.location || null;
	}
	
	/**
	 * 
	 * @memberof EThing.Device
	 * @this {EThing.Device}
	 * @returns {Date|null}
	 */
	EThing.Device.prototype.lastSeenDate = function() {
	  return (typeof this._json.lastSeenDate == 'string') ? new Date(this._json.lastSeenDate) : null;
	}
	
	/**
	 * 
	 * @memberof EThing.Device
	 * @this {EThing.Device}
	 * @returns {boolean}
	 */
	EThing.Device.prototype.hasBattery = function() {
	  return (typeof this._json.battery == "number") && this._json.battery >= 0 ;
	}
	
	/**
	 * 
	 * @memberof EThing.Device
	 * @this {EThing.Device}
	 * @returns {number}
	 */
	EThing.Device.prototype.battery = function() {
	  return this.hasBattery() ? this._json.battery : null ;
	}
	
	/**
	 * List the available operations on this device.
	 * @memberof EThing.Device
	 * @this {EThing.Device}
	 * @returns {string[]}
	 */
	EThing.Device.prototype.operations = function(){
		return this._json.operations ? this._json.operations : [];
	}
	
	
	/**
	 * Execute an operation on this device.
	 * @memberof EThing.Device
	 * @this {EThing.Device}
	 * @param {string} operationId
	 * @param {object} [data] the optional data required by the operation
	 * @param {boolean} [binary] if true, return the content as binary data (as Blob in a browser, or Buffer in NodeJs)
	 * @param {function(data,XHR,options)} [callback] it is executed once the request is complete whether in failure or success
	 * @returns {EThing.Device} The instance on which this method was called.
	 * @example
	 * // if this device is a thermometer :
	 * device.execute('getTemperature').done(function(data){
     *   // success, handle the data here
     * });
	 *
	 * // if this device is a switch :
	 * device.execute('setState', {
	 * 	 state: true
	 * });
	 * 
	 * // you may also do :
	 * device.getTemperature().done(function(data){
     *   // success, handle the data here
     * });
	 *
	 */
	EThing.Device.prototype.execute = function(){
		var args = [].slice.call(arguments);
		return this.deferred(function(){
				args.unshift(this);
				return EThing.Device.execute.apply(EThing, args);
			});
	}
	
	/**
	 * Returns an url for executing an operation.
	 * @memberof EThing.Device
	 * @this {EThing.Device}
	 * @param {string} operationId
	 * @param {object} [data] the optional data required by the operation
	 * @returns {string} The url.
	 * @example
	 * 
	 * var image = new Image();
	 * image.src = device.executeUrl('getImage');
	 * document.body.appendChild(image);
	 *
	 */
	EThing.Device.prototype.executeUrl = function(operationId, data){
		var url = 'devices/'+this.id()+'/call/'+operationId;
		
		if(isPlainObject(data) && Object.keys(data).length !== 0){
			var jsonStr = JSON.stringify(data);
			url += '?paramData='+ encodeURIComponent(jsonStr);
		}
		
		return EThing.toApiUrl(url,true);
	}
	
	/**
	 * Retrieve information about a specific operation or all the operations available for this device.
	 * @memberof EThing.Device
	 * @this {EThing.Device}
	 * @param {string} [operationId] if set, only information about this operation will be returned
	 * @param {function(data,XHR,options)} [callback] it is executed once the request is complete whether in failure or success
	 * @returns {EThing.Device} The instance on which this method was called.
	 *
	 */
	EThing.Device.prototype.getApi = function(operationId, callback){
		var args = [].slice.call(arguments);
		return this.deferred(function(){
			args.unshift(this);
			return EThing.Device.getApi.apply(EThing, args);
		});
	}
	
	
	
	
	
	/*
	device, operationId[, data ]
	*/
	EThing.Device.execute = function(device, operationId, data, binary, callback){
		
		var context;
		
		if(device instanceof EThing.Device){
			context = device;
			device = device.id();
		}
		else if(isResourceId(device))
			device = device;
		else {
			throw "First argument must be a Device object or a Device id !";
			return;
		}
		
		if(arguments.length == 4){
			
			if(typeof binary == 'function'){
				callback = binary;
				binary = undefined;
			}
			
		} else if(arguments.length == 3){
			
			if(typeof data == 'function'){
				callback = data;
				data = undefined;
			}
			
		}
		
		return EThing.request({
			'url': '/devices/' + device + '/call/' + operationId,
			'method': 'POST',
			'contentType': "application/json; charset=utf-8",
			'data': typeof data != 'undefined' && data!==null ? JSON.stringify(data) : undefined,
			'dataType': binary ? (EThing.utils.isNode ? 'buffer' : 'blob') : 'auto',
			'context': context
		},callback);
		
	};
	
	
	/*
	device[, operationId]
	*/
	EThing.Device.getApi = function(device, operationId, callback){
		
		var context;
		
		if(typeof operationId == 'function' && typeof callback == 'undefined'){
			callback = operationId;
			operationId = undefined;
		}
		
		if(device instanceof EThing.Device){
			context = device;
			device = device.id();
		}
		else if(isResourceId(device))
			device = device;
		else {
			throw "First argument must be a Device object or a Device id !";
			return;
		}
		
		return EThing.request({
			'url': '/devices/' + device + '/api' + (operationId?('/'+operationId):''),
			'method': 'GET',
			'context': context,
			'dataType': 'json'
		},callback);
		
	};
	
	
	
	
})(this);