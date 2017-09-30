/**
 * EThing - javascript API of the EThing project
 * @version v0.1.0
 */
(function (global) {
	
	
	/**
	 * Contains all eThing API classes and functions.
	 * @namespace EThing
	 */
	var EThing = global.EThing || {};
	
	var Blob = global.Blob || function(){};
	var Buffer = global.Buffer || function(){};
	
	var extend = EThing.utils.extend;
	var isResourceId = EThing.utils.isId;
	var isPlainObject = EThing.utils.isPlainObject;
	
	
	
	
	var ajaxSuccessHandlers = [],
		ajaxCompleteHandlers = [],
		ajaxErrorHandlers = [],
		ajaxSendHandlers = [],
		apiRequestPrefilterHandler = null;
	
	
	EThing.Error = function(json){
		this.name = 'EThing.Error';
		if(typeof json == "string")
			json = {
				message: json
			};
		extend(this, {
			message: 'unknown error'
		}, json);
	}
	EThing.Error.prototype = new Error;
	
	
	// only absolute url will be preserved untouched,
	// else api server url is prepended
	EThing.toApiUrl = function(url, auth){
		url = url || '';
		
		if(!/^([a-z]+:)?\/\//.test(url)){
			// relative url
			if(!/^\//.test(url) && url)
				url = '/'+url;
			
			url = EThing.config.apiUrl + url;
		}
		
		if(auth && isApiUrl(url)){
			url = _processAuth(url);
			if(typeof apiRequestPrefilterHandler == 'function')
				url = apiRequestPrefilterHandler(url);
		}
		return url;
	}
	
	// returns true if it is an URL to the HTTP API
	var isApiUrl = function(url){
		return (new RegExp('^([a-z]+:)?//'+EThing.config.apiUrl.replace(/^([a-z]+:)?\/\//,''))).test(url);
	}
	
	
	
	EThing.apiUrl = function(){
		return EThing.toApiUrl();
	}
	
	
	
	var ajax = function(options){
		var deferred = new EThing.utils.Deferred(),
			xhr = new global.XMLHttpRequest();
		
		if(typeof options == 'string')
			options = {
				url: options
			};
		
		options = extend({
			method: 'GET',
			context: null,
			url: null,
			data: null,
			contentType: null, // When sending data to the server, use this content type , default to 'application/x-www-form-urlencoded; charset=UTF-8'
			headers: null,
			dataType: null, // The type of data that you're expecting back from the server (json -> {object}, text -> {string} , arraybuffer, blob -> (not available on nodejs), buffer (nodejs only) )
			converter: null, // a user defined function to convert the receive data into something else ...
			synchronous: false
		},options);
		
		
		if(typeof options.url != 'string')
			return null;
		
		var url = EThing.toApiUrl(options.url);
		var apiRequest = isApiUrl(url);
		
		
		options.method = options.method.toUpperCase();
		
		var context = options.context || EThing;
		
		var isBodyRequest = !/^(?:GET|HEAD)$/.test( options.method ),
			body = undefined,
			hasData = typeof options.data != 'undefined' && options.data !== null;
		
		
		
		// If data is available, append data to url
		if ( !isBodyRequest && hasData ){
			// GET, HEAD request, append the data to the query string
			url += ( /\?/.test( url ) ? "&" : "?" ) + ( typeof options.data == 'string' ? options.data : EThing.utils.param(options.data));
		}
		
		
		xhr.open(options.method, url, !options.synchronous);
		
		
		// user headers
		var requestContentType = null;
		if(isPlainObject(options.headers)){
			for(var i in options.headers){
				if(options.headers.hasOwnProperty(i)){
					if(/^content-type$/i.test(i)){
						requestContentType = options.headers[i];
					}
					xhr.setRequestHeader(i, options.headers[i]);	
				}
			}
		}
		
		// content-type header
		if(!requestContentType && options.contentType)
			xhr.setRequestHeader('Content-Type', requestContentType = options.contentType);
		
		if(isBodyRequest && hasData){
			
			if(requestContentType){
				
				body = options.data;
				
				if(isPlainObject(options.data) || Array.isArray(options.data)){
					// transform the data according to the content-type
					if(/json/i.test(requestContentType))
						body = JSON.stringify(options.data)
					else if(/application\/x-www-form-urlencoded/i.test(requestContentType))
						body = EThing.utils.param(options.data);
				}
				
			} else {
				// no content-type set, set to defaults
				if(options.data instanceof Blob){
					xhr.setRequestHeader('Content-Type', requestContentType = options.data.type);
					body = options.data;
				} else if( (options.data instanceof ArrayBuffer) || (options.data instanceof Buffer) ){
					xhr.setRequestHeader('Content-Type', requestContentType = 'application/octet-stream');
					body = options.data;
				} else {
					xhr.setRequestHeader('Content-Type', requestContentType = 'application/x-www-form-urlencoded; charset=UTF-8');
					body = typeof options.data == 'string' ? options.data : EThing.utils.param(options.data);
				}
			}
			
		}
		
		
		
		// authentication
		if(apiRequest){
			xhr = _processAuth(xhr);
			if(typeof apiRequestPrefilterHandler == 'function')
				xhr = apiRequestPrefilterHandler(xhr);
		}
		
		// responseType
		var dataType = options.dataType;
		if(dataType && dataType != 'auto') xhr.responseType = dataType;
		
		function reject(error){
			
			var ct = xhr.getResponseHeader("Content-Type") || '',
				data = null;
			
			if(typeof error != 'undefined'){
				data = error;
			}
			else if(/json/.test(ct) || /text\/plain/.test(ct)){
				
				
				switch(xhr.responseType){
					
					case '':
					case 'text':
					case 'json':
						data = xhr.response;
						break;
					case 'blob':
						
						if(options.synchronous){
							
							if(!FileReaderSync){
								throw new Error("FileReaderSync not supported.");
							}
							
							var fileReader = new FileReaderSync();
							data = String.fromCharCode.apply(null, new Uint8Array(fileReader.readAsArrayBuffer(xhr.response)));
						} else {
							data = EThing.utils.Deferred();
							
							if(!FileReader){
								throw new Error("FileReaderSync not supported.");
							}
							
							var fileReader = new FileReader();
							fileReader.onload = function() {
								data.resolve( String.fromCharCode.apply(null, new Uint8Array(this.result)) );
							};
							fileReader.readAsArrayBuffer(xhr.response);
						}
						
						break;
					case 'arraybuffer':
						data = String.fromCharCode.apply(null, new Uint8Array(xhr.response));
						break;
					case 'buffer':
						data = xhr.response.toString("utf8");
						break;
					default:
						throw new Error(xhr.responseType+" response type not supported.");
						break;
				}
				
			}
			
			EThing.utils.Deferred.when(data).always(function(data){
				
				try{
					data = JSON.parse(data);
				} catch(e){}
				
				var error = new EThing.Error(data || (xhr.status ? (xhr.status+' ['+xhr.statusText+']') : 'unknown error')),
					args = [error,xhr,options];
				
				EThing.trigger('ething.request.error',args);
				ajaxErrorHandlers.forEach(function(handler){
					handler.apply(context,args);
				});
				EThing.trigger('ething.request.complete',args);
				ajaxCompleteHandlers.forEach(function(handler){
					handler.apply(context,args);
				});
				deferred.rejectWith(context,args);
				
			});
			
			
		}
		
		function resolve(data){
			var args = [data,xhr,options];
			
			EThing.trigger('ething.request.success',args);
			ajaxSuccessHandlers.forEach(function(handler){
				handler.apply(context,args);
			});
			EThing.trigger('ething.request.complete',args);
			ajaxCompleteHandlers.forEach(function(handler){
				handler.apply(context,args);
			});
			deferred.resolveWith(context,args);
		}
		
		// events
		xhr.onload=function(e){
			var success = xhr.status >= 200 && xhr.status < 300 || xhr.status === 304;
			if (success) {  
				// success
				var data = xhr.response;
				
				if(dataType == 'auto'){
					if(/json/.test(xhr.getResponseHeader("Content-Type") || '')){
						try {
							data = JSON.parse(data);
						} catch(err){}
					}
				} else if(dataType == 'json' && typeof data === 'string'){ // for ie compatibility
					try {
						data = JSON.parse(data);
					} catch(err){}
				}
				
				if(typeof options.converter == 'function'){
					data = options.converter.call(context,data,xhr,options);
				}
				
				resolve(data);
			}
			else
				reject();
		}
		xhr.onerror=function(){reject();};
		xhr.onabort=function(){reject();};
		xhr.onprogress=function(e){
			deferred.notifyWith(context,[e,xhr,options]);
		}
		
		var evt = EThing.Event('ething.request.send');
		EThing.trigger(evt,[xhr, options]);
		
		if(evt.isDefaultPrevented()){
			reject('Aborded');
		}
		else {
		
			ajaxSendHandlers.forEach(function(handler){
				handler.call(context,xhr);
			});
			
			xhr.send(body);
			
		}
		
		return deferred.promise();
	}
	
	function isResourceMetaData(json){
		return json.hasOwnProperty('id') && json.hasOwnProperty('type') && json.hasOwnProperty('name');
	}
	
	var getClass = EThing.getClass = function (str){
		var cc = str.split(/[.\\]/), obj = EThing;
		cc.forEach(function(c){
			if(typeof obj[c] != 'undefined')
				obj = obj[c];
			else {
				obj = undefined;
				return false;
			}
		});
		return obj;
	}
	
	var instanciate = EThing.instanciate = function (json){
		var cl = getClass(json.type);
		return cl ? new (cl)(json) : false;
	}
	
	// if the argument is a json object describing a resource, then it converts it into a Resource instance, else it returns the object unchanged
	EThing.resourceConverter = function(data, xhr){
		
		if(typeof data == 'object' && data !== null){
			
			var isArray = Array.isArray(data);
			if(!isArray) data = [data];
			
			// convert into resource instance
			data = data.map(function(r){
				return EThing.instanciate(r);
			}).filter(function(r){
				return r;
			});
			
			
			// update the arbo collection with the new properties
			// and return the corresponding resource object(s)
			data = EThing.arbo.update(data).resources;
			
			if(!isArray) data = data.length ? data[0] : null;
		}
		
		return data;
	}
	
	
	
	
	/**
	 * Make a HTTP request. The options object contains the following properties :
	 *  - url {string} __required__ The url of the request. The API url will be prepended to relative URLs.
	 *  - method {string} The HTTP request method to use. Default is GET.
	 *  - data {string|object|Blob|ArrayBuffer|Buffer} The query string for GET request. The HTTP request body for POST|PATCH|PUT requests. If an object is given, it will be serialized into a query string.
	 *  - contentType {string} When sending data to the server, use this content type. Default is 'application/octet-stream' if the data is an instance of ArrayBuffer or Buffer, if data is an instance of Blob, the default will be the type of the data itself, else 'application/x-www-form-urlencoded; charset=UTF-8'.
	 *  - dataType {string} The type of data that you're expecting back from the server. See {@link http://xhr.spec.whatwg.org/#the-responsetype-attribute|XMLHttpRequest standard}.
	 *  - headers {object} Additional HTTP request headers.
	 *  - context {object} The value of this provided for the call of the callbacks
	 *  - converter {function(data,XHR)} A function that returns the transformed value of the response
	 *
	 * 
	 * You may also give a callback as a second parameter. This callback is executed when the request is complete whether in failure or success.
	 * On success, it receives the returned request data, as well as the XMLHttpRequest object.
	 * On failure, the first parameter will be a Error object describing the error.
	 * To check if a request is in failure :
	 * <pre><code>EThing.request(options,function(data,xhr){
	 *     if(data instanceof EThing.Error){
	 *       // an error occurs, print the associated message
	 *       console.log(data.message);
	 *     }
	 *   })`
	 * </code></pre>
	 *
	 *
	 * This function returns a {@link http://api.jquery.com/category/deferred-object/|jQuery like Promise object} object.
	 *
	 * The done|fail|always functions take the same parameters than the {@link http://api.jquery.com/category/deferred-object/|jQuery version}.
	 *
	 *
	 *
	 * @method EThing.request
	 * @param {string|object} options a set of key/value pairs that configure the request. If an URL is given, a GET request with the default options is made.
	 * @param {function(data,XHR,options)} [callback] it is executed once the request is complete whether in failure or success
	 * @returns {Deferred} a {@link http://api.jquery.com/category/deferred-object/|jQuery like Promise object}
	 * @example
	 * // GET request
	 * EThing.request('/resources') // is equivalent to EThing.list()
	 *
	 * // pass an object to make more complex request
	 * // store some data in a file
	 * EThing.request({
	 *   url: '/files/'+fileId,
	 *   method: 'PUT',
	 *   data: 'some content here ...',
	 *   contentType: 'text/plain'
	 * })
	 * .done(function(file){
	 *   console.log("the content was stored in the file "+file.name());
	 * })
	 * .fail(function(error){
	 *   console.log("an error occurs : "+error.message);
	 * });
	 */
	// opt : same as ajax options or an url
	EThing.request = function(opt,callback){
		var d = ajax(opt);
		
		if(typeof callback == 'function') {
			d.always(function(){
				callback.apply(this,Array.prototype.slice.call(arguments));
			});
		}
		
		// if sync return the result instead of the deferred object !
		if(opt.synchronous){
			var result = null;
			d.always(function(r){
				result = r;
			});
			return result;
		} else {
			return d;
		}
	}
	
	
	/**
	*
	*/
	EThing.apiRequestPrefilter = function(handler){
		apiRequestPrefilterHandler = handler;
	}
	/**
	 * Register a handler to be called just before API requests is sent.
	 *
	 * @method EThing.ajaxSend
	 * @param {function(XHR)} handler The function to be invoked.
	 */
	EThing.ajaxSend = function(handler){
		if(typeof handler == 'function'){
			ajaxSendHandlers.push(handler);
		}
	}
	/**
	 * Register a handler to be called when API requests complete.
	 *
	 * @method EThing.ajaxComplete
	 * @param {function(data,XHR,options)} handler The function to be invoked.
	 */
	EThing.ajaxComplete = function(handler){
		if(typeof handler == 'function'){
			ajaxCompleteHandlers.push(handler);
		}
	}
	/**
	 * Register a handler to be called when API requests complete successfully.
	 *
	 * @method EThing.ajaxSuccess
	 * @param {function(data,XHR,options)} handler The function to be invoked.
	 */
	EThing.ajaxSuccess = function(handler){
		if(typeof handler == 'function'){
			ajaxSuccessHandlers.push(handler);
		}
	}
	/**
	 * Register a handler to be called when API requests complete with an error.
	 *
	 * @method EThing.ajaxError
	 * @param {function(data,XHR,options)} handler The function to be invoked.
	 */
	EThing.ajaxError = function(handler){
		if(typeof handler == 'function'){
			ajaxErrorHandlers.push(handler);
		}
	}
	
	
	
	
		
	// deferred engine
	var DeferredObject = EThing.DeferredObject = function(){
		
		var resolvedDfr = EThing.utils.Deferred().resolve(),
			queue = [],
			self = this;
		
		
		['done','fail','always','progress','then','state','isRejected','isResolved'].forEach(function(fctname){
			this[fctname] = function(){
				// get last deferred object in queue
				var dfr = queue.length ? queue[queue.length-1].dfr : resolvedDfr;
				
				var r = dfr[fctname].apply(self,Array.prototype.slice.call(arguments));
				
				if(typeof r == 'object' && fctname!=='then'){
					// dfr object
					return self;
				} else {
					return r; // state , isRejected, isResolved, then
				}
			}
		}, this);
		this.promise = function(){
			return self;
		}
		
		function processQueue(){
			
			for(var i=0; i<queue.length; i++){
				
				var dfr = queue[i].dfr,
					pending = queue[i].pending,
					fn = queue[i].fn;
				
				if(pending){
					
					queue[i].pending = false;
					
					fn.call(self,self)
						.done(function(){
							
							var args = Array.prototype.slice.call(arguments);
							
							// why ? I don't remember ...
							/*if(args.length>0 && (args[0] instanceof EThing.Resource) && args[0].id() === self.id() )
								self._fromJson(args[0].json()); // update resource metadata*/
							
							dfr.resolveWith(self,args);
						})
						.fail(function(){
							dfr.rejectWith(self,Array.prototype.slice.call(arguments));
						})
						.progress(function(){
							dfr.notifyWith(self,Array.prototype.slice.call(arguments));
						});
					
				}
				else {
					
					if(dfr.isResolved() || dfr.isRejected()){
						queue.splice(i, 1); // remove finished actions
						i--;
						continue;
					}
					// else busy, wait for that element to finish
					
				}
				
				break;
				
			}
		}
		
		this.deferred = function(action){
			
			// bind a new deferred object to this new action
			var dfr = new EThing.utils.Deferred();
			
			
			dfr.always(function(){
				// execute the next action
				processQueue();
			});
			
			
			// add this action to the queue 
			queue.push({
				fn: action,
				dfr: dfr,
				pending: true
			});
			
			processQueue();
			
			return this; // chainable
			
		};
		
	}

	
	
	
	
	/*
	* Configuration
	*/
	
	var defaultApiUrl = (global.location ? (window.location.protocol+'//'+window.location.hostname) : 'http://localhost')+'/ething/api';
	
	
	
	EThing.config = extend({
		apiUrl: defaultApiUrl,
	},EThing.config);
	
	
	
	
	
	
	
	
	
	
	
	
	
	

	/**
	 * Base class of all the resources
	 * @protected
	 * @class
	 * @memberOf EThing
	 * @param {object} json
	 */
	EThing.Resource = function (json)
	{
		DeferredObject.call(this);
		
		EThing.EventEngine(this);
		
		this._fromJson(json, true);
	}
	EThing.utils.inherits(EThing.Resource,DeferredObject);
	
	// loader
	EThing.Resource.prototype._fromJson = function(json, noTrigger){
		
		var updated = this._json && json && this._json.modifiedDate && json.modifiedDate && this._json.modifiedDate !== json.modifiedDate;
		var updatedKeys = [];
		
		json = extend({
			name:null,
			id:null,
			type:null,
			createdBy:null,
			createdDate: 0,
			modifiedDate: 0,
			data: null,
			description: null
		}, json || {});
		
		if(!noTrigger && updated) {
			// list the kays that have been updated
			Object.keys(json).forEach(function(key){
				if((typeof this._json[key] === 'undefined') || !EThing.utils.isEqual(json[key],this._json[key])){
					updatedKeys.push(key);
				}
			},this);
		}
		
		this._json = json;
		
		if(!noTrigger && updated) {
			//console.log('resource updated '+this.name());
			this.trigger('updated', [updatedKeys]);
			EThing.trigger('ething.resource.updated',[this, updatedKeys]);
		}
		
		return updated;
	}
	
	
	/**
	 *  Returns the representation of this instance
	 * @memberof EThing.Resource
	 * @this {EThing.Resource}
	 * @returns {object}
	 */
	EThing.Resource.prototype.json = function(){
		return this._json;
	}
	
	// path accessors
	/**
	 * Returns the name of this resource. A name is constructed as __PathName/FileName__.
	 * To get only the FileName, see {@link EThing.Resource#basename}.
	 * To get only the PathName, see {@link EThing.Resource#dirname}.
	 * @memberof EThing.Resource
	 * @this {EThing.Resource}
	 * @returns {string}
	 */
	EThing.Resource.prototype.name = function() {
		return this._json.name;
	}
	/**
	 * Returns the path of this resource
	 * @memberof EThing.Resource
	 * @this {EThing.Resource}
	 * @returns {string}
	 */
	EThing.Resource.prototype.dirname = function() {
		return EThing.Resource.dirname(this._json.name);
	}
	/**
	 * Returns the basename of this resource
	 * @memberof EThing.Resource
	 * @this {EThing.Resource}
	 * @returns {string}
	 */
	EThing.Resource.prototype.basename = function() {
		return EThing.Resource.basename(this._json.name);
	}
	/**
	 * Returns the extension of this resource
	 * @memberof EThing.Resource
	 * @this {EThing.Resource}
	 * @returns {string}
	 */
	EThing.Resource.prototype.extension = function(){
		return EThing.Resource.extension(this._json.name);
	}
	/**
	 * Returns the id of this resource. This id is unique and immutable.
	 * @memberof EThing.Resource
	 * @this {EThing.Resource}
	 * @returns {string}
	 */
	EThing.Resource.prototype.id = function(){
		return this._json.id;
	}
	/**
	 * Returns information about the Resource which creates it.
	 * @memberof EThing.Resource
	 * @this {EThing.Resource}
	 * @returns {Object|null}
	 */
	EThing.Resource.prototype.createdBy = function(){
		return this._json.createdBy;
	}
	
	/**
	 *  Returns the type of this resource :
	 *  - "File"
	 *  - "Table"
	 *  - "App"
	 *  - "Device"
	 * @memberof EThing.Resource
	 * @this {EThing.Resource}
	 * @returns {string}
	 */
	EThing.Resource.prototype.type = function() {
		return this._json.type;
	}
	/**
	 *  Returns the type of this resource :
	 *  - "File"
	 *  - "Table"
	 *  - "App"
	 *  - "Device"
	 * @memberof EThing.Resource
	 * @this {EThing.Resource}
	 * @returns {string}
	 */
	EThing.Resource.prototype.baseType = function() {
		return this._json.type.split('\\').shift();
	}
	/**
	 * Create time for this resource
	 * @memberof EThing.Resource
	 * @this {EThing.Resource}
	 * @returns {Date}
	 */
	EThing.Resource.prototype.createdDate = function() {
		return new Date(this._json.createdDate);
	}
	EThing.Resource.prototype.ctime = function(){
		return this.createdDate();
	}
	
	/**
	 * Last time this resource was modified
	 * @memberof EThing.Resource
	 * @this {EThing.Resource}
	 * @returns {Date}
	 */
	EThing.Resource.prototype.modifiedDate = function() {
		return new Date(this._json.modifiedDate);
	}
	EThing.Resource.prototype.mtime = function(){
		return this.modifiedDate();
	}
	
	/**
	 * Tells if this resource is publicly available.
	 * @memberof EThing.Resource
	 * @this {EThing.Resource}
	 * @returns {boolean|string}
	 */
	EThing.Resource.prototype.public = function() {
		return this._json.public || false;
	}
	
	/**
	 * Returns the data attached to this resource.
	 * @memberof EThing.Resource
	 * @param {string} [name] an optional attribute name.
	 * @param {} [defaultValue] a default value if the attribute was not found.
	 * @param {function(data,XHR,options)} [callback] it is executed once the request is complete whether in failure or success
	 * @this {EThing.Resource}
	 * @returns {object|null}
	 */
	EThing.Resource.prototype.data = function(name, defaultValue) {
		if(typeof name == 'undefined')
			return this._json.data;
		else {
			return this._json.data.hasOwnProperty(name) ? this._json.data[name] : defaultValue;
		}
	}
	/**
	 * Returns the description of this resource
	 * @memberof EThing.Resource
	 * @this {EThing.Resource}
	 * @returns {string}
	 */
	EThing.Resource.prototype.description = function() {
		return this._json.description || "";
	}
	
	// resource modificators (async)
	/**
	 * Remove this resource.
	 * @memberof EThing.Resource
	 * @this {EThing.Resource}
	 * @param {Boolean} [removeChildren] When true, the children are also removed. Default to false.
	 * @param {function(data,XHR,options)} [callback] it is executed once the request is complete whether in failure or success
	 * @returns {EThing.Resource} The instance on which this method was called.
	 * @fires EThing#ething.resource.removed
	 * @example
	 * resource.remove().done(function(){
	 *   // the resource was successfully removed
	 * });
	 */
	EThing.Resource.prototype.remove = function(removeChildren, callback){
		return this.deferred(function(){
				return EThing.Resource.remove(this, callback);
			});
	}
	
	EThing.Resource.prototype.update = function(callback){
		return this.deferred(function(){
				return EThing.get(this, callback);
			});
	}
	
	/**
	 * Update this resource attributes
	 * @memberof EThing.Resource
	 * @this {EThing.Resource}
	 * @param {} properties
	 * @param {function(data,XHR,options)} [callback] it is executed once the request is complete whether in failure or success
	 * @returns {EThing.Resource} The instance on which this method was called.
	 * @example
	 * resource.set({
	 *   name: "newName.txt"
	 * }).done(function(){
	 *   console.log("the resource was successfully renamed to :"+this.name());
	 * });
	 */
	EThing.Resource.prototype.set = function(properties, callback){
		var args = [].slice.call(arguments);
		return this.deferred(function(){
				args.unshift(this);
				return EThing.Resource.set.apply(EThing, args);
			});
	}
	/**
	 * Attaches persistant data to this resource
	 * @memberof EThing.Resource
	 * @this {EThing.Resource}
	 * @param {object} data
	 * @param {function(data,XHR,options)} [callback] it is executed once the request is complete whether in failure or success
	 * @returns {EThing.Resource} The instance on which this method was called.
	 * @example
	 * resource.setData({
	 *   "key": "value"
	 * }).done(function(){
	 *   // success
	 * });
	 * 
	 * // you can also write :
	 * resource.setData("key", "value").done(function(){
	 *   // success
	 * });
	 */
	EThing.Resource.prototype.setData = function(data, callback){
		
		if(typeof data === 'string' && typeof callback != 'function'){
			var key = data, value = callback, callback = arguments[2];
			data = {};
			data[key] = value;
		}
		
		return this.set({'data':data},callback);
	}
	
	
	
	
	
	

	
	
	
	
	
	/**
	 * This function get the available resources. A filter may be given to retrieve resources with specific attributes (see the HTTP API for more details).
	 * @method EThing.list
	 * @param {string} [query] Query string for searching resources
	 * @param {function(data,XHR,options)} [callback] it is executed once the request is complete whether in failure or success
	 * @returns {Deferred} a {@link http://api.jquery.com/category/deferred-object/|jQuery like Promise object}. {@link EThing.request|More ...} 
	 * @example
	 * // get all the resources
	 * EThing.list().done(function(resources){
	 *     console.log(resources);
	 * })
	 *
	 * // get only File & Table resources
	 * EThing.list('type == "File" or type == "Table"').done(function(resources){
	 *     console.log(resources);
	 * })
	 */
	EThing.list = EThing.find = function(a,b)
	{
		var query = null, callback = null;
		
		if(arguments.length==1){
			if(typeof arguments[0] == 'function')
				callback = arguments[0];
			else
				query = arguments[0];
		}
		else if(arguments.length>=2){
			query = arguments[0];
			callback = arguments[1];
		}
		
		return EThing.request({
			'url': '/resources?' + EThing.utils.param({'q':query}),
			'method': 'GET',
			'dataType': 'json',
			'converter': EThing.resourceConverter
		},callback);
	};
	
	
	/**
	 * Gets an object containing informations about space usage :
	 *  - used {number} the amount of space used in bytes
	 *  - quota_size {number} the maximum space authorized in bytes
	 *
	 * @method EThing.Resource.usage
	 * @param {function(data,XHR,options)} [callback] it is executed once the request is complete whether in failure or success
	 * @returns {Deferred} a {@link http://api.jquery.com/category/deferred-object/|jQuery like Promise object}. {@link EThing.request|More ...} 
	 * @example
	 * // get the occupied space :
	 * EThing.Resource.usage().done(function(usage){
	 *     console.log('space used : ' + (100 * usage.used / usage.quota_size) );
	 * })
	 */
	EThing.Resource.usage = function(a)
	{
		var callback = a;
		
		return EThing.request({
			'url': '/usage',
			'dataType': 'json',
			'method': 'GET'
		},callback);
	};
	
	
	/*
	Resource,callback
	*/
	EThing.Resource.remove = function(a,removeChildren,callback)
	{
		var context;
		if(a instanceof EThing.Resource){
			context = a;
			a = a.id();
		}
		else if(!isResourceId(a)) {
			throw "First argument must be a Resource object or a Resource id : "+a;
			return;
		}
		
		if(arguments.length==2 && typeof removeChildren === 'function'){
			callback = removeChildren;
			removeChildren = false;
		}
		
		return EThing.request({
			'url': '/resources/' + a + '?' + EThing.utils.param({'children':removeChildren}),
			'method': 'DELETE',
			'context': context
		},callback).done(function(){
			EThing.trigger('ething.resource.removed',[a]);
		});
	};
	
	/**
	 * Gets a resource by its id.
	 *
	 * @method EThing.get
	 * @param {string|EThing.Resource} resourceIdentifier
	 * @param {function(data,XHR,options)} [callback] it is executed once the request is complete whether in failure or success
	 * @returns {Deferred} a {@link http://api.jquery.com/category/deferred-object/|jQuery like Promise object}. {@link EThing.request|More ...} 
	 * @example
	 * // get a resource by its id
	 * EThing.get("54516eb").done(function(resource){
	 *     console.log('the name is ' + resource.name());
	 * })
	 */
	EThing.get = function(a,b)
	{
		var context;
		if(a instanceof EThing.Resource){
			context = a;
			a = a.id();
		}
		else if(!isResourceId(a)) {
			throw "First argument must be a Resource object or a Resource id : "+a;
			return;
		}
		
		var callback = b;
		
		return EThing.request({
			'url': '/resources/' + a,
			'dataType': 'json',
			'method': 'GET',
			'context': context,
			'converter': EThing.resourceConverter
		},callback);
	};
	
	/*
	Resource,data,callback
	*/
	EThing.Resource.set = function(a,b,c)
	{
		var context;
		
		if(!isPlainObject(b) || !b){
			throw 'Second argument must be a unempty object !';
			return;
		}
		
		if(a instanceof EThing.Resource){
			context = a;
			a = a.id();
		}
		else if(!isResourceId(a)) {
			throw "First argument must be a Resource object or a Resource id : "+a;
			return;
		}
		
		var callback = c;
		
		return EThing.request({
			'url': '/resources/' + a,
			'dataType': 'json',
			'method': 'POST',
			'contentType': "application/json; charset=utf-8",
			'data': b,
			'context': context,
			'headers': {
				"X-HTTP-Method-Override": "PATCH"
			},
			'converter': EThing.resourceConverter
		},callback);
	};
	
	
	
	
	
	
	
	/*
	* TOOLS
	*/
	EThing.Resource.dirname = function(f) {
		var s = f.replace(/\/[^\/]*\/?$/, '');
		return ( s === f ) ? "" : s;
	}
	EThing.Resource.basename = function(f) {
		return f.replace( /.*\//, '' );
	}
	EThing.Resource.extension = function(f){
		return f.indexOf('.')>=0 ? f.split('.').pop() : '';
	}
	EThing.Resource.fnmatch = function fnmatch(pattern, path) {
		
		var patternTab = pattern.split(' ');
		var parsedPattern, regexp;
		
		for(var i=0; i<patternTab.length; i++){
			if(patternTab[i] == '') continue;
			
			parsedPattern = '^' + patternTab[i].replace(/\//g, '\\/').
			replace(/\*\*/g, '(\\/[^\\/]+)*').
			replace(/\*/g, '[^\\/]+').
			replace(/((?!\\))\?/g, '$1.') + '$';
			
			parsedPattern = '^' + parsedPattern + '$';
			
			regexp = new RegExp(parsedPattern);
			if( path.match(regexp) != null ) return true;
		}
		return false;
	};
	
	
	
	
	/*
	* Settings
	*/
	
	EThing.settings = EThing.settings || {};
	
	/**
	 * Retrieve the settings.
	 * @memberof EThing.settings
	 * @this {EThing.settings}
	 * @param {function(data,XHR,options)} [callback] it is executed once the request is complete whether in failure or success
	 * @returns {Deferred} a {@link http://api.jquery.com/category/deferred-object/|jQuery like Promise object}. {@link EThing.request|More ...} 
	 */
	
	EThing.settings.get = function(callback){
		return EThing.request({
			'url': '/settings',
			'dataType': 'json',
			'method': 'GET'
		},callback);
	};
	
	/**
	 * Update the settings.
	 * @memberof EThing.settings
	 * @this {EThing.settings}
	 * @param {object} [data] updated settings object
	 * @param {function(data,XHR,options)} [callback] it is executed once the request is complete whether in failure or success
	 * @returns {Deferred} a {@link http://api.jquery.com/category/deferred-object/|jQuery like Promise object}. {@link EThing.request|More ...} 
	 */
	EThing.settings.set = function(data, callback){
		
		if(!isPlainObject(data))
			throw "First argument must be an object !";
		
		
		return EThing.request({
			'url': '/settings',
			'dataType': 'json',
			'method': 'POST',
			'contentType': "application/json; charset=utf-8",
			'data': data,
			'headers': {
				"X-HTTP-Method-Override": "PATCH"
			}
		},callback);
	};
	
	
	
	/**
	 * Send a notification.
	 * @memberof EThing
	 * @param {string} [subject] The subject of the notification
	 * @param {string} message The message of the notification
	 * @param {function(data,XHR,options)} [callback] it is executed once the request is complete whether in failure or success
	 * @returns {Deferred} a {@link http://api.jquery.com/category/deferred-object/|jQuery like Promise object}. {@link EThing.request|More ...} 
	 * @example
	 * EThing.notify("hello world")
	 *   .done(function(){
	 *     alert("A notification has been sent");
	 *   })
	 */
	EThing.notify = function(subject,message, callback){
		var query = {};
		
		if(arguments.length == 3){
			query['body'] = message;
			query['subject'] = subject;
		}
		else if(arguments.length == 2){
			if(typeof message == 'string'){
				query['subject'] = subject;
				query['body'] = message;
			}
			else{
				query['body'] = subject;
				callback = message;
			}
		}
		else if(arguments.length == 1){
			query['body'] = subject;
		}
		else {
			throw "Bad arguments!";
			return;
		}
		
		return EThing.request({
			'url': '/notification',
			'method': 'POST',
			'contentType': "application/json; charset=utf-8",
			'data': query
		},callback);
	}
	
	
	
	
	
	/*
	 * AUTH
	 */
	
	var NoAuth = function(a){ return a; };
	
	
	// private
	var _app = null,
		_device = null,
		_scope = null,
		_authType = null,
		_processAuth = NoAuth; // function(xhr|url) -> return xhr|url
	
	
	
	/**
	 * @namespace EThing.auth
	 */

	EThing.auth = {};
	
	
	
	/**
	 * Returns true if the authentication process has been successful.
	 * @method EThing.auth.isAuthenticated
	 * @returns {boolean}
	 */
	EThing.auth.isAuthenticated = function(){
		return !!_authType;
	}
	
	/**
	 * Returns the authenticated app. Only available with app's apikey authentication.
	 * @method EThing.auth.getApp
	 * @returns {EThing.App} the authenticated app or null.
	 */
	EThing.auth.getApp = function(){
		return _app;
	}
	
	/**
	 * Returns the authenticated app. Only available with devices's apikey authentication.
	 * @method EThing.auth.getDevice
	 * @returns {EThing.Device} the authenticated device or null.
	 */
	EThing.auth.getDevice = function(){
		return _device;
	}
	
	/**
	 * Returns the scope of the current authentication
	 * @method EThing.auth.getScope
	 * @returns {string} the scope. May be an empty string if no permissions is set. May be null if full permissions.
	 */
	EThing.auth.getScope = function(){
		return _scope;
	}
	
	
	
	/**
	 * Reset authentication. You must restart an authentication process to make API calls again.
	 * @method EThing.auth.reset
	 */
	EThing.auth.reset = function(){
		_app = null;
		_device = null;
		_authType = null;
		_scope = null;
		_processAuth = NoAuth;
	}
	
	
	
	
	EThing.auth.setApiKey = function(apiKey){
		
		EThing.auth.reset();
		
		_processAuth = function(xhrOrUrl){
			
			if(typeof xhrOrUrl == 'string')
				xhrOrUrl = EThing.utils.insertParam(xhrOrUrl, 'api_key', apiKey);
			else 
				xhrOrUrl.setRequestHeader('X-API-KEY', apiKey);
			
			return xhrOrUrl;
		};
		
	};
	
	EThing.auth.setBasicAuth = function(login, password){
		
		EThing.auth.reset();
		
		_processAuth = function(xhrOrUrl){
			
			if(typeof xhrOrUrl == 'string')
				xhrOrUrl = xhrOrUrl.replace(/\/\/([^:]+:[^@]+@)?/, '//'+login+':'+password+'@');
			else 
				xhrOrUrl.setRequestHeader("Authorization", "Basic " + global.btoa(login + ":" + password));
			
			return xhrOrUrl;
		};
	};
	
	
	
	
	/**
	 * Initialize the eThing library.
	 *
	 * @method EThing.initialize
	 * @param {Object} options
	 * @param {number} options.apiUrl The URL of your eThing API (e.g. http://example.org/ething/api ).
	 * @param {number} [options.apiKey] Authenticate with an API key.
	 * @param {number} [options.login] Basic Authentication login (Should be used only server side i.e. NodeJS).
	 * @param {number} [options.password] Basic Authentication password (Should be used only server side i.e. NodeJS).
	 * @param {function(EThing.Error)} [errorFn] it is executed on authentication error.
	 * @returns {Deferred} a {@link http://api.jquery.com/category/deferred-object/|jQuery like Promise object}
	 * @fires EThing#ething.authenticated
	 * @example
	 *
	 * EThing.initialize({
     *    apiUrl: 'http://example.org/ething/api',
     *    apiKey: 'a4e28b3c-1f05-4a62-95f7-c12453b66b3c'
     *  }, function(){
	 *    // on authentication success
	 *    alert('connected !');
	 *  }, function(error) {
     *    // on authentication error
     *    alert(error.message);
     *  });
	 *
	 */
	EThing.initialize = function(options, successFn, errorFn){
		
		EThing.auth.reset();
		
		options = extend({
			apiUrl: null,
			// auth apikey
			apiKey: null,
			// auth basic
			login: null,
			password:null
		},options || {});
		
		if(options.apiUrl)
			EThing.config.apiUrl = options.apiUrl;
		
		
		if(options.apiKey)
			EThing.auth.setApiKey(options.apiKey);
		else if(options.login && options.password)
			EThing.auth.setBasicAuth(options.login, options.password);
		
		return EThing.request({
			'url': '/auth',
			'dataType': 'json',
			'context': EThing,
			'converter': function(data){
				_authType = data.type;
				if(data.app)
					_app = new EThing.App(data.app);
				if(data.device)
					_device = new EThing.Device.Http(data.device);
				if(data.scope)
					_scope = data.scope;
			}
		}).done(function(){
			
			authenticatedCb_.forEach(function(cb){
				cb.call(EThing);
			});
			
			EThing.trigger('ething.authenticated');
		}).done(successFn).fail(errorFn);
		
	}
	
	
	/**
	 * Register a handler to be executed once the authentication is complete.
	 *
	 * @method EThing.authenticated
	 * @param {function()} callback it is executed on authentication success.
	 *
	 */
	var authenticatedCb_ = [];
	EThing.authenticated = function(callback){
		
		if(typeof callback == 'function'){
			authenticatedCb_.push(callback);
			
			if(EThing.auth.isAuthenticated()){
				callback.call(EThing);
			}
		}
	}
	
	
	
	global.EThing = EThing;
	
})(this);
