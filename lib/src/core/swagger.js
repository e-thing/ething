(function (global) {

var EThing = global.EThing || {};

var dependencies = '//cdn.rawgit.com/swagger-api/swagger-js/v2.1.18/browser/swagger-client.js';

/**
* A HTTP client using the EThing API request function.
*/
var ethingHTTPSwaggerClient = {
  // implement an execute function
  execute: function(obj) {
	
	obj.data = obj.body;
	
	var accept = obj.headers['Accept'];
	
	// get binary data if the request expect an image back
	if(/^image\//.test(accept))
		obj.dataType = 'blob';
	else
		obj.dataType = 'text'; // force it as text, let the swagger lib do the parsing
	
	var d = EThing.request(obj, function(data,xhr,options){
		
		// parse header into a key/value object
		var headers = {};
		var headerArray = xhr.getAllResponseHeaders().split('\n');
		for (var i = 0; i < headerArray.length; i++) {
			var toSplit = headerArray[i].trim();

			if (toSplit.length === 0) {
				continue;
			}

			var separator = toSplit.indexOf(':');

			if (separator === -1) {
				// Name but no value in the header
				headers[toSplit] = null;

				continue;
			}

			var name = toSplit.substring(0, separator).trim();
			var value = toSplit.substring(separator + 1).trim();

			headers[name] = value;
		}
		
		var out = {
		  url: obj.url,
		  method: obj.method,
		  status: xhr.status,
		  statusText: xhr.statusText,
		  headers: headers
		};
		
		if(data instanceof EThing.Error){
			out.data = data.message;
			out.message = data.message;
			obj.on.error(out);
		}
		else {
			try {
			  var possibleObj =  xhr.responseJSON || jsyaml.safeLoad(xhr.responseText);
			  out.obj = (typeof possibleObj === 'string') ? {} : possibleObj;
			} catch (ex) {}
			
			out.data = data;
			obj.on.response(out);
		}
		
	});
	
	obj.deferred = d;
    
  }
};



var depdfr = null;
function depload(){
	if(!depdfr){
		depdfr = EThing.utils.require(dependencies);
	}
	return depdfr;
};



EThing.Device.getDescriptor = function(dev, raw, callback){
	
	var dev, context;
	
	if(typeof raw == 'function' && typeof callback == 'undefined'){
		callback = raw;
		raw = false;
	}
	
	if(dev instanceof EThing.Device){
		context = dev;
		dev = dev.id();
	}
	else if(!EThing.utils.isId(dev))
		throw "First argument must be a Device object or a Device id !";
	
	return EThing.request({
		'url': '/device/' + dev + '/descriptor',
		'context': context,
		'converter': function(spec){
			
			var url = EThing.toApiUrl('device/' + dev + '/request');
			
			if(!spec.swagger) spec.swagger = "2.0";
			if(!spec.info) spec.info = {};
			if(!spec.info.version) spec.info.version = "0.0.0";
			if(!spec.info.title) spec.info.title = (this instanceof EThing.Device) ? this.name() : 'unnamed';
			if(!spec.paths) spec.paths = {};
			
			if(!raw){
				// url parser
				var parser = document.createElement('a');
				parser.href = url; // see https://gist.github.com/jlong/2428561
				
				spec.host = parser.host+(parser.port && parser.port != '80' ? (':'+parser.port) : '');
				spec.basePath = (parser.pathname+(spec.basePath || '')).replace(/\/+/,'/').replace(/\/$/,'');
				spec.schemes = [parser.protocol.replace(/:$/, '')];
			}
			
			return spec;
			
		}
	},callback);
	
};

EThing.Device.getSwaggerClient = function(device, callback){
	var dfr = new EThing.utils.Deferred(), context;
	
	if(device instanceof EThing.Device){
		context = device;
		device = device.id();
	}
	
	EThing.utils.Deferred.when(
		EThing.Device.getDescriptor(device),
		depload()
	).done(function(){
		
		var spec = arguments[0][0];
		
		var client = new SwaggerClient({
			spec: spec,
			client: ethingHTTPSwaggerClient,
			success: function() {
				
				var client = this;
				
				var operations = {};
				client.apisArray.forEach(function(api){
				  Object.keys(client.apis[api.name].operations).forEach(function(operationName){
					operations[operationName] = {
					  execute: client.apis[api.name][operationName],
					  api: client.apis[api.name].apis[operationName]
					}
				  })
				});
				
				client.operations = operations;
				
				dfr.resolveWith(context,[this]);
			}
		});
		
	})
	.fail(function(err){
		dfr.rejectWith(context,[err]);
	});
	
	return dfr.promise();
};

/**
 * Get the API descriptor of this device.
 * @memberof EThing.Device
 * @this {EThing.Device}
 * @returns {EThing.Device}
 */
EThing.Device.prototype.getDescriptor = function(raw, callback) {
  return this.deferred(function(){
			return EThing.Device.getDescriptor(this,raw,callback);
		});
}

/**
 * Get the SwaggerClient of this device.
 * @memberof EThing.Device
 * @this {EThing.Device}
 * @returns {EThing.Device}
 */
EThing.Device.prototype.getSwaggerClient = function(callback) {
  return this.deferred(function(){
			return EThing.Device.getSwaggerClient(this,callback);
		});
}




EThing.utils.ethingHTTPSwaggerClient = ethingHTTPSwaggerClient;


})(this);
